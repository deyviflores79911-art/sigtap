from django.utils import timezone
from rest_framework import serializers

from usuarios.models import Area

from .models import (
    EstadoMantenimiento,
    RequerimientoMantenimiento,
)


# ==========================================================
# ESTADO
# ==========================================================

class EstadoMantenimientoSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = EstadoMantenimiento

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "es_inicial",
            "es_terminal",
            "activo",
        ]


# ==========================================================
# REQUERIMIENTO DE MANTENIMIENTO
# ==========================================================

class RequerimientoMantenimientoSerializer(
    serializers.ModelSerializer
):

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
        source="estado.nombre",
        read_only=True
    )

    estado_codigo = serializers.CharField(
        source="estado.codigo",
        read_only=True
    )

    responsable_servicios_generales_nombre = (
        serializers.SerializerMethodField()
    )

    auxiliar_asignado_nombre = (
        serializers.SerializerMethodField()
    )

    evidencia_archivo_url = (
        serializers.SerializerMethodField()
    )

    fotografia_trabajo_url = (
        serializers.SerializerMethodField()
    )


    # ======================================================
    # CAMPOS QUE EL PORTAL SOLICITANTE YA NO PIDE
    # ======================================================
    #
    # El formulario simplificado del solicitante solo
    # captura título, descripción, categoría y foto. Estos
    # campos se completan con un valor por defecto en la
    # vista (RequerimientoMantenimientoViewSet.create)
    # cuando no llegan en el payload.
    # ======================================================

    area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        required=False
    )

    ubicacion = serializers.CharField(
        required=False,
        allow_blank=True
    )

    tipo = serializers.ChoiceField(
        choices=RequerimientoMantenimiento.TIPOS_MANTENIMIENTO,
        required=False
    )

    compra_vinculada = (
        serializers.SerializerMethodField()
    )


    class Meta:

        model = RequerimientoMantenimiento

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

            "ubicacion",

            "tipo",

            "evidencia",

            "evidencia_archivo",

            "evidencia_archivo_url",

            "estado",

            "estado_nombre",

            "estado_codigo",

            "responsable_servicios_generales",

            "responsable_servicios_generales_nombre",

            "auxiliar_asignado",

            "auxiliar_asignado_nombre",

            "compra_vinculada",

            "requiere_reposicion",

            "producto_requerido",

            "cantidad_requerida",

            "especificacion_producto",

            "producto_disponible_almacen",

            "producto_entregado",

            "observacion_almacen",

            "derivado_compra",

            "codigo_compra_vinculada",

            "compra_completada",

            "trabajo_realizado",

            "observaciones_trabajo",

            "informe_trabajo",

            "fotografia_trabajo",

            "fotografia_trabajo_url",

            "recibido_en",

            "derivado_en",

            "revision_almacen_en",

            "inicio_mantenimiento_en",

            "informe_registrado_en",

            "finalizado_en",

            "activo",

            "creado_en",

            "actualizado_en",
        ]


        read_only_fields = [

            "codigo",

            "solicitante",

            "estado",

            "responsable_servicios_generales",

            "auxiliar_asignado",

            "requiere_reposicion",

            "producto_requerido",

            "cantidad_requerida",

            "especificacion_producto",

            "producto_disponible_almacen",

            "producto_entregado",

            "observacion_almacen",

            "derivado_compra",

            "codigo_compra_vinculada",

            "compra_completada",

            "trabajo_realizado",

            "observaciones_trabajo",

            "informe_trabajo",

            "fotografia_trabajo",

            "recibido_en",

            "derivado_en",

            "revision_almacen_en",

            "inicio_mantenimiento_en",

            "informe_registrado_en",

            "finalizado_en",

            "creado_en",

            "actualizado_en",
        ]


    def get_responsable_servicios_generales_nombre(
        self,
        obj
    ):

        if not obj.responsable_servicios_generales:
            return None

        return (
            obj.responsable_servicios_generales
            .nombre_completo
        )


    def get_auxiliar_asignado_nombre(
        self,
        obj
    ):

        if not obj.auxiliar_asignado:
            return None

        return (
            obj.auxiliar_asignado
            .nombre_completo
        )


    def get_compra_vinculada(
        self,
        obj
    ):

        solicitud = (
            obj.compras_generadas
            .filter(activo=True)
            .order_by("-creado_en")
            .first()
        )

        if not solicitud:
            return None

        from compras.serializers import SolicitudCompraResumenSerializer

        return SolicitudCompraResumenSerializer(solicitud).data


    def get_evidencia_archivo_url(
        self,
        obj
    ):

        if not obj.evidencia_archivo:
            return None

        try:

            url = obj.evidencia_archivo.url

        except ValueError:

            return None


        request = self.context.get(
            "request"
        )


        if request:

            return request.build_absolute_uri(
                url
            )


        return url


    def get_fotografia_trabajo_url(
        self,
        obj
    ):

        if not obj.fotografia_trabajo:
            return None

        try:

            url = obj.fotografia_trabajo.url

        except ValueError:

            return None


        request = self.context.get(
            "request"
        )


        if request:

            return request.build_absolute_uri(
                url
            )


        return url


    def validate_evidencia_archivo(
        self,
        archivo
    ):

        if not archivo:
            return archivo


        maximo = (
            5
            *
            1024
            *
            1024
        )


        if archivo.size > maximo:

            raise serializers.ValidationError(
                "El archivo no puede superar los 5 MB."
            )


        nombre = archivo.name.lower()


        extensiones = (
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
        )


        if not nombre.endswith(
            extensiones
        ):

            raise serializers.ValidationError(
                "Solo se permiten archivos JPG, JPEG, PNG o PDF."
            )


        return archivo


    def create(
        self,
        validated_data
    ):

        request = self.context.get(
            "request"
        )


        if not request:

            raise serializers.ValidationError(
                {
                    "detalle":
                        "No se pudo identificar al usuario."
                }
            )


        try:

            estado_inicial = (
                EstadoMantenimiento.objects
                .get(
                    codigo="RECIBIDO",
                    activo=True
                )
            )

        except EstadoMantenimiento.DoesNotExist:

            raise serializers.ValidationError(
                {
                    "estado":
                        "No existe el estado RECIBIDO."
                }
            )


        anio = timezone.now().year

        prefijo = (
            f"MTO-{anio}-"
        )


        ultimo = (
            RequerimientoMantenimiento.objects
            .filter(
                codigo__startswith=prefijo
            )
            .order_by(
                "-codigo"
            )
            .first()
        )


        numero = 1


        if ultimo:

            try:

                numero = (
                    int(
                        ultimo.codigo
                        .split("-")[-1]
                    )
                    +
                    1
                )

            except (
                ValueError,
                IndexError
            ):

                numero = (
                    RequerimientoMantenimiento.objects
                    .filter(
                        codigo__startswith=prefijo
                    )
                    .count()
                    +
                    1
                )


        codigo = (
            f"{prefijo}{numero:04d}"
        )


        requerimiento = (
            RequerimientoMantenimiento.objects
            .create(
                codigo=codigo,
                solicitante=request.user,
                estado=estado_inicial,
                **validated_data
            )
        )


        return requerimiento