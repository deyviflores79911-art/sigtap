from django.utils import timezone

from rest_framework import (
    status,
    viewsets,
)

from usuarios.authentication import (
    ExpiringTokenAuthentication as TokenAuthentication,
)

from rest_framework.decorators import (
    action,
)

from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response


from usuarios.models import (
    Area,
    Usuario,
    UsuarioRol,
    obtener_codigos_rol_efectivos,
)

from auditoria.utils import (
    registrar_bitacora,
)


from .models import (
    EstadoMantenimiento,
    RequerimientoMantenimiento,
)

from .serializers import (
    EstadoMantenimientoSerializer,
    RequerimientoMantenimientoSerializer,
)


# ==========================================================
# VALORES POR DEFECTO DEL FORMULARIO SIMPLIFICADO
# ==========================================================
#
# El portal solicitante ya no pide área ni tipo: solo
# título, descripción, categoría (Soporte/Mantenimiento)
# y foto. Este helper completa el área que el modelo
# RequerimientoMantenimiento sigue requiriendo.
# ==========================================================

def _area_por_defecto():

    return (
        Area.objects
        .filter(activo=True)
        .order_by("id")
        .first()
    )


# ==========================================================
# ROLES ADMINISTRATIVOS
# ==========================================================

ROLES_ADMIN = {
    "ADMIN",
    "ADMINISTRADOR",
    "ADMINISTRADOR_SIGTA",
}


# ==========================================================
# OBTENER ROLES DEL USUARIO
# ==========================================================

def obtener_roles(usuario):

    # Incluye roles delegados temporalmente (Delegar aprobación
    # temporal) además de los roles propios.
    return obtener_codigos_rol_efectivos(usuario)


# ==========================================================
# ADMIN
# ==========================================================

def es_admin(usuario):

    if (
        not usuario
        or not usuario.is_authenticated
    ):
        return False


    if usuario.is_superuser:
        return True


    roles = {
        str(codigo).strip().upper()
        for codigo in obtener_roles(usuario)
    }


    return bool(
        roles.intersection(
            ROLES_ADMIN
        )
    )


# ==========================================================
# VERIFICAR ROL
# ==========================================================

def tiene_rol(
    usuario,
    *codigos
):

    if es_admin(usuario):
        return True


    roles_usuario = {
        str(codigo).strip().upper()
        for codigo in obtener_roles(usuario)
    }


    codigos_validos = {
        str(codigo).strip().upper()
        for codigo in codigos
    }


    return bool(
        roles_usuario.intersection(
            codigos_validos
        )
    )


# ==========================================================
# PERSONAL QUE OPERA MANTENIMIENTO
# ==========================================================

def puede_operar_mantenimiento(usuario):

    return (
        es_admin(usuario)
        or
        tiene_rol(
            usuario,
            "SERVICIOS_GENERALES",
            "AUXILIAR_SERVICIOS_GENERALES",
            "ENCARGADO_COMPRAS_ALMACEN",
        )
    )


# ==========================================================
# OBTENER ESTADO
# ==========================================================

def obtener_estado(codigo):

    try:

        return EstadoMantenimiento.objects.get(
            codigo=codigo,
            activo=True
        )

    except EstadoMantenimiento.DoesNotExist:

        return None


# ==========================================================
# VALIDAR ESTADO
# ==========================================================

def estado_permitido(
    requerimiento,
    codigos
):

    return (
        requerimiento.estado.codigo
        in codigos
    )


# ==========================================================
# RESPUESTA DEL REQUERIMIENTO
# ==========================================================

def respuesta_requerimiento(
    requerimiento,
    mensaje,
    request,
    codigo_http=status.HTTP_200_OK
):

    serializer = (
        RequerimientoMantenimientoSerializer(
            requerimiento,
            context={
                "request": request
            }
        )
    )


    return Response(
        {
            "ok": True,
            "mensaje": mensaje,
            "requerimiento": serializer.data,
        },
        status=codigo_http
    )


# ==========================================================
# ESTADOS
# ==========================================================

class EstadoMantenimientoViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        EstadoMantenimiento.objects
        .filter(
            activo=True
        )
        .order_by(
            "id"
        )
    )

    serializer_class = (
        EstadoMantenimientoSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


# ==========================================================
# REQUERIMIENTOS DE MANTENIMIENTO
# ==========================================================

class RequerimientoMantenimientoViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        RequerimientoMantenimientoSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]


    # ======================================================
    # CONSULTA
    # ======================================================

    def get_queryset(self):

        usuario = self.request.user


        queryset = (
            RequerimientoMantenimiento.objects
            .select_related(
                "solicitante",
                "area",
                "estado",
                "responsable_servicios_generales",
                "auxiliar_asignado",
            )
            .order_by(
                "-creado_en"
            )
        )


        # ADMIN y personal de mantenimiento ven todos
        if puede_operar_mantenimiento(
            usuario
        ):

            return queryset


        # Director: acceso de solo lectura a los requerimientos
        # ya finalizados (BPMN: "Director recibe los reportes").
        # No opera el flujo, por eso no entra en
        # puede_operar_mantenimiento.
        if tiene_rol(usuario, "DIRECTOR"):

            return queryset.filter(
                estado__codigo="FINALIZADO"
            )


        # Solicitante solamente ve sus requerimientos
        return queryset.filter(
            solicitante=usuario
        )


    # ======================================================
    # REGISTRAR REQUERIMIENTO
    # ======================================================

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_serializer(
            data=request.data
        )


        serializer.is_valid(
            raise_exception=True
        )


        if not serializer.validated_data.get("evidencia_archivo"):

            return Response(
                {"detalle": "Debe adjuntar una foto como evidencia."},
                status=status.HTTP_400_BAD_REQUEST
            )


        extra = {}

        if not serializer.validated_data.get("area"):

            area_defecto = _area_por_defecto()

            if area_defecto is None:
                return Response(
                    {"detalle": "No hay áreas registradas en el sistema."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            extra["area"] = area_defecto

        if not serializer.validated_data.get("ubicacion"):
            extra["ubicacion"] = "No especificado"

        if not serializer.validated_data.get("tipo"):
            extra["tipo"] = "CORRECTIVO"


        requerimiento = (
            serializer.save(**extra)
        )


        registrar_bitacora(
            request=request,
            accion=
                "REGISTRAR_REQUERIMIENTO_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"Se registró el requerimiento "
                f"{requerimiento.codigo}: "
                f"{requerimiento.titulo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            "Requerimiento de mantenimiento registrado correctamente.",
            request,
            status.HTTP_201_CREATED
        )


    # ======================================================
    # MODIFICAR REQUERIMIENTO
    # ======================================================

    def partial_update(
        self,
        request,
        *args,
        **kwargs
    ):

        requerimiento = (
            self.get_object()
        )

        usuario = request.user


        # --------------------------------------------------
        # SOLICITANTE
        # --------------------------------------------------

        if (
            requerimiento.solicitante_id
            ==
            usuario.id
        ):

            if (
                requerimiento.estado.codigo
                !=
                "RECIBIDO"
            ):

                return Response(
                    {
                        "detalle": (
                            "El requerimiento ya fue "
                            "derivado y no puede "
                            "modificarse libremente."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


        # --------------------------------------------------
        # PERSONAL AUTORIZADO
        # --------------------------------------------------

        elif not puede_operar_mantenimiento(
            usuario
        ):

            return Response(
                {
                    "detalle": (
                        "No tiene permiso para "
                        "modificar este requerimiento."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        respuesta = (
            super()
            .partial_update(
                request,
                *args,
                **kwargs
            )
        )


        registrar_bitacora(
            request=request,
            accion=
                "MODIFICAR_REQUERIMIENTO_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"Se modificó el requerimiento "
                f"{requerimiento.codigo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta


    # ======================================================
    # ANULAR REQUERIMIENTO
    # ======================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):

        requerimiento = (
            self.get_object()
        )

        usuario = request.user


        if (
            requerimiento.solicitante_id
            !=
            usuario.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el solicitante puede "
                        "anular este requerimiento."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if (
            requerimiento.estado.codigo
            !=
            "RECIBIDO"
        ):

            return Response(
                {
                    "detalle": (
                        "El requerimiento ya está "
                        "siendo atendido y no puede "
                        "anularse."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_anulado = obtener_estado(
            "ANULADO"
        )


        if not estado_anulado:

            return Response(
                {
                    "detalle":
                        "No existe el estado ANULADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.estado = (
            estado_anulado
        )

        requerimiento.activo = False


        requerimiento.save(
            update_fields=[
                "estado",
                "activo",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "ANULAR_REQUERIMIENTO_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"Se anuló el requerimiento "
                f"{requerimiento.codigo}."
            ),
            nivel=
                "WARNING",
        )


        return Response(
            {
                "ok": True,
                "mensaje":
                    "Requerimiento anulado correctamente."
            },
            status=status.HTTP_200_OK
        )


    # ======================================================
    # 1. DERIVAR A SU AUXILIAR
    # ======================================================
    #
    # BPMN:
    #
    # SERVICIOS GENERALES
    # "DERIVA A SU AUXILIAR"
    #
    # RECIBIDO -> DERIVADO
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="derivar-auxiliar"
    )
    def derivar_auxiliar(
        self,
        request,
        pk=None
    ):

        if not tiene_rol(
            request.user,
            "SERVICIOS_GENERALES"
        ):

            return Response(
                {
                    "detalle": (
                        "Solo Servicios Generales "
                        "puede derivar el requerimiento."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        requerimiento = (
            self.get_object()
        )


        if not estado_permitido(
            requerimiento,
            ["RECIBIDO"]
        ):

            return Response(
                {
                    "detalle": (
                        "Solo los requerimientos "
                        "RECIBIDOS pueden derivarse."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        auxiliar_id = (
            request.data.get(
                "auxiliar_id"
            )
        )


        if not auxiliar_id:

            return Response(
                {
                    "auxiliar_id":
                        "Debe seleccionar un auxiliar."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        try:

            auxiliar = (
                Usuario.objects.get(
                    id=auxiliar_id,
                    is_active=True
                )
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "auxiliar_id": (
                        "El auxiliar seleccionado "
                        "no existe o está inactivo."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        tiene_rol_auxiliar = (
            UsuarioRol.objects
            .filter(
                usuario=auxiliar,
                activo=True,
                rol__activo=True,
                rol__codigo=
                    "AUXILIAR_SERVICIOS_GENERALES"
            )
            .exists()
        )


        if not tiene_rol_auxiliar:

            return Response(
                {
                    "auxiliar_id": (
                        "El usuario seleccionado "
                        "no posee el rol "
                        "Auxiliar de Servicios Generales."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_derivado = obtener_estado(
            "DERIVADO"
        )


        if not estado_derivado:

            return Response(
                {
                    "detalle":
                        "No existe el estado DERIVADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        requerimiento.responsable_servicios_generales = (
            request.user
        )

        requerimiento.auxiliar_asignado = (
            auxiliar
        )

        requerimiento.estado = (
            estado_derivado
        )

        requerimiento.recibido_en = (
            requerimiento.recibido_en
            or ahora
        )

        requerimiento.derivado_en = (
            ahora
        )


        requerimiento.save(
            update_fields=[
                "responsable_servicios_generales",
                "auxiliar_asignado",
                "estado",
                "recibido_en",
                "derivado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "DERIVAR_AUXILIAR_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"El requerimiento "
                f"{requerimiento.codigo} "
                f"fue derivado a "
                f"{auxiliar.nombre_completo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            "Requerimiento derivado al auxiliar correctamente.",
            request
        )


    # ======================================================
    # 2. VERIFICAR SI REQUIERE REPOSICIÓN
    # ======================================================
    #
    # BPMN:
    #
    # "¿REQUIERE REPOSICIÓN DE ALMACÉN?"
    #
    # NO -> EN_MANTENIMIENTO
    # SI -> REVISION_ALMACEN
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="verificar-reposicion"
    )
    def verificar_reposicion(
        self,
        request,
        pk=None
    ):

        requerimiento = (
            self.get_object()
        )


        if not (
            es_admin(request.user)
            or
            (
                requerimiento.auxiliar_asignado_id
                ==
                request.user.id
            )
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el auxiliar asignado "
                        "puede realizar esta verificación."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if not estado_permitido(
            requerimiento,
            ["DERIVADO"]
        ):

            return Response(
                {
                    "detalle": (
                        "El requerimiento debe "
                        "encontrarse DERIVADO."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requiere = (
            request.data.get(
                "requiere_reposicion"
            )
        )


        if requiere not in [
            True,
            False
        ]:

            return Response(
                {
                    "requiere_reposicion": (
                        "Debe indicar True o False."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        requerimiento.requiere_reposicion = (
            requiere
        )


        # --------------------------------------------------
        # NO NECESITA PRODUCTO
        # --------------------------------------------------

        if requiere is False:

            estado_mantenimiento = obtener_estado(
                "EN_MANTENIMIENTO"
            )


            if not estado_mantenimiento:

                return Response(
                    {
                        "detalle": (
                            "No existe el estado "
                            "EN_MANTENIMIENTO."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


            requerimiento.estado = (
                estado_mantenimiento
            )

            requerimiento.inicio_mantenimiento_en = (
                ahora
            )


            requerimiento.save(
                update_fields=[
                    "requiere_reposicion",
                    "estado",
                    "inicio_mantenimiento_en",
                    "actualizado_en",
                ]
            )


            registrar_bitacora(
                request=request,
                accion=
                    "NO_REQUIERE_REPOSICION",
                modulo=
                    "Mantenimiento",
                detalle=(
                    f"El requerimiento "
                    f"{requerimiento.codigo} "
                    f"no requiere reposición."
                ),
                nivel=
                    "INFO",
            )


            return respuesta_requerimiento(
                requerimiento,
                (
                    "No requiere reposición. "
                    "Puede realizarse el mantenimiento."
                ),
                request
            )


        # --------------------------------------------------
        # SÍ NECESITA PRODUCTO
        # --------------------------------------------------

        producto = (
            str(
                request.data.get(
                    "producto_requerido",
                    ""
                )
            )
            .strip()
        )


        cantidad = (
            request.data.get(
                "cantidad_requerida"
            )
        )


        especificacion = (
            str(
                request.data.get(
                    "especificacion_producto",
                    ""
                )
            )
            .strip()
        )


        if not producto:

            return Response(
                {
                    "producto_requerido":
                        "Debe indicar el producto requerido."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        try:

            cantidad = int(
                cantidad
            )

        except (
            TypeError,
            ValueError
        ):

            return Response(
                {
                    "cantidad_requerida":
                        "Debe indicar una cantidad válida."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if cantidad <= 0:

            return Response(
                {
                    "cantidad_requerida": (
                        "La cantidad debe ser "
                        "mayor a cero."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_revision = obtener_estado(
            "REVISION_ALMACEN"
        )


        if not estado_revision:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "REVISION_ALMACEN."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.producto_requerido = (
            producto
        )

        requerimiento.cantidad_requerida = (
            cantidad
        )

        requerimiento.especificacion_producto = (
            especificacion
        )

        requerimiento.estado = (
            estado_revision
        )

        requerimiento.revision_almacen_en = (
            ahora
        )


        requerimiento.save(
            update_fields=[
                "requiere_reposicion",
                "producto_requerido",
                "cantidad_requerida",
                "especificacion_producto",
                "estado",
                "revision_almacen_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "SOLICITAR_REVISION_ALMACEN",
            modulo=
                "Mantenimiento",
            detalle=(
                f"El requerimiento "
                f"{requerimiento.codigo} "
                f"requiere {cantidad} unidad(es) "
                f"de {producto}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            "Se solicitó la revisión de existencia en almacén.",
            request
        )


    # ======================================================
    # 3. REPORTAR EXISTENCIA / NO EXISTENCIA
    # ======================================================
    #
    # BPMN:
    #
    # HAY PRODUCTO:
    # entrega producto -> mantenimiento
    #
    # NO HAY:
    # reporta no existencia -> Compra Caja Chica
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="reportar-existencia"
    )
    def reportar_existencia(
        self,
        request,
        pk=None
    ):

        if not tiene_rol(
            request.user,
            "ENCARGADO_COMPRAS_ALMACEN"
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el responsable de almacén "
                        "puede registrar la existencia "
                        "del producto."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        requerimiento = (
            self.get_object()
        )


        if not estado_permitido(
            requerimiento,
            ["REVISION_ALMACEN"]
        ):

            return Response(
                {
                    "detalle": (
                        "El requerimiento debe estar "
                        "en REVISIÓN DE ALMACÉN."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        disponible = (
            request.data.get(
                "producto_disponible"
            )
        )


        if disponible not in [
            True,
            False
        ]:

            return Response(
                {
                    "producto_disponible": (
                        "Debe indicar True o False."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        observacion = (
            str(
                request.data.get(
                    "observacion_almacen",
                    ""
                )
            )
            .strip()
        )


        requerimiento.producto_disponible_almacen = (
            disponible
        )

        requerimiento.observacion_almacen = (
            observacion
        )


        # --------------------------------------------------
        # EXISTE PRODUCTO
        # --------------------------------------------------

        if disponible is True:

            estado_mantenimiento = obtener_estado(
                "EN_MANTENIMIENTO"
            )


            if not estado_mantenimiento:

                return Response(
                    {
                        "detalle": (
                            "No existe el estado "
                            "EN_MANTENIMIENTO."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


            requerimiento.producto_entregado = (
                True
            )

            requerimiento.estado = (
                estado_mantenimiento
            )

            requerimiento.inicio_mantenimiento_en = (
                timezone.now()
            )


            requerimiento.save(
                update_fields=[
                    "producto_disponible_almacen",
                    "producto_entregado",
                    "observacion_almacen",
                    "estado",
                    "inicio_mantenimiento_en",
                    "actualizado_en",
                ]
            )


            registrar_bitacora(
                request=request,
                accion=
                    "ENTREGAR_PRODUCTO_ALMACEN",
                modulo=
                    "Mantenimiento",
                detalle=(
                    f"Almacén entregó el producto "
                    f"para {requerimiento.codigo}."
                ),
                nivel=
                    "INFO",
            )


            return respuesta_requerimiento(
                requerimiento,
                (
                    "Producto disponible y entregado. "
                    "Puede realizarse el mantenimiento."
                ),
                request
            )


        # --------------------------------------------------
        # NO EXISTE PRODUCTO
        # --------------------------------------------------

        estado_espera = obtener_estado(
            "EN_ESPERA_COMPRA"
        )


        if not estado_espera:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_ESPERA_COMPRA."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.derivado_compra = (
            True
        )

        requerimiento.estado = (
            estado_espera
        )


        # Se crea el expediente real de Compra Caja Chica en vez
        # de dejar solo la bandera derivado_compra encendida. El
        # responsable (auxiliar o, en su defecto, Servicios
        # Generales) queda como solicitante del expediente para
        # poder completar Informe/POA/Pedido/Proforma.
        from compras.models import SolicitudCompra

        responsable_compra = (
            requerimiento.auxiliar_asignado
            or requerimiento.responsable_servicios_generales
            or requerimiento.solicitante
        )

        solicitud_compra = SolicitudCompra.objects.create(
            codigo=SolicitudCompra.generar_codigo(),
            titulo=(
                requerimiento.producto_requerido
                or f"Reposición para mantenimiento {requerimiento.codigo}"
            ),
            descripcion=(
                requerimiento.especificacion_producto
                or requerimiento.producto_requerido
                or ""
            ),
            solicitante=responsable_compra,
            area=requerimiento.area,
            tipo="COMPONENTE",
            cantidad=requerimiento.cantidad_requerida or 1,
            especificaciones=requerimiento.especificacion_producto,
            justificacion=(
                "Reposición de almacén requerida para atender "
                f"el mantenimiento {requerimiento.codigo}."
            ),
            estado="CREADO_PENDIENTE_DAF",
            origen_modulo="MANTENIMIENTO",
            requerimiento_mantenimiento=requerimiento,
        )

        requerimiento.codigo_compra_vinculada = solicitud_compra.codigo


        requerimiento.save(
            update_fields=[
                "producto_disponible_almacen",
                "observacion_almacen",
                "derivado_compra",
                "codigo_compra_vinculada",
                "estado",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "REPORTAR_NO_EXISTENCIA_PRODUCTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"No existe el producto requerido "
                f"para {requerimiento.codigo}. "
                f"Se generó el expediente {solicitud_compra.codigo} "
                f"y se derivó a Compra Caja Chica."
            ),
            nivel=
                "WARNING",
        )


        return respuesta_requerimiento(
            requerimiento,
            (
                "No existe el producto en almacén. "
                f"Se generó el expediente {solicitud_compra.codigo} "
                "en Compra Caja Chica."
            ),
            request
        )


    # ======================================================
    # 4. REGISTRAR COMPRA COMPLETADA
    # ======================================================
    #
    # Cuando el subproceso de compra termina,
    # mantenimiento puede continuar.
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="registrar-compra"
    )
    def registrar_compra(
        self,
        request,
        pk=None
    ):

        if not (
            es_admin(request.user)
            or
            tiene_rol(
                request.user,
                "ENCARGADO_COMPRAS_ALMACEN",
                "SERVICIOS_GENERALES",
            )
        ):

            return Response(
                {
                    "detalle": (
                        "No tiene permiso para "
                        "registrar la recepción "
                        "de la compra."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        requerimiento = (
            self.get_object()
        )


        if not estado_permitido(
            requerimiento,
            ["EN_ESPERA_COMPRA"]
        ):

            return Response(
                {
                    "detalle": (
                        "El requerimiento no está "
                        "esperando una compra."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        # La compra ya no se confirma con un código escrito a
        # mano: se busca el expediente real vinculado (creado
        # automáticamente en reportar-existencia) y se exige
        # que Compras ya lo haya cerrado y archivado.
        solicitud_compra = (
            requerimiento.compras_generadas
            .filter(activo__in=[True, False])
            .order_by("-creado_en")
            .first()
        )

        if not solicitud_compra:

            return Response(
                {
                    "detalle": (
                        "Este requerimiento no tiene una "
                        "solicitud de compra vinculada."
                    )
                },
                status=
                    status.HTTP_409_CONFLICT
            )

        if solicitud_compra.estado != "CERRADO_ARCHIVADO":

            return Response(
                {
                    "detalle": (
                        "La compra vinculada "
                        f"({solicitud_compra.codigo}) todavía "
                        "no fue cerrada y archivada por Tesorería."
                    )
                },
                status=
                    status.HTTP_409_CONFLICT
            )


        estado_mantenimiento = obtener_estado(
            "EN_MANTENIMIENTO"
        )


        if not estado_mantenimiento:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_MANTENIMIENTO."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.codigo_compra_vinculada = (
            solicitud_compra.codigo
        )

        requerimiento.compra_completada = (
            True
        )

        requerimiento.producto_entregado = (
            True
        )

        requerimiento.estado = (
            estado_mantenimiento
        )

        requerimiento.inicio_mantenimiento_en = (
            timezone.now()
        )


        requerimiento.save(
            update_fields=[
                "codigo_compra_vinculada",
                "compra_completada",
                "producto_entregado",
                "estado",
                "inicio_mantenimiento_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "REGISTRAR_COMPRA_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"La compra {solicitud_compra.codigo} "
                f"fue confirmada para el requerimiento "
                f"{requerimiento.codigo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            (
                "Compra recibida. "
                "El mantenimiento puede continuar."
            ),
            request
        )


    # ======================================================
    # 5. REALIZAR EL MANTENIMIENTO
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="realizar-mantenimiento"
    )
    def realizar_mantenimiento(
        self,
        request,
        pk=None
    ):

        requerimiento = (
            self.get_object()
        )


        if not (
            es_admin(request.user)
            or
            (
                requerimiento.auxiliar_asignado_id
                ==
                request.user.id
            )
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el auxiliar asignado "
                        "puede registrar el mantenimiento."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if not estado_permitido(
            requerimiento,
            ["EN_MANTENIMIENTO"]
        ):

            return Response(
                {
                    "detalle": (
                        "El requerimiento no se "
                        "encuentra EN MANTENIMIENTO."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        trabajo = (
            str(
                request.data.get(
                    "trabajo_realizado",
                    ""
                )
            )
            .strip()
        )


        observaciones = (
            str(
                request.data.get(
                    "observaciones_trabajo",
                    ""
                )
            )
            .strip()
        )


        if not trabajo:

            return Response(
                {
                    "trabajo_realizado":
                        "Debe registrar el trabajo realizado."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.trabajo_realizado = (
            trabajo
        )

        requerimiento.observaciones_trabajo = (
            observaciones
        )


        requerimiento.save(
            update_fields=[
                "trabajo_realizado",
                "observaciones_trabajo",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "REALIZAR_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"Se registró el trabajo realizado "
                f"en {requerimiento.codigo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            "Trabajo de mantenimiento registrado correctamente.",
            request
        )


    # ======================================================
    # 6. REALIZAR INFORME Y FOTOGRAFÍA
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="registrar-informe"
    )
    def registrar_informe(
        self,
        request,
        pk=None
    ):

        requerimiento = (
            self.get_object()
        )


        if not (
            es_admin(request.user)
            or
            (
                requerimiento.auxiliar_asignado_id
                ==
                request.user.id
            )
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el auxiliar asignado "
                        "puede registrar el informe."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if not estado_permitido(
            requerimiento,
            ["EN_MANTENIMIENTO"]
        ):

            return Response(
                {
                    "detalle": (
                        "El requerimiento debe estar "
                        "EN MANTENIMIENTO."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not requerimiento.trabajo_realizado:

            return Response(
                {
                    "detalle": (
                        "Primero debe registrar "
                        "el trabajo realizado."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        informe = (
            str(
                request.data.get(
                    "informe_trabajo",
                    ""
                )
            )
            .strip()
        )


        if not informe:

            return Response(
                {
                    "informe_trabajo":
                        "Debe registrar el informe del trabajo."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        fotografia = (
            request.FILES.get(
                "fotografia_trabajo"
            )
        )


        estado_informe = obtener_estado(
            "INFORME_REGISTRADO"
        )


        if not estado_informe:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "INFORME_REGISTRADO."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.informe_trabajo = (
            informe
        )


        if fotografia:

            requerimiento.fotografia_trabajo = (
                fotografia
            )


        requerimiento.estado = (
            estado_informe
        )

        requerimiento.informe_registrado_en = (
            timezone.now()
        )


        requerimiento.save()


        registrar_bitacora(
            request=request,
            accion=
                "REGISTRAR_INFORME_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"Se registró el informe "
                f"del requerimiento "
                f"{requerimiento.codigo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            "Informe del mantenimiento registrado correctamente.",
            request
        )


    # ======================================================
    # 7. FINALIZAR
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="finalizar"
    )
    def finalizar(
        self,
        request,
        pk=None
    ):

        if not (
            es_admin(request.user)
            or
            tiene_rol(
                request.user,
                "SERVICIOS_GENERALES"
            )
        ):

            return Response(
                {
                    "detalle": (
                        "Solo Servicios Generales "
                        "puede finalizar el requerimiento."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        requerimiento = (
            self.get_object()
        )


        if not estado_permitido(
            requerimiento,
            ["INFORME_REGISTRADO"]
        ):

            return Response(
                {
                    "detalle": (
                        "Primero debe registrarse "
                        "el informe del trabajo."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_finalizado = obtener_estado(
            "FINALIZADO"
        )


        if not estado_finalizado:

            return Response(
                {
                    "detalle":
                        "No existe el estado FINALIZADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        requerimiento.estado = (
            estado_finalizado
        )

        requerimiento.finalizado_en = (
            timezone.now()
        )


        requerimiento.save(
            update_fields=[
                "estado",
                "finalizado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion=
                "FINALIZAR_MANTENIMIENTO",
            modulo=
                "Mantenimiento",
            detalle=(
                f"Se finalizó el requerimiento "
                f"{requerimiento.codigo}."
            ),
            nivel=
                "INFO",
        )


        return respuesta_requerimiento(
            requerimiento,
            "Requerimiento de mantenimiento finalizado.",
            request
        )


    # ======================================================
    # 7. REPORTE MENSUAL
    # ======================================================
    #
    # BPMN: "A fin de mes se da a conocer todos los
    # mantenimientos" -> "Director recibe los reportes".
    # Consolidado real por periodo (no un filtro de texto
    # en el frontend).
    #
    # ======================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="reporte-mensual"
    )
    def reporte_mensual(
        self,
        request
    ):

        if not (
            es_admin(request.user)
            or
            tiene_rol(
                request.user,
                "SERVICIOS_GENERALES",
                "DIRECTOR",
            )
        ):

            return Response(
                {
                    "detalle": (
                        "No tiene permiso para consultar "
                        "el reporte mensual de mantenimiento."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        ahora = timezone.now()

        try:
            anio = int(request.query_params.get("anio", ahora.year))
            mes = int(request.query_params.get("mes", ahora.month))
        except ValueError:
            return Response(
                {"detalle": "Año y mes deben ser numéricos."},
                status=status.HTTP_400_BAD_REQUEST
            )


        queryset = (
            RequerimientoMantenimiento.objects
            .filter(
                estado__codigo="FINALIZADO",
                finalizado_en__year=anio,
                finalizado_en__month=mes,
            )
            .select_related(
                "solicitante",
                "area",
                "responsable_servicios_generales",
                "auxiliar_asignado",
            )
            .order_by("-finalizado_en")
        )

        serializer = RequerimientoMantenimientoSerializer(
            queryset,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "anio": anio,
                "mes": mes,
                "total_finalizados": queryset.count(),
                "requerimientos": serializer.data,
            }
        )