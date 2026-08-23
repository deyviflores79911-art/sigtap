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


        # ADMIN VE TODO
        if es_admin(usuario):
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
                != "NUEVO"
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
            != "NUEVO"
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