from rest_framework import (
    status,
    viewsets,
)

from rest_framework.authentication import (
    TokenAuthentication,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from decimal import Decimal, InvalidOperation


from usuarios.models import UsuarioRol

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

    return list(
        UsuarioRol.objects
        .filter(
            usuario=usuario,
            activo=True,
            rol__activo=True,
        )
        .values_list(
            "rol__codigo",
            flat=True
        )
    )


def es_admin(usuario):

    if usuario.is_superuser:
        return True

    return (
        "ADMIN"
        in obtener_roles(usuario)
    )


def tiene_rol(usuario, *codigos):
    return es_admin(usuario) or bool(set(obtener_roles(usuario)) & set(codigos))


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
        if tiene_rol(usuario, "DAF", "TESORERIA", "DIRECTOR", "ENCARGADO_COMPRAS_ALMACEN"):
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

    def partial_update(
        self,
        request,
        *args,
        **kwargs
    ):

        solicitud = (
            self.get_object()
        )


        # --------------------------------------------------
        # SOLICITANTE
        # --------------------------------------------------

        if (
            solicitud.solicitante_id
            == request.user.id
        ):

            if (
                solicitud.estado
                not in ("NUEVO", "CREADO_PENDIENTE_DAF")
            ):

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

    def _transicion(self, request, solicitud, rol, origen, destino, accion, detalle):
        if not tiene_rol(request.user, rol):
            return Response({"detalle": f"Esta acción corresponde al rol {rol}."}, status=status.HTTP_403_FORBIDDEN)
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
        if not tiene_rol(request.user, "DAF"):
            return Response({"detalle": "Acción exclusiva de DAF."}, status=403)
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
        return self._transicion(request, solicitud, "DAF", ["CREADO_PENDIENTE_DAF"], "EVALUADO_PENDIENTE_CERTIFICACION", "EVALUAR_PRESUPUESTO", "La solicitud califica presupuestariamente.")

    @action(detail=True, methods=["post"], url_path="certificar-daf")
    def certificar_daf(self, request, pk=None):
        solicitud = self.get_object()
        if not tiene_rol(request.user, "DAF"):
            return Response({"detalle": "Acción exclusiva de DAF."}, status=403)
        if solicitud.estado != "EVALUADO_PENDIENTE_CERTIFICACION":
            return Response({"detalle": "El expediente no está pendiente de certificación."}, status=409)
        archivo = request.FILES.get("certificacion_presupuestaria")
        if not archivo:
            return Response({"detalle": "Debe adjuntar la certificación presupuestaria PDF."}, status=400)
        if not archivo.name.lower().endswith(".pdf"):
            return Response({"detalle": "La certificación debe ser un archivo PDF."}, status=400)
        solicitud.certificacion_presupuestaria = archivo
        solicitud.save(update_fields=["certificacion_presupuestaria", "actualizado_en"])
        return self._transicion(request, solicitud, "DAF", ["EVALUADO_PENDIENTE_CERTIFICACION"], "CERTIFICADO_PENDIENTE_VERIFICACION", "CERTIFICAR_PRESUPUESTO", "Certificación adjuntada y expediente enviado a Tesorería.")

    @action(detail=True, methods=["post"], url_path="verificar-tesoreria")
    def verificar_tesoreria(self, request, pk=None):
        s = self.get_object()
        if not all((s.informe, s.poa, s.pedido, s.proforma, s.certificacion_presupuestaria)):
            return Response({"detalle": "El expediente no contiene los cinco documentos obligatorios."}, status=400)
        return self._transicion(request, s, "TESORERIA", ["CERTIFICADO_PENDIENTE_VERIFICACION"], "VERIFICADO_PENDIENTE_AUTORIZACION", "VERIFICAR_EXPEDIENTE", "Tesorería verificó la integridad del expediente.")

    @action(detail=True, methods=["post"], url_path="visto-bueno-director")
    def visto_bueno_director(self, request, pk=None):
        return self._transicion(request, self.get_object(), "DIRECTOR", ["VERIFICADO_PENDIENTE_AUTORIZACION"], "APROBADO_PARA_DESEMBOLSO", "VISTO_BUENO_DIRECTOR", "Director autorizó y derivó a Tesorería.")

    @action(detail=True, methods=["post"], url_path="desembolsar")
    def desembolsar(self, request, pk=None):
        s = self.get_object()
        if not tiene_rol(request.user, "TESORERIA"):
            return Response({"detalle": "Acción exclusiva de Tesorería."}, status=403)
        if s.estado != "APROBADO_PARA_DESEMBOLSO":
            return Response({"detalle": "El expediente no está aprobado para desembolso."}, status=409)
        try: monto = Decimal(str(request.data.get("monto_desembolsado", "")))
        except InvalidOperation: return Response({"detalle": "Monto de desembolso inválido."}, status=400)
        responsable = str(request.data.get("responsable_adquisicion", "")).strip()
        if monto <= 0 or not responsable:
            return Response({"detalle": "Debe registrar monto y responsable de la adquisición."}, status=400)
        s.monto_desembolsado, s.responsable_adquisicion = monto, responsable
        s.save(update_fields=["monto_desembolsado", "responsable_adquisicion", "actualizado_en"])
        return self._transicion(request, s, "TESORERIA", ["APROBADO_PARA_DESEMBOLSO"], "FONDOS_DESEMBOLSADOS", "DESEMBOLSAR_FONDOS", "Tesorería registró la entrega física del efectivo.")

    @action(detail=True, methods=["post"], url_path="registrar-compra")
    def registrar_compra(self, request, pk=None):
        s = self.get_object()
        if not tiene_rol(request.user, "ENCARGADO_COMPRAS_ALMACEN"):
            return Response({"detalle": "Acción exclusiva de Compras y Almacén."}, status=403)
        if s.estado != "FONDOS_DESEMBOLSADOS":
            return Response({"detalle": "Los fondos todavía no fueron desembolsados."}, status=409)
        try: monto = Decimal(str(request.data.get("monto_real", "")))
        except InvalidOperation: return Response({"detalle": "Monto real inválido."}, status=400)
        proveedor = str(request.data.get("proveedor", "")).strip()
        if monto <= 0 or not proveedor:
            return Response({"detalle": "Debe registrar monto real y proveedor."}, status=400)
        s.monto_real, s.proveedor = monto, proveedor
        s.save(update_fields=["monto_real", "proveedor", "actualizado_en"])
        return self._transicion(request, s, "ENCARGADO_COMPRAS_ALMACEN", ["FONDOS_DESEMBOLSADOS"], "COMPRA_REGISTRADA", "REGISTRAR_COMPRA", "Compra física registrada.")

    @action(detail=True, methods=["post"], url_path="registrar-entrega")
    def registrar_entrega(self, request, pk=None):
        return self._transicion(request, self.get_object(), "ENCARGADO_COMPRAS_ALMACEN", ["COMPRA_REGISTRADA"], "COMPRADO_Y_ENTREGADO", "REGISTRAR_ENTRADA_SALIDA", "Ingreso y salida de almacén registrados.")

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
        return Response(self.get_serializer(s).data)

    @action(detail=True, methods=["post"], url_path="cerrar-archivar")
    @transaction.atomic
    def cerrar_archivar(self, request, pk=None):
        s = self.get_object()
        if not tiene_rol(request.user, "TESORERIA"):
            return Response({"detalle": "Acción exclusiva de Tesorería."}, status=403)
        if s.estado != "DESCARGO_PENDIENTE_LIQUIDACION" or not all((s.factura, s.acta_conformidad, s.fotograma)):
            return Response({"detalle": "El descargo no está completo."}, status=409)
        if s.monto_desembolsado is not None and s.monto_real != s.monto_desembolsado:
            return Response({"detalle": "El monto de la factura no coincide con el dinero desembolsado."}, status=400)
        s.estado, s.cerrado_inmutable, s.activo = "CERRADO_ARCHIVADO", True, False
        s.save()
        registrar_bitacora(request=request, accion="CERRAR_CAJA_CHICA", modulo="Compras", detalle=f"{s.codigo}: expediente liquidado y archivado de forma inmutable.", nivel="INFO")
        return Response(self.get_serializer(s).data)
