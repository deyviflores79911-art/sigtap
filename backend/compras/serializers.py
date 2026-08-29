from urllib.parse import urlsplit

from rest_framework import serializers

from .models import SolicitudCompra


# ==========================================================
# ARCHIVOS DEL EXPEDIENTE
# ==========================================================
#
# Se sirven como ruta relativa ("/media/...") en vez de URL
# absoluta con el host interno del backend (127.0.0.1:8000),
# que nunca es alcanzable desde fuera de esta máquina. El
# frontend (Vite) reenvía /media al backend, así que la ruta
# relativa siempre resuelve contra el mismo origen que sirvió
# la página (localhost o el túnel público).
# ==========================================================

CAMPOS_ARCHIVO = (
    "informe", "poa", "pedido", "proforma",
    "certificacion_presupuestaria",
    "factura", "acta_conformidad", "fotograma",
)


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

            "origen_modulo",
            "ticket_soporte",
            "requerimiento_mantenimiento",
            "ticket_soporte_vinculado",

            "observaciones",
            "informe", "poa", "pedido", "proforma",
            "certificacion_presupuestaria",
            "factura", "acta_conformidad", "fotograma",
            "motivo_rechazo", "monto_desembolsado",
            "responsable_adquisicion", "monto_real", "proveedor",
            "componente_verificado", "observacion_verificacion",
            "fecha_ingreso_almacen", "fecha_despacho_almacen",
            "cerrado_inmutable",

            "activo",

            "creado_en",
            "actualizado_en",
        ]

        read_only_fields = [
            "codigo",
            "solicitante",
            "estado",
            "via_adquisicion",
            "origen_modulo",
            "ticket_soporte",
            "requerimiento_mantenimiento",
            "ticket_soporte_vinculado",
            "observaciones",
            "certificacion_presupuestaria", "factura",
            "acta_conformidad", "fotograma", "motivo_rechazo",
            "monto_desembolsado", "responsable_adquisicion",
            "monto_real", "proveedor",
            "componente_verificado", "observacion_verificacion",
            "fecha_ingreso_almacen", "fecha_despacho_almacen",
            "cerrado_inmutable",
            "creado_en",
            "actualizado_en",
        ]

    def to_representation(self, instance):

        data = super().to_representation(instance)

        for campo in CAMPOS_ARCHIVO:

            valor = data.get(campo)

            if valor:
                data[campo] = urlsplit(valor).path

        return data

    def create(self, validated_data):

        request = self.context["request"]

        usuario = request.user

        return SolicitudCompra.objects.create(
            codigo=SolicitudCompra.generar_codigo(),
            solicitante=usuario,
            estado="CREADO_PENDIENTE_DAF",
            **validated_data
        )

    def validate(self, attrs):
        if self.instance is None:
            faltantes = [
                nombre for nombre in ("informe", "poa", "pedido", "proforma")
                if not attrs.get(nombre)
            ]
            if faltantes:
                raise serializers.ValidationError({
                    "documentos": "Debe adjuntar Informe, POA, Pedido y Proforma. Faltan: " + ", ".join(faltantes)
                })

        # Se exige PDF para que el expediente sea previsualizable
        # (el navegador no puede renderizar .docx/.pptx en línea).
        no_pdf = [
            nombre for nombre in ("informe", "poa", "pedido", "proforma")
            if attrs.get(nombre) and not attrs[nombre].name.lower().endswith(".pdf")
        ]
        if no_pdf:
            raise serializers.ValidationError({
                "documentos": "Informe, POA, Pedido y Proforma deben ser archivos PDF: " + ", ".join(no_pdf)
            })

        return attrs


class SolicitudCompraResumenSerializer(serializers.ModelSerializer):
    """Resumen liviano usado por Mantenimiento/Soporte para
    mostrar el estado de una compra vinculada sin exponer todos
    los campos ni requerir permiso de Compras."""

    estado_nombre = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = SolicitudCompra
        fields = ["id", "codigo", "titulo", "estado", "estado_nombre", "creado_en", "actualizado_en"]
        read_only_fields = fields
