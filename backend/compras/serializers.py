from django.utils import timezone
from rest_framework import serializers

from .models import SolicitudCompra


class SolicitudCompraSerializer(serializers.ModelSerializer):

    solicitante_nombre = serializers.CharField(
        source="solicitante.nombre_completo",
        read_only=True
    )

    solicitante_email = serializers.CharField(
        source="solicitante.email",
        read_only=True
    )

    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True
    )

    estado_nombre = serializers.CharField(
        source="get_estado_display",
        read_only=True
    )

    tipo_nombre = serializers.CharField(
        source="get_tipo_display",
        read_only=True
    )

    via_nombre = serializers.CharField(
        source="get_via_adquisicion_display",
        read_only=True
    )

    class Meta:

        model = SolicitudCompra

        fields = [
            "id",
            "codigo",
            "titulo",
            "descripcion",

            "solicitante",
            "solicitante_nombre",
            "solicitante_email",

            "area",
            "area_nombre",

            "tipo",
            "tipo_nombre",

            "cantidad",
            "especificaciones",
            "justificacion",
            "centro_costo",

            "monto_estimado",

            "via_adquisicion",
            "via_nombre",

            "estado",
            "estado_nombre",

            "ticket_soporte_vinculado",

            "observaciones",

            "activo",

            "creado_en",
            "actualizado_en",
        ]

        read_only_fields = [
            "codigo",
            "solicitante",
            "estado",
            "via_adquisicion",
            "observaciones",
            "creado_en",
            "actualizado_en",
        ]

    def create(self, validated_data):

        request = self.context["request"]

        usuario = request.user

        anio = timezone.now().year

        prefijo = f"CMP-{anio}-"

        ultimo = (
            SolicitudCompra.objects
            .filter(
                codigo__startswith=prefijo
            )
            .order_by("-codigo")
            .first()
        )

        numero = 1

        if ultimo:

            try:
                numero = (
                    int(
                        ultimo.codigo.split("-")[-1]
                    )
                    + 1
                )

            except ValueError:
                numero = (
                    SolicitudCompra.objects.count()
                    + 1
                )

        codigo = (
            f"{prefijo}{numero:04d}"
        )

        return SolicitudCompra.objects.create(
            codigo=codigo,
            solicitante=usuario,
            estado="NUEVO",
            **validated_data
        )