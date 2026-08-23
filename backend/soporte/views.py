from datetime import timedelta

from django.utils import timezone

from rest_framework import (
    status,
    viewsets,
)

from rest_framework.authentication import (
    TokenAuthentication,
)

from rest_framework.decorators import (
    action,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response


from usuarios.models import (
    Usuario,
    UsuarioRol,
    RolPermiso,
)

from auditoria.utils import (
    registrar_bitacora,
)

from .models import (
    CategoriaTicket,
    EstadoTicket,
    Ticket,
)

from .serializers import (
    CategoriaTicketSerializer,
    EstadoTicketSerializer,
    TicketSerializer,
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
# SLA POR PRIORIDAD
# ==========================================================
#
# Por ahora estos valores forman parte de la lógica del
# sistema. Más adelante los conectaremos con Preferencias.
#
# ==========================================================

SLA_POR_PRIORIDAD = {
    "CRITICA": 4,
    "ALTA": 8,
    "MEDIA": 24,
    "BAJA": 48,
}


# ==========================================================
# ROLES DEL USUARIO
# ==========================================================

def obtener_roles(usuario):

    if (
        not usuario
        or
        not usuario.is_authenticated
    ):
        return []


    return list(
        UsuarioRol.objects
        .filter(
            usuario=usuario,
            activo=True,
            rol__activo=True
        )
        .values_list(
            "rol__codigo",
            flat=True
        )
    )


# ==========================================================
# VERIFICAR ADMIN
# ==========================================================

def es_admin(usuario):

    if (
        not usuario
        or
        not usuario.is_authenticated
    ):
        return False


    if usuario.is_superuser:
        return True


    roles = {
        str(codigo)
        .strip()
        .upper()

        for codigo in obtener_roles(
            usuario
        )
    }


    return bool(
        roles.intersection(
            ROLES_ADMIN
        )
    )


# ==========================================================
# VERIFICAR PERMISO
# ==========================================================

def tiene_permiso(
    usuario,
    codigo_permiso
):

    if es_admin(usuario):
        return True


    return (
        RolPermiso.objects
        .filter(
            rol__usuarios_asignados__usuario=usuario,
            rol__usuarios_asignados__activo=True,

            rol__activo=True,

            permiso__codigo=codigo_permiso,
            permiso__activo=True,

            activo=True,
        )
        .exists()
    )


# ==========================================================
# OPERADOR DE SOPORTE
# ==========================================================

def puede_operar_soporte(
    usuario
):

    if es_admin(usuario):
        return True


    if tiene_permiso(
        usuario,
        "VER_SOPORTE_TECNICO"
    ):
        return True


    # Compatibilidad temporal con roles anteriores.
    roles = obtener_roles(
        usuario
    )


    return (
        "AGENTE" in roles
        or
        "SUPERVISOR_AREA" in roles
    )


# ==========================================================
# RESPUESTA SIN PERMISO
# ==========================================================

def respuesta_sin_permiso(
    codigo_permiso
):

    return Response(
        {
            "ok": False,

            "detalle": (
                "No tiene permiso para realizar "
                "esta actividad."
            ),

            "permiso_requerido":
                codigo_permiso,
        },
        status=status.HTTP_403_FORBIDDEN
    )


# ==========================================================
# BUSCAR ESTADO
# ==========================================================

def obtener_estado(
    codigo
):

    try:

        return EstadoTicket.objects.get(
            codigo=codigo,
            activo=True
        )

    except EstadoTicket.DoesNotExist:

        return None


# ==========================================================
# VALIDAR ESTADO DEL TICKET
# ==========================================================

def validar_estado_ticket(
    ticket,
    estados_permitidos
):

    return (
        ticket.estado.codigo
        in estados_permitidos
    )


# ==========================================================
# RESPUESTA DEL TICKET
# ==========================================================

def respuesta_ticket(
    ticket,
    mensaje,
    codigo_http=status.HTTP_200_OK
):

    serializer = TicketSerializer(
        ticket
    )


    return Response(
        {
            "ok": True,

            "mensaje":
                mensaje,

            "ticket":
                serializer.data,
        },
        status=codigo_http
    )


# ==========================================================
# CALCULAR CUMPLIMIENTO SLA
# ==========================================================

def calcular_sla_cumplido(
    ticket,
    fecha_fin=None
):

    if not ticket.sla_fecha_limite:
        return None


    if fecha_fin is None:

        fecha_fin = timezone.now()


    return (
        fecha_fin
        <=
        ticket.sla_fecha_limite
    )


# ==========================================================
# CATEGORÍAS
# ==========================================================

class CategoriaTicketViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        CategoriaTicket.objects
        .filter(
            activo=True
        )
        .order_by(
            "nombre"
        )
    )

    serializer_class = (
        CategoriaTicketSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


# ==========================================================
# ESTADOS
# ==========================================================

class EstadoTicketViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        EstadoTicket.objects
        .filter(
            activo=True
        )
        .order_by(
            "id"
        )
    )

    serializer_class = (
        EstadoTicketSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


# ==========================================================
# TICKETS DE SOPORTE
# ==========================================================

class TicketViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        TicketSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


    # ======================================================
    # CONSULTA
    # ======================================================

    def get_queryset(self):

        usuario = (
            self.request.user
        )


        queryset = (
            Ticket.objects
            .select_related(
                "solicitante",
                "tecnico_asignado",
                "area",
                "categoria",
                "estado",
            )
            .prefetch_related(
                "especialistas_apoyo"
            )
            .order_by(
                "-creado_en"
            )
        )


        if es_admin(usuario):
            return queryset


        if puede_operar_soporte(
            usuario
        ):
            return queryset


        return queryset.filter(
            solicitante=usuario
        )


    # ======================================================
    # CREAR / REGISTRAR TICKET
    # ======================================================

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        if not (
            es_admin(
                request.user
            )
            or
            tiene_permiso(
                request.user,
                "REGISTRAR_TICKET"
            )
        ):

            return respuesta_sin_permiso(
                "REGISTRAR_TICKET"
            )


        serializer = self.get_serializer(
            data=request.data
        )


        serializer.is_valid(
            raise_exception=True
        )


        ticket = serializer.save()


        registrar_bitacora(
            request=request,
            accion="REGISTRAR_TICKET",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registró el ticket "
                f"{ticket.codigo}: "
                f"{ticket.titulo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Ticket registrado correctamente.",
            status.HTTP_201_CREATED
        )


    # ======================================================
    # MODIFICAR TICKET
    # ======================================================

    def partial_update(
        self,
        request,
        *args,
        **kwargs
    ):

        ticket = self.get_object()

        usuario = request.user


        # --------------------------------------------------
        # SOLICITANTE
        # --------------------------------------------------

        if (
            ticket.solicitante_id
            ==
            usuario.id
        ):

            if (
                ticket.estado.codigo
                not in [
                    "BORRADOR",
                    "NUEVO",
                ]
            ):

                return Response(
                    {
                        "detalle": (
                            "El ticket ya está siendo "
                            "atendido y no puede modificarse."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


        # --------------------------------------------------
        # PERSONAL DE SOPORTE
        # --------------------------------------------------

        elif not puede_operar_soporte(
            usuario
        ):

            return Response(
                {
                    "detalle": (
                        "No tiene permiso para "
                        "modificar este ticket."
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
            accion="MODIFICAR_TICKET_SOPORTE",
            modulo="Soporte Técnico",
            detalle=(
                f"Se modificó el ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta


    # ======================================================
    # ANULAR TICKET
    # ======================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):

        ticket = self.get_object()

        usuario = request.user


        if (
            ticket.solicitante_id
            !=
            usuario.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el solicitante puede "
                        "anular este ticket."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if (
            ticket.estado.codigo
            not in [
                "BORRADOR",
                "NUEVO",
            ]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket ya está en atención "
                        "y no puede anularse."
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


        ticket.estado = estado_anulado

        ticket.activo = False


        ticket.save(
            update_fields=[
                "estado",
                "activo",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="ANULAR_TICKET_SOPORTE",
            modulo="Soporte Técnico",
            detalle=(
                f"Se anuló el ticket "
                f"{ticket.codigo}."
            ),
            nivel="WARNING",
        )


        return Response(
            {
                "ok": True,

                "mensaje":
                    "Ticket anulado correctamente."
            },
            status=status.HTTP_200_OK
        )


    # ======================================================
    # 1. RECIBIR TICKET Y VALIDAR TICKET
    # ======================================================
    #
    # Actor: Jefe de UTIC
    #
    # NUEVO -> EN_ANALISIS
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="validar-ticket"
    )
    def validar_ticket(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "RECIBIR_VALIDAR_TICKET"
        ):

            return respuesta_sin_permiso(
                "RECIBIR_VALIDAR_TICKET"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["NUEVO"]
        ):

            return Response(
                {
                    "detalle": (
                        "Solo los tickets NUEVOS "
                        "pueden recibirse y validarse."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_destino = obtener_estado(
            "EN_ANALISIS"
        )


        if not estado_destino:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_ANALISIS."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.estado = estado_destino

        ticket.validado_en = timezone.now()


        ticket.save(
            update_fields=[
                "estado",
                "validado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="RECIBIR_VALIDAR_TICKET",
            modulo="Soporte Técnico",
            detalle=(
                f"Se recibió y validó el ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Ticket recibido y validado correctamente."
        )


    # ======================================================
    # 2. CLASIFICAR PRIORIDAD Y ASIGNAR SLA
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="clasificar-prioridad"
    )
    def clasificar_prioridad(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "CLASIFICAR_PRIORIDAD_SLA"
        ):

            return respuesta_sin_permiso(
                "CLASIFICAR_PRIORIDAD_SLA"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_ANALISIS"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_ANALISIS."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        prioridad = (
            str(
                request.data.get(
                    "prioridad",
                    ""
                )
            )
            .strip()
            .upper()
        )


        if prioridad not in SLA_POR_PRIORIDAD:

            return Response(
                {
                    "prioridad": (
                        "Seleccione BAJA, MEDIA, "
                        "ALTA o CRITICA."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        criterio_tecnico = (
            str(
                request.data.get(
                    "criterio_tecnico",
                    ""
                )
            )
            .strip()
        )


        if not criterio_tecnico:

            return Response(
                {
                    "criterio_tecnico": (
                        "Debe registrar el criterio "
                        "técnico de clasificación."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()

        horas_sla = (
            SLA_POR_PRIORIDAD[
                prioridad
            ]
        )


        fecha_limite = (
            ahora
            +
            timedelta(
                hours=horas_sla
            )
        )


        ticket.prioridad = prioridad

        ticket.criterio_tecnico = (
            criterio_tecnico
        )

        ticket.sla_horas = (
            horas_sla
        )

        ticket.sla_fecha_limite = (
            fecha_limite
        )

        ticket.sla_cumplido = None

        ticket.clasificado_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "prioridad",
                "criterio_tecnico",
                "sla_horas",
                "sla_fecha_limite",
                "sla_cumplido",
                "clasificado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="CLASIFICAR_PRIORIDAD_SLA",
            modulo="Soporte Técnico",
            detalle=(
                f"Se clasificó el ticket "
                f"{ticket.codigo} como "
                f"{prioridad}. "
                f"SLA asignado: "
                f"{horas_sla} horas."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            (
                f"Prioridad {prioridad} registrada. "
                f"SLA asignado: {horas_sla} horas."
            )
        )


    # ======================================================
    # 3. DESIGNAR REVISIÓN AL ESPECIALISTA
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="designar-revision"
    )
    def designar_revision(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "DESIGNAR_REVISION"
        ):

            return respuesta_sin_permiso(
                "DESIGNAR_REVISION"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_ANALISIS"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_ANALISIS."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not ticket.prioridad:

            return Response(
                {
                    "detalle": (
                        "Primero debe clasificar "
                        "la prioridad y asignar SLA."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        tecnico_id = request.data.get(
            "tecnico_id"
        )


        if not tecnico_id:

            return Response(
                {
                    "tecnico_id": (
                        "Debe seleccionar al "
                        "especialista responsable."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        try:

            tecnico = Usuario.objects.get(
                pk=tecnico_id,
                is_active=True
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "tecnico_id": (
                        "El especialista seleccionado "
                        "no existe o está inactivo."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        tiene_rol_especialista = (
            UsuarioRol.objects
            .filter(
                usuario=tecnico,
                activo=True,
                rol__activo=True,
                rol__codigo__in=[
                    "ESPECIALISTA",
                    "AGENTE",
                ]
            )
            .exists()
        )


        if not tiene_rol_especialista:

            return Response(
                {
                    "tecnico_id": (
                        "El usuario seleccionado no "
                        "posee el rol Especialista."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_asignado = obtener_estado(
            "ASIGNADO"
        )


        if not estado_asignado:

            return Response(
                {
                    "detalle":
                        "No existe el estado ASIGNADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        ticket.tecnico_asignado = tecnico

        ticket.estado = estado_asignado

        ticket.asignado_en = ahora


        ticket.save(
            update_fields=[
                "tecnico_asignado",
                "estado",
                "asignado_en",
                "actualizado_en",
            ]
        )


        apoyo_ids = request.data.get(
            "especialistas_apoyo",
            []
        )


        if isinstance(
            apoyo_ids,
            list
        ):

            especialistas = (
                Usuario.objects
                .filter(
                    id__in=apoyo_ids,
                    is_active=True,
                    roles_asignados__activo=True,
                    roles_asignados__rol__codigo__in=[
                        "ESPECIALISTA",
                        "AGENTE",
                    ]
                )
                .distinct()
            )


            ticket.especialistas_apoyo.set(
                especialistas
            )


        registrar_bitacora(
            request=request,
            accion="DESIGNAR_REVISION",
            modulo="Soporte Técnico",
            detalle=(
                f"Se designó a "
                f"{tecnico.nombre_completo} "
                f"como responsable del ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Especialista designado correctamente."
        )


    # ======================================================
    # 4. REALIZAR INSPECCIÓN TÉCNICA Y DIAGNÓSTICO
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="registrar-diagnostico"
    )
    def registrar_diagnostico(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "REALIZAR_INSPECCION_DIAGNOSTICO"
        ):

            return respuesta_sin_permiso(
                "REALIZAR_INSPECCION_DIAGNOSTICO"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["ASIGNADO"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "ASIGNADO."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not (
            es_admin(
                request.user
            )
            or
            ticket.tecnico_asignado_id
            ==
            request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el especialista asignado "
                        "puede registrar el diagnóstico."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        diagnostico = (
            str(
                request.data.get(
                    "diagnostico",
                    ""
                )
            )
            .strip()
        )


        plan_solucion = (
            str(
                request.data.get(
                    "plan_solucion",
                    ""
                )
            )
            .strip()
        )


        if not diagnostico:

            return Response(
                {
                    "diagnostico":
                        "Debe registrar el diagnóstico."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not plan_solucion:

            return Response(
                {
                    "plan_solucion":
                        "Debe registrar el plan de solución."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_ejecucion = obtener_estado(
            "EN_EJECUCION"
        )


        if not estado_ejecucion:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_EJECUCION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        ticket.diagnostico = diagnostico

        ticket.plan_solucion = (
            plan_solucion
        )

        ticket.estado = (
            estado_ejecucion
        )

        ticket.inicio_atencion_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "diagnostico",
                "plan_solucion",
                "estado",
                "inicio_atencion_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="REALIZAR_INSPECCION_DIAGNOSTICO",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registró la inspección y "
                f"diagnóstico del ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Inspección y diagnóstico registrados correctamente."
        )


    # ======================================================
    # 5. REALIZAR REPARACIÓN O INSTALACIÓN Y REGISTRAR
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="registrar-intervencion"
    )
    def registrar_intervencion(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "REALIZAR_REPARACION_INSTALACION"
        ):

            return respuesta_sin_permiso(
                "REALIZAR_REPARACION_INSTALACION"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_EJECUCION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_EJECUCION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not (
            es_admin(
                request.user
            )
            or
            ticket.tecnico_asignado_id
            ==
            request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el especialista asignado "
                        "puede registrar la intervención."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        solucion = (
            str(
                request.data.get(
                    "solucion",
                    ""
                )
            )
            .strip()
        )


        if not solucion:

            return Response(
                {
                    "solucion": (
                        "Debe registrar la reparación, "
                        "instalación o intervención realizada."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.solucion = solucion


        ticket.save(
            update_fields=[
                "solucion",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="REALIZAR_REPARACION_INSTALACION",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registró la intervención "
                f"del ticket {ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Intervención técnica registrada correctamente."
        )


    # ======================================================
    # 6. REALIZAR PRUEBAS TÉCNICAS
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="pruebas-tecnicas"
    )
    def pruebas_tecnicas(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "REALIZAR_PRUEBAS_TECNICAS"
        ):

            return respuesta_sin_permiso(
                "REALIZAR_PRUEBAS_TECNICAS"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_EJECUCION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_EJECUCION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not ticket.solucion:

            return Response(
                {
                    "detalle": (
                        "Primero debe registrar "
                        "la intervención técnica."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        resultado = (
            str(
                request.data.get(
                    "resultado_pruebas",
                    ""
                )
            )
            .strip()
        )


        if not resultado:

            return Response(
                {
                    "resultado_pruebas": (
                        "Debe registrar el resultado "
                        "de las pruebas técnicas."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_verificacion = obtener_estado(
            "EN_VERIFICACION"
        )


        if not estado_verificacion:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_VERIFICACION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        ticket.resultado_pruebas = (
            resultado
        )

        ticket.estado = (
            estado_verificacion
        )

        ticket.pruebas_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "resultado_pruebas",
                "estado",
                "pruebas_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="REALIZAR_PRUEBAS_TECNICAS",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registraron las pruebas técnicas "
                f"del ticket {ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Pruebas técnicas registradas correctamente."
        )


    # ======================================================
    # 7. VERIFICAR FUNCIONAMIENTO
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="verificar-funcionamiento"
    )
    def verificar_funcionamiento(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "VERIFICAR_FUNCIONAMIENTO"
        ):

            return respuesta_sin_permiso(
                "VERIFICAR_FUNCIONAMIENTO"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_VERIFICACION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_VERIFICACION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        funciona = request.data.get(
            "funciona_correctamente"
        )


        if funciona not in [
            True,
            False,
        ]:

            return Response(
                {
                    "funciona_correctamente": (
                        "Debe indicar True o False."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        # --------------------------------------------------
        # NO CONFORME TÉCNICAMENTE
        # --------------------------------------------------

        if funciona is False:

            estado_ejecucion = obtener_estado(
                "EN_EJECUCION"
            )


            if not estado_ejecucion:

                return Response(
                    {
                        "detalle": (
                            "No existe el estado "
                            "EN_EJECUCION."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


            ticket.rework_count += 1

            ticket.estado = (
                estado_ejecucion
            )

            ticket.verificado_en = (
                ahora
            )


            ticket.save(
                update_fields=[
                    "rework_count",
                    "estado",
                    "verificado_en",
                    "actualizado_en",
                ]
            )


            registrar_bitacora(
                request=request,
                accion="VERIFICACION_NO_CONFORME",
                modulo="Soporte Técnico",
                detalle=(
                    f"El ticket {ticket.codigo} "
                    f"requiere nueva intervención."
                ),
                nivel="WARNING",
            )


            return respuesta_ticket(
                ticket,
                (
                    "La verificación no fue conforme. "
                    "El ticket volvió a ejecución."
                )
            )


        # --------------------------------------------------
        # FUNCIONAMIENTO CORRECTO
        # --------------------------------------------------

        estado_conformidad = obtener_estado(
            "PENDIENTE_CONFORMIDAD"
        )


        if not estado_conformidad:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "PENDIENTE_CONFORMIDAD."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.estado = (
            estado_conformidad
        )

        ticket.verificado_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "estado",
                "verificado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="VERIFICAR_FUNCIONAMIENTO",
            modulo="Soporte Técnico",
            detalle=(
                f"Se verificó el funcionamiento "
                f"del ticket {ticket.codigo}. "
                f"Pendiente de conformidad."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            (
                "Funcionamiento verificado. "
                "El ticket quedó pendiente "
                "de conformidad del solicitante."
            )
        )


    # ======================================================
    # 8. INFORMAR CONFORMIDAD
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="informar-conformidad"
    )
    def informar_conformidad(
        self,
        request,
        pk=None
    ):

        ticket = self.get_object()


        if (
            ticket.solicitante_id
            !=
            request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el solicitante del ticket "
                        "puede informar la conformidad."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if not tiene_permiso(
            request.user,
            "INFORMAR_CONFORMIDAD"
        ):

            return respuesta_sin_permiso(
                "INFORMAR_CONFORMIDAD"
            )


        if not validar_estado_ticket(
            ticket,
            ["PENDIENTE_CONFORMIDAD"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket todavía no está "
                        "pendiente de conformidad."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        conformidad = request.data.get(
            "conformidad"
        )


        observaciones = (
            str(
                request.data.get(
                    "observaciones",
                    ""
                )
            )
            .strip()
        )


        if conformidad not in [
            True,
            False,
        ]:

            return Response(
                {
                    "conformidad": (
                        "Debe indicar True o False."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        # --------------------------------------------------
        # NO CONFORMIDAD
        # --------------------------------------------------

        if conformidad is False:

            estado_ejecucion = obtener_estado(
                "EN_EJECUCION"
            )


            if not estado_ejecucion:

                return Response(
                    {
                        "detalle":
                            "No existe EN_EJECUCION."
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


            ticket.conformidad_usuario = (
                False
            )

            ticket.observaciones_usuario = (
                observaciones
            )

            ticket.conformidad_en = (
                ahora
            )

            ticket.rework_count += 1

            ticket.estado = (
                estado_ejecucion
            )


            ticket.save(
                update_fields=[
                    "conformidad_usuario",
                    "observaciones_usuario",
                    "conformidad_en",
                    "rework_count",
                    "estado",
                    "actualizado_en",
                ]
            )


            registrar_bitacora(
                request=request,
                accion="INFORMAR_NO_CONFORMIDAD",
                modulo="Soporte Técnico",
                detalle=(
                    f"El solicitante informó "
                    f"no conformidad en "
                    f"{ticket.codigo}."
                ),
                nivel="WARNING",
            )


            return respuesta_ticket(
                ticket,
                (
                    "No conformidad registrada. "
                    "El ticket regresó a ejecución."
                )
            )


        # --------------------------------------------------
        # CONFORMIDAD
        # --------------------------------------------------

        estado_cerrado = obtener_estado(
            "CERRADO"
        )


        if not estado_cerrado:

            return Response(
                {
                    "detalle":
                        "No existe el estado CERRADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.conformidad_usuario = (
            True
        )

        ticket.observaciones_usuario = (
            observaciones
        )

        ticket.conformidad_en = (
            ahora
        )

        ticket.estado = (
            estado_cerrado
        )

        ticket.cerrado_en = (
            ahora
        )

        ticket.sla_cumplido = (
            calcular_sla_cumplido(
                ticket,
                ahora
            )
        )


        ticket.save(
            update_fields=[
                "conformidad_usuario",
                "observaciones_usuario",
                "conformidad_en",
                "estado",
                "cerrado_en",
                "sla_cumplido",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="INFORMAR_CONFORMIDAD",
            modulo="Soporte Técnico",
            detalle=(
                f"El solicitante informó "
                f"conformidad y se cerró "
                f"el ticket {ticket.codigo}. "
                f"SLA cumplido: "
                f"{ticket.sla_cumplido}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Conformidad registrada. Ticket cerrado."
        )