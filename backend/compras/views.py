from rest_framework import (
    status,
    viewsets,
)

from usuarios.authentication import (
    ExpiringTokenAuthentication as TokenAuthentication,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation


from usuarios.models import UsuarioRol, RolPermiso, obtener_codigos_rol_efectivos

from auditoria.utils import registrar_bitacora


from .models import (
    SolicitudCompra,
)

from .serializers import (
    SolicitudCompraSerializer,
)


# ==========================================================
# AUXILIAR
# ==========================================================

def obtener_roles(usuario):

    # Incluye roles delegados temporalmente (Delegar aprobación
    # temporal) además de los roles propios.
    return obtener_codigos_rol_efectivos(usuario)


def es_admin(usuario):

    if usuario.is_superuser:
        return True

    return (
        "ADMIN"
        in obtener_roles(usuario)
    )


def tiene_permiso(usuario, codigo_permiso):
    """Autorización real de Compras: sigue el mismo patrón de
    Permiso/RolPermiso ya usado en Soporte, en vez de comprobar
    el código de rol a mano en cada acción. Incluye roles
    delegados temporalmente y vigentes (obtener_roles)."""

    if es_admin(usuario):
        return True

    codigos_rol = obtener_roles(usuario)

    return (
        RolPermiso.objects
        .filter(
            rol__codigo__in=codigos_rol,
            rol__activo=True,
            permiso__codigo=codigo_permiso,
            permiso__activo=True,
            activo=True,
        )
        .exists()
    )


def respuesta_sin_permiso(codigo_permiso):
    return Response(
        {
            "detalle": "No tiene permiso para realizar esta actividad.",
            "permiso_requerido": codigo_permiso,
        },
        status=status.HTTP_403_FORBIDDEN,
    )


# ==========================================================
# SOLICITUDES DE COMPRA
# ==========================================================

class SolicitudCompraViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        SolicitudCompraSerializer
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

        usuario = self.request.user


        queryset = (
            SolicitudCompra.objects
            .select_related(
                "solicitante",
                "area"
            )
            .order_by(
                "-creado_en"
            )
        )


        # Actores del BPMN consultan la bandeja institucional.
        if tiene_permiso(usuario, "VER_COMPRAS"):
            return queryset


        # SOLICITANTE VE LOS SUYOS
        return queryset.filter(
            solicitante=usuario
        )


    # ======================================================
    # CREAR
    # ======================================================

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        if not tiene_permiso(request.user, "CARGAR_EXPEDIENTE"):
            return respuesta_sin_permiso("CARGAR_EXPEDIENTE")

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        solicitud = serializer.save()


        registrar_bitacora(
            request=request,
            accion="CREAR_SOLICITUD_COMPRA",
            modulo="Compras",
            detalle=(
                f"Se creó la solicitud "
                f"{solicitud.codigo}: "
                f"{solicitud.titulo}."
            ),
            nivel="INFO",
        )


        salida = self.get_serializer(
            solicitud
        )


        return Response(
            salida.data,
            status=status.HTTP_201_CREATED
        )


    # ======================================================
    # MODIFICAR
    # ======================================================

    # Campos que determinan el monto/objeto evaluado por DAF.
    # Una vez que el expediente sale de CREADO_PENDIENTE_DAF,
    # NADIE (ni ADMIN) puede modificarlos por esta vía genérica:
    # solo así el monto que Tesorería y Director vieron es
    # garantizado el mismo que se desembolsa/cierra.
    CAMPOS_INMUTABLES_EN_PROCESO = {
        "monto_estimado", "cantidad", "tipo",
        "especificaciones", "justificacion",
        "informe", "poa", "pedido", "proforma",
    }

    def partial_update(
        self,
        request,
        *args,
        **kwargs
    ):

        solicitud = (
            self.get_object()
        )

        en_proceso = solicitud.estado != "CREADO_PENDIENTE_DAF"


        # --------------------------------------------------
        # SOLICITANTE
        # --------------------------------------------------

        if (
            solicitud.solicitante_id
            == request.user.id
        ):

            if en_proceso:

                return Response(
                    {
                        "detalle":
                            "La solicitud ya está siendo procesada y no puede modificarse."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        elif not es_admin(
            request.user
        ):

            return Response(
                {
                    "detalle":
                        "No tiene permiso para modificar esta solicitud."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        elif en_proceso:

            campos_prohibidos = (
                self.CAMPOS_INMUTABLES_EN_PROCESO
                & set(request.data.keys())
            )

            if campos_prohibidos:

                return Response(
                    {
                        "detalle": (
                            "No se puede modificar "
                            f"{', '.join(sorted(campos_prohibidos))} "
                            "una vez que el expediente está en "
                            "proceso de aprobación."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
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
            accion="MODIFICAR_SOLICITUD_COMPRA",
            modulo="Compras",
            detalle=(
                f"Se modificó la solicitud "
                f"{solicitud.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta


    # ======================================================
    # ANULAR
    # ======================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):

        solicitud = (
            self.get_object()
        )


        # --------------------------------------------------
        # SOLO EL AUTOR
        # --------------------------------------------------

        if (
            solicitud.solicitante_id
            != request.user.id
        ):

            return Response(
                {
                    "detalle":
                        "Solo el solicitante puede anular su solicitud."
                },
                status=status.HTTP_403_FORBIDDEN
            )


        # --------------------------------------------------
        # SOLO NUEVO
        # --------------------------------------------------

        if (
            solicitud.estado
            not in ("NUEVO", "CREADO_PENDIENTE_DAF")
        ):

            return Response(
                {
                    "detalle":
                        "La solicitud ya está en procesamiento y no puede anularse."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        solicitud.estado = (
            "ANULADO"
        )

        solicitud.activo = False


        solicitud.save(
            update_fields=[
                "estado",
                "activo",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="ANULAR_SOLICITUD_COMPRA",
            modulo="Compras",
            detalle=(
                f"Se anuló la solicitud "
                f"{solicitud.codigo}."
            ),
            nivel="WARNING",
        )


        return Response(
            {
                "ok": True,
                "mensaje":
                    "Solicitud de compra anulada correctamente."
            },
            status=status.HTTP_200_OK
        )

    def _transicion(self, request, solicitud, permiso, origen, destino, accion, detalle):
        if not tiene_permiso(request.user, permiso):
            return respuesta_sin_permiso(permiso)
        if solicitud.cerrado_inmutable:
            return Response({"detalle": "El expediente está cerrado y es inmutable."}, status=status.HTTP_409_CONFLICT)
        if solicitud.estado not in origen:
            return Response({"detalle": f"Transición no permitida desde {solicitud.estado}."}, status=status.HTTP_409_CONFLICT)
        solicitud.estado = destino
        solicitud.save()
        registrar_bitacora(request=request, accion=accion, modulo="Compras", detalle=f"{solicitud.codigo}: {detalle}", nivel="INFO")
        return Response(self.get_serializer(solicitud).data)

    @action(detail=True, methods=["post"], url_path="evaluar-daf")
    def evaluar_daf(self, request, pk=None):
        solicitud = self.get_object()
        if not tiene_permiso(request.user, "EVALUAR_EXPEDIENTE"):
            return respuesta_sin_permiso("EVALUAR_EXPEDIENTE")
        if solicitud.estado != "CREADO_PENDIENTE_DAF":
            return Response({"detalle": "El expediente no está pendiente de evaluación DAF."}, status=409)
        califica = str(request.data.get("califica", "")).lower() in ("true", "1", "si", "sí")
        if not califica:
            motivo = str(request.data.get("motivo", "")).strip()
            if not motivo:
                return Response({"detalle": "Debe registrar el motivo del rechazo."}, status=400)
            solicitud.estado, solicitud.motivo_rechazo, solicitud.activo = "RECHAZADO", motivo, False
            solicitud.save()
            return Response(self.get_serializer(solicitud).data)
        return self._transicion(request, solicitud, "EVALUAR_EXPEDIENTE", ["CREADO_PENDIENTE_DAF"], "EVALUADO_PENDIENTE_CERTIFICACION", "EVALUAR_PRESUPUESTO", "La solicitud califica presupuestariamente.")

    @action(detail=True, methods=["post"], url_path="certificar-daf")
    def certificar_daf(self, request, pk=None):
        solicitud = self.get_object()
        if not tiene_permiso(request.user, "CERTIFICAR_PRESUPUESTO"):
            return respuesta_sin_permiso("CERTIFICAR_PRESUPUESTO")
        if solicitud.estado != "EVALUADO_PENDIENTE_CERTIFICACION":
            return Response({"detalle": "El expediente no está pendiente de certificación."}, status=409)
        archivo = request.FILES.get("certificacion_presupuestaria")
        if not archivo:
            return Response({"detalle": "Debe adjuntar la certificación presupuestaria PDF."}, status=400)
        if not archivo.name.lower().endswith(".pdf"):
            return Response({"detalle": "La certificación debe ser un archivo PDF."}, status=400)
        solicitud.certificacion_presupuestaria = archivo
        solicitud.save(update_fields=["certificacion_presupuestaria", "actualizado_en"])
        # El expediente certificado queda automáticamente disponible en la
        # bandeja institucional de Tesorería (get_queryset filtra por
        # VER_COMPRAS): no existe un paso de "derivar" independiente.
        return self._transicion(request, solicitud, "CERTIFICAR_PRESUPUESTO", ["EVALUADO_PENDIENTE_CERTIFICACION"], "CERTIFICADO_PENDIENTE_VERIFICACION", "CERTIFICAR_PRESUPUESTO", "Certificación adjuntada; expediente derivado automáticamente a Tesorería.")

    @action(detail=True, methods=["post"], url_path="verificar-tesoreria")
    def verificar_tesoreria(self, request, pk=None):
        s = self.get_object()
        if not tiene_permiso(request.user, "VERIFICAR_EXPEDIENTE_TESORERIA"):
            return respuesta_sin_permiso("VERIFICAR_EXPEDIENTE_TESORERIA")
        if not all((s.informe, s.poa, s.pedido, s.proforma, s.certificacion_presupuestaria)):
            return Response({"detalle": "El expediente no contiene los cinco documentos obligatorios."}, status=400)
        return self._transicion(request, s, "VERIFICAR_EXPEDIENTE_TESORERIA", ["CERTIFICADO_PENDIENTE_VERIFICACION"], "VERIFICADO_PENDIENTE_AUTORIZACION", "VERIFICAR_EXPEDIENTE", "Tesorería verificó la integridad del expediente.")

    @action(detail=True, methods=["post"], url_path="visto-bueno-director")
    def visto_bueno_director(self, request, pk=None):
        # Igual que certificar-daf: al dar el visto bueno, el expediente
        # queda automáticamente disponible para Tesorería (desembolso).
        return self._transicion(request, self.get_object(), "DAR_VISTO_BUENO", ["VERIFICADO_PENDIENTE_AUTORIZACION"], "APROBADO_PARA_DESEMBOLSO", "VISTO_BUENO_DIRECTOR", "Director autorizó; expediente derivado automáticamente a Tesorería para desembolso.")

    @action(detail=True, methods=["post"], url_path="rechazar")
    def rechazar(self, request, pk=None):
        # Rechazo genérico previo al desembolso. evaluar-daf ya cubre el
        # rechazo en el primer paso (CREADO_PENDIENTE_DAF); esta acción
        # cubre el resto de los pasos previos al desembolso, incluida la
        # decisión final del Director (visto-bueno-director no tenía
        # rama de rechazo).
        solicitud = self.get_object()

        if not tiene_permiso(request.user, "DAR_VISTO_BUENO"):
            return respuesta_sin_permiso("DAR_VISTO_BUENO")

        if solicitud.cerrado_inmutable:
            return Response({"detalle": "El expediente está cerrado y es inmutable."}, status=status.HTTP_409_CONFLICT)

        estados_rechazables = [
            "CREADO_PENDIENTE_DAF",
            "EVALUADO_PENDIENTE_CERTIFICACION",
            "CERTIFICADO_PENDIENTE_VERIFICACION",
            "VERIFICADO_PENDIENTE_AUTORIZACION",
        ]

        if solicitud.estado not in estados_rechazables:
            return Response({"detalle": f"Transición no permitida desde {solicitud.estado}."}, status=status.HTTP_409_CONFLICT)

        motivo = str(request.data.get("motivo", "")).strip()

        if not motivo:
            return Response({"detalle": "Debe registrar el motivo del rechazo."}, status=400)

        solicitud.estado = "RECHAZADO"
        solicitud.motivo_rechazo = motivo
        solicitud.activo = False
        solicitud.save()

        registrar_bitacora(
            request=request,
            accion="RECHAZAR_EXPEDIENTE",
            modulo="Compras",
            detalle=f"{solicitud.codigo}: {motivo}",
            nivel="INFO",
        )

        return Response(self.get_serializer(solicitud).data)

    @action(detail=True, methods=["post"], url_path="desembolsar")
    def desembolsar(self, request, pk=None):
        s = self.get_object()
        if not tiene_permiso(request.user, "REGISTRAR_DESEMBOLSO"):
            return respuesta_sin_permiso("REGISTRAR_DESEMBOLSO")
        if s.estado != "APROBADO_PARA_DESEMBOLSO":
            return Response({"detalle": "El expediente no está aprobado para desembolso."}, status=409)
        try: monto = Decimal(str(request.data.get("monto_desembolsado", "")))
        except InvalidOperation: return Response({"detalle": "Monto de desembolso inválido."}, status=400)
        responsable = str(request.data.get("responsable_adquisicion", "")).strip()
        if monto <= 0 or not responsable:
            return Response({"detalle": "Debe registrar monto y responsable de la adquisición."}, status=400)
        s.monto_desembolsado, s.responsable_adquisicion = monto, responsable
        s.save(update_fields=["monto_desembolsado", "responsable_adquisicion", "actualizado_en"])
        return self._transicion(request, s, "REGISTRAR_DESEMBOLSO", ["APROBADO_PARA_DESEMBOLSO"], "FONDOS_DESEMBOLSADOS", "DESEMBOLSAR_FONDOS", "Tesorería registró la entrega física del efectivo.")

    @action(detail=True, methods=["post"], url_path="registrar-compra")
    def registrar_compra(self, request, pk=None):
        s = self.get_object()
        if not tiene_permiso(request.user, "REALIZAR_COMPRA"):
            return respuesta_sin_permiso("REALIZAR_COMPRA")
        if s.estado != "FONDOS_DESEMBOLSADOS":
            return Response({"detalle": "Los fondos todavía no fueron desembolsados."}, status=409)
        try: monto = Decimal(str(request.data.get("monto_real", "")))
        except InvalidOperation: return Response({"detalle": "Monto real inválido."}, status=400)
        proveedor = str(request.data.get("proveedor", "")).strip()
        if monto <= 0 or not proveedor:
            return Response({"detalle": "Debe registrar monto real y proveedor."}, status=400)
        # Caso de uso "Registrar verificación de componentes": se exige
        # como parte del mismo registro de compra (no hay un paso de
        # verificación separado en el BPMN de Caja Chica).
        verificado = str(request.data.get("componente_verificado", "")).lower() in ("true", "1", "si", "sí")
        if not verificado:
            return Response({"detalle": "Debe confirmar la verificación de componentes antes de registrar la compra."}, status=400)
        s.monto_real, s.proveedor = monto, proveedor
        s.componente_verificado = True
        s.observacion_verificacion = str(request.data.get("observacion_verificacion", "")).strip()
        s.save(update_fields=["monto_real", "proveedor", "componente_verificado", "observacion_verificacion", "actualizado_en"])
        return self._transicion(request, s, "REALIZAR_COMPRA", ["FONDOS_DESEMBOLSADOS"], "COMPRA_REGISTRADA", "REGISTRAR_COMPRA", "Compra física registrada y componentes verificados.")

    @action(detail=True, methods=["post"], url_path="registrar-ingreso-almacen")
    def registrar_ingreso_almacen(self, request, pk=None):
        s = self.get_object()
        if not tiene_permiso(request.user, "REGISTRAR_ENTRADA_SALIDA_ALMACEN"):
            return respuesta_sin_permiso("REGISTRAR_ENTRADA_SALIDA_ALMACEN")
        if s.estado != "COMPRA_REGISTRADA":
            return Response({"detalle": "La compra todavía no fue registrada."}, status=409)
        if s.fecha_ingreso_almacen:
            return Response({"detalle": "El ingreso a almacén ya fue registrado."}, status=409)
        s.fecha_ingreso_almacen = timezone.now()
        s.save(update_fields=["fecha_ingreso_almacen", "actualizado_en"])
        registrar_bitacora(request=request, accion="REGISTRAR_INGRESO_ALMACEN", modulo="Compras", detalle=f"{s.codigo}: ingreso a almacén registrado.", nivel="INFO")
        return Response(self.get_serializer(s).data)

    @action(detail=True, methods=["post"], url_path="registrar-despacho-almacen")
    def registrar_despacho_almacen(self, request, pk=None):
        s = self.get_object()
        if not tiene_permiso(request.user, "ENTREGAR_PRODUCTO"):
            return respuesta_sin_permiso("ENTREGAR_PRODUCTO")
        if s.estado != "COMPRA_REGISTRADA":
            return Response({"detalle": "La compra todavía no fue registrada."}, status=409)
        if not s.fecha_ingreso_almacen:
            return Response({"detalle": "Debe registrar primero el ingreso a almacén."}, status=409)
        s.fecha_despacho_almacen = timezone.now()
        s.save(update_fields=["fecha_despacho_almacen", "actualizado_en"])
        return self._transicion(request, s, "ENTREGAR_PRODUCTO", ["COMPRA_REGISTRADA"], "COMPRADO_Y_ENTREGADO", "REGISTRAR_DESPACHO_ALMACEN", "Despacho desde almacén registrado; producto entregado a la unidad solicitante.")

    @action(detail=True, methods=["post"], url_path="presentar-descargo")
    def presentar_descargo(self, request, pk=None):
        s = self.get_object()
        if s.solicitante_id != request.user.id and not es_admin(request.user):
            return Response({"detalle": "Solo el solicitante puede presentar el descargo."}, status=403)
        if s.estado != "COMPRADO_Y_ENTREGADO":
            return Response({"detalle": "La compra todavía no fue entregada."}, status=409)
        archivos = {n: request.FILES.get(n) for n in ("factura", "acta_conformidad", "fotograma")}
        if not all(archivos.values()):
            return Response({"detalle": "Debe adjuntar Factura, Acta de Conformidad y Fotograma."}, status=400)
        for nombre, archivo in archivos.items(): setattr(s, nombre, archivo)
        s.estado = "DESCARGO_PENDIENTE_LIQUIDACION"
        s.save()
        registrar_bitacora(request=request, accion="REGISTRAR_DESCARGO", modulo="Compras", detalle=f"{s.codigo}: descargo presentado por el solicitante.", nivel="INFO")
        return Response(self.get_serializer(s).data)

    @action(detail=True, methods=["post"], url_path="cerrar-archivar")
    @transaction.atomic
    def cerrar_archivar(self, request, pk=None):
        s = self.get_object()
        if not tiene_permiso(request.user, "CERRAR_ARCHIVAR_EXPEDIENTE"):
            return respuesta_sin_permiso("CERRAR_ARCHIVAR_EXPEDIENTE")
        if s.estado != "DESCARGO_PENDIENTE_LIQUIDACION" or not all((s.factura, s.acta_conformidad, s.fotograma)):
            return Response({"detalle": "El descargo no está completo."}, status=409)
        if s.monto_desembolsado is not None and s.monto_real != s.monto_desembolsado:
            return Response({"detalle": "El monto de la factura no coincide con el dinero desembolsado."}, status=400)
        s.estado, s.cerrado_inmutable, s.activo = "CERRADO_ARCHIVADO", True, False
        s.save()
        registrar_bitacora(request=request, accion="CERRAR_CAJA_CHICA", modulo="Compras", detalle=f"{s.codigo}: expediente liquidado y archivado de forma inmutable.", nivel="INFO")
        return Response(self.get_serializer(s).data)
