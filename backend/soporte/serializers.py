from django.utils import timezone

from rest_framework import serializers


from .models import (
    CategoriaTicket,
    EstadoTicket,
    Ticket,
)


# ==========================================================
# CATEGORÍA
# ==========================================================

class CategoriaTicketSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = CategoriaTicket

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "activo",
        ]


# ==========================================================
# ESTADO
# ==========================================================

class EstadoTicketSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = EstadoTicket

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
# TICKET SOPORTE TÉCNICO
# ==========================================================

class TicketSerializer(
    serializers.ModelSerializer
):

    # ======================================================
    # DATOS DESCRIPTIVOS PARA EL FRONTEND
    # ======================================================

    solicitante_nombre = serializers.CharField(
        source="solicitante.nombre_completo",
        read_only=True
    )

    solicitante_email = serializers.CharField(
        source="solicitante.email",
        read_only=True
    )

    tecnico_nombre = serializers.SerializerMethodField()

    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True
    )

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True
    )

    categoria_codigo = serializers.CharField(
        source="categoria.codigo",
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

    especialistas_apoyo_nombres = (
        serializers.SerializerMethodField()
    )


    # ======================================================
    # EVIDENCIA
    # ======================================================

    evidencia_archivo = serializers.FileField(
        required=False,
        allow_null=True
    )

    evidencia_archivo_url = (
        serializers.SerializerMethodField()
    )


    # ======================================================
    # DATOS CALCULADOS DEL SLA
    # ======================================================

    sla_estado = (
        serializers.SerializerMethodField()
    )

    sla_restante_minutos = (
        serializers.SerializerMethodField()
    )


    # ======================================================
    # META
    # ======================================================

    class Meta:

        model = Ticket

        fields = [

            # ------------------------------------------------
            # IDENTIFICACIÓN
            # ------------------------------------------------

            "id",

            "codigo",

            "titulo",

            "descripcion",


            # ------------------------------------------------
            # SOLICITANTE
            # ------------------------------------------------

            "solicitante",

            "solicitante_nombre",

            "solicitante_email",


            # ------------------------------------------------
            # ÁREA / UBICACIÓN
            # ------------------------------------------------

            "area",

            "area_nombre",

            "ubicacion",

            "equipo_afectado",


            # ------------------------------------------------
            # EVIDENCIA
            # ------------------------------------------------

            "evidencia",

            "evidencia_archivo",

            "evidencia_archivo_url",


            # ------------------------------------------------
            # CLASIFICACIÓN UTIC
            # ------------------------------------------------

            "categoria",

            "categoria_nombre",

            "categoria_codigo",

            "tipo_problema",

            "prioridad",

            "criterio_tecnico",


            # ------------------------------------------------
            # SLA
            # ------------------------------------------------

            "sla_horas",

            "sla_fecha_limite",

            "sla_cumplido",

            "sla_estado",

            "sla_restante_minutos",


            # ------------------------------------------------
            # ESTADO
            # ------------------------------------------------

            "estado",

            "estado_nombre",

            "estado_codigo",


            # ------------------------------------------------
            # RESPONSABLES
            # ------------------------------------------------

            "tecnico_asignado",

            "tecnico_nombre",

            "especialistas_apoyo",

            "especialistas_apoyo_nombres",


            # ------------------------------------------------
            # DIAGNÓSTICO
            # ------------------------------------------------

            "diagnostico",

            "plan_solucion",

            "solucion",


            # ------------------------------------------------
            # COMPRA VINCULADA
            # ------------------------------------------------

            "requiere_compra",

            "componente_requerido",

            "especificaciones_tecnicas",

            "costo_estimado",

            "codigo_compra_vinculada",


            # ------------------------------------------------
            # RESULTADOS
            # ------------------------------------------------

            "resultado_pruebas",

            "conformidad_usuario",

            "observaciones_usuario",

            "informe_final",


            # ------------------------------------------------
            # FECHAS DEL WORKFLOW
            # ------------------------------------------------

            "validado_en",

            "clasificado_en",

            "asignado_en",

            "inicio_atencion_en",

            "pruebas_en",

            "verificado_en",

            "conformidad_en",


            # ------------------------------------------------
            # CONTROL Y AUDITORÍA
            # ------------------------------------------------

            "rework_count",

            "activo",

            "creado_en",

            "actualizado_en",

            "cerrado_en",
        ]


        # ==================================================
        # CAMPOS CONTROLADOS POR SIGTA
        # ==================================================
        #
        # El solicitante NO puede enviar estos valores
        # directamente.
        #
        # Son modificados mediante las acciones específicas
        # definidas en soporte/views.py.
        #
        # ==================================================

        read_only_fields = [

            "codigo",

            "solicitante",

            "estado",

            "tecnico_asignado",

            "especialistas_apoyo",

            "tipo_problema",

            "prioridad",

            "criterio_tecnico",


            # SLA

            "sla_horas",

            "sla_fecha_limite",

            "sla_cumplido",


            # Diagnóstico

            "diagnostico",

            "plan_solucion",

            "solucion",


            # Compra

            "requiere_compra",

            "componente_requerido",

            "especificaciones_tecnicas",

            "costo_estimado",

            "codigo_compra_vinculada",


            # Resultados

            "resultado_pruebas",

            "conformidad_usuario",

            "observaciones_usuario",

            "informe_final",


            # Fechas workflow

            "validado_en",

            "clasificado_en",

            "asignado_en",

            "inicio_atencion_en",

            "pruebas_en",

            "verificado_en",

            "conformidad_en",


            # Control

            "rework_count",

            "cerrado_en",

            "creado_en",

            "actualizado_en",
        ]


    # ======================================================
    # TÉCNICO ASIGNADO
    # ======================================================

    def get_tecnico_nombre(
        self,
        obj
    ):

        if not obj.tecnico_asignado:

            return None


        return (
            obj.tecnico_asignado
            .nombre_completo
        )


    # ======================================================
    # ESPECIALISTAS DE APOYO
    # ======================================================

    def get_especialistas_apoyo_nombres(
        self,
        obj
    ):

        return [
            usuario.nombre_completo

            for usuario
            in obj.especialistas_apoyo.all()
        ]


    # ======================================================
    # URL DEL ARCHIVO DE EVIDENCIA
    # ======================================================

    def get_evidencia_archivo_url(
        self,
        obj
    ):

        if not obj.evidencia_archivo:

            return None


        try:

            url = (
                obj.evidencia_archivo.url
            )

        except ValueError:

            return None


        request = self.context.get(
            "request"
        )


        if request:

            return (
                request.build_absolute_uri(
                    url
                )
            )


        return url


    # ======================================================
    # ESTADO DEL SLA
    # ======================================================

    def get_sla_estado(
        self,
        obj
    ):

        # --------------------------------------------------
        # TODAVÍA NO TIENE SLA
        # --------------------------------------------------

        if not obj.sla_fecha_limite:

            return "SIN_SLA"


        # --------------------------------------------------
        # TICKET CERRADO
        # --------------------------------------------------

        if obj.cerrado_en:

            if obj.sla_cumplido is True:

                return "CUMPLIDO"


            if obj.sla_cumplido is False:

                return "INCUMPLIDO"


        # --------------------------------------------------
        # TICKET ACTIVO
        # --------------------------------------------------

        ahora = timezone.now()


        if ahora > obj.sla_fecha_limite:

            return "VENCIDO"


        # --------------------------------------------------
        # CALCULAR RIESGO
        # --------------------------------------------------

        if obj.clasificado_en:

            duracion_total = (
                obj.sla_fecha_limite
                -
                obj.clasificado_en
            )

            tiempo_restante = (
                obj.sla_fecha_limite
                -
                ahora
            )


            # Menos del 25 % del SLA restante
            if (
                duracion_total.total_seconds()
                >
                0
            ):

                porcentaje_restante = (
                    tiempo_restante.total_seconds()
                    /
                    duracion_total.total_seconds()
                )


                if porcentaje_restante <= 0.25:

                    return "EN_RIESGO"


        return "EN_TIEMPO"


    # ======================================================
    # MINUTOS RESTANTES DEL SLA
    # ======================================================

    def get_sla_restante_minutos(
        self,
        obj
    ):

        if not obj.sla_fecha_limite:

            return None


        if obj.cerrado_en:

            return 0


        diferencia = (
            obj.sla_fecha_limite
            -
            timezone.now()
        )


        return int(
            diferencia.total_seconds()
            /
            60
        )


    # ======================================================
    # VALIDAR ARCHIVO DE EVIDENCIA
    # ======================================================

    def validate_evidencia_archivo(
        self,
        archivo
    ):

        if not archivo:

            return archivo


        # --------------------------------------------------
        # TAMAÑO MÁXIMO: 5 MB
        # --------------------------------------------------

        maximo = (
            5
            *
            1024
            *
            1024
        )


        if archivo.size > maximo:

            raise serializers.ValidationError(
                (
                    "El archivo no puede "
                    "superar los 5 MB."
                )
            )


        # --------------------------------------------------
        # EXTENSIONES
        # --------------------------------------------------

        nombre = (
            archivo.name
            .lower()
        )


        extensiones_permitidas = (
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
        )


        if not nombre.endswith(
            extensiones_permitidas
        ):

            raise serializers.ValidationError(
                (
                    "Solo se permiten archivos "
                    "JPG, JPEG, PNG o PDF."
                )
            )


        return archivo


    # ======================================================
    # VALIDACIÓN GENERAL
    # ======================================================

    def validate(
        self,
        attrs
    ):

        # --------------------------------------------------
        # IMPORTANTE:
        #
        # En PATCH pueden no venir todos los campos.
        # Por eso utilizamos instance cuando exista.
        # --------------------------------------------------

        titulo = attrs.get(
            "titulo",
            getattr(
                self.instance,
                "titulo",
                ""
            )
        )


        descripcion = attrs.get(
            "descripcion",
            getattr(
                self.instance,
                "descripcion",
                ""
            )
        )


        ubicacion = attrs.get(
            "ubicacion",
            getattr(
                self.instance,
                "ubicacion",
                ""
            )
        )


        equipo = attrs.get(
            "equipo_afectado",
            getattr(
                self.instance,
                "equipo_afectado",
                ""
            )
        )


        # --------------------------------------------------
        # NORMALIZAR
        # --------------------------------------------------

        titulo = (
            str(
                titulo
                or
                ""
            )
            .strip()
        )


        descripcion = (
            str(
                descripcion
                or
                ""
            )
            .strip()
        )


        ubicacion = (
            str(
                ubicacion
                or
                ""
            )
            .strip()
        )


        equipo = (
            str(
                equipo
                or
                ""
            )
            .strip()
        )


        # --------------------------------------------------
        # VALIDACIONES
        # --------------------------------------------------

        if not titulo:

            raise serializers.ValidationError(
                {
                    "titulo":
                        "El título es obligatorio."
                }
            )


        if not descripcion:

            raise serializers.ValidationError(
                {
                    "descripcion":
                        "La descripción es obligatoria."
                }
            )


        if not ubicacion:

            raise serializers.ValidationError(
                {
                    "ubicacion":
                        "La ubicación es obligatoria."
                }
            )


        if not equipo:

            raise serializers.ValidationError(
                {
                    "equipo_afectado": (
                        "Debe indicar el equipo "
                        "afectado."
                    )
                }
            )


        return attrs


    # ======================================================
    # CREAR TICKET
    # ======================================================

    def create(
        self,
        validated_data
    ):

        request = (
            self.context.get(
                "request"
            )
        )


        if not request:

            raise serializers.ValidationError(
                {
                    "detalle": (
                        "No se pudo identificar "
                        "al usuario."
                    )
                }
            )


        usuario = (
            request.user
        )


        # ==================================================
        # ESTADO INICIAL
        # ==================================================

        try:

            estado_nuevo = (
                EstadoTicket.objects
                .get(
                    codigo="NUEVO",
                    activo=True
                )
            )


        except EstadoTicket.DoesNotExist:

            raise serializers.ValidationError(
                {
                    "estado": (
                        "No existe el estado NUEVO "
                        "activo en el sistema."
                    )
                }
            )


        # ==================================================
        # GENERAR CÓDIGO
        # SOP-2026-0001
        # ==================================================

        anio = (
            timezone.now().year
        )


        prefijo = (
            f"SOP-{anio}-"
        )


        ultimo = (
            Ticket.objects
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
                    Ticket.objects
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


        # ==================================================
        # CREAR
        # ==========================================================

        ticket = (
            Ticket.objects.create(

                codigo=codigo,

                solicitante=usuario,

                estado=estado_nuevo,

                # ==========================================
                # EL SOLICITANTE NO DEFINE:
                #
                # - prioridad
                # - SLA
                # - responsable
                # - estado
                #
                # ==========================================

                prioridad=None,

                sla_horas=None,

                sla_fecha_limite=None,

                sla_cumplido=None,

                **validated_data
            )
        )


        return ticket