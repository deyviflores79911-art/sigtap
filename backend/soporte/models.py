from django.conf import settings
from django.db import models

from usuarios.models import Area


# ==========================================================
# CATEGORÍAS DE SOPORTE
# ==========================================================

class CategoriaTicket(models.Model):

    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre


# ==========================================================
# ESTADOS DEL WORKFLOW
# ==========================================================

class EstadoTicket(models.Model):

    codigo = models.CharField(
        max_length=40,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    es_inicial = models.BooleanField(
        default=False
    )

    es_terminal = models.BooleanField(
        default=False
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre


# ==========================================================
# TICKET SOPORTE TÉCNICO
# ==========================================================

class Ticket(models.Model):

    # ======================================================
    # OPCIONES
    # ======================================================

    PRIORIDADES = [
        ("BAJA", "Baja"),
        ("MEDIA", "Media"),
        ("ALTA", "Alta"),
        ("CRITICA", "Crítica"),
    ]

    TIPOS_PROBLEMA = [
        ("HARDWARE", "Hardware"),
        ("SOFTWARE", "Software"),
        ("RED", "Redes y conectividad"),
        ("PROYECTOR", "Proyectores"),
        ("SISTEMA", "Sistema institucional"),
        ("ACCESO", "Accesos y cuentas"),
        ("OTRO", "Otro"),
    ]


    # ======================================================
    # IDENTIFICACIÓN
    # ======================================================

    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    titulo = models.CharField(
        max_length=200
    )

    descripcion = models.TextField()


    # ======================================================
    # SOLICITANTE
    # ======================================================

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tickets_solicitados"
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="tickets_soporte"
    )

    ubicacion = models.CharField(
        max_length=200
    )

    equipo_afectado = models.CharField(
        max_length=200
    )


    # ======================================================
    # EVIDENCIA
    # ======================================================

    evidencia = models.TextField(
        blank=True,
        default="",
        help_text="Descripción adicional de la evidencia."
    )

    evidencia_archivo = models.FileField(
        upload_to="soporte/evidencias/%Y/%m/",
        blank=True,
        null=True,
        help_text="Imagen o documento adjunto como evidencia."
    )


    # ======================================================
    # CLASIFICACIÓN UTIC
    # ======================================================

    categoria = models.ForeignKey(
        CategoriaTicket,
        on_delete=models.PROTECT,
        related_name="tickets"
    )

    tipo_problema = models.CharField(
        max_length=30,
        choices=TIPOS_PROBLEMA,
        blank=True
    )

    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDADES,
        null=True,
        blank=True
    )

    criterio_tecnico = models.TextField(
        blank=True
    )


    # ======================================================
    # SLA
    # ======================================================
    #
    # Se registra cuando el Jefe de UTIC realiza:
    #
    # "Clasificar prioridad y asignar SLA"
    #
    # Ejemplo:
    #
    # CRÍTICA -> 4 horas
    # ALTA    -> 8 horas
    # MEDIA   -> 24 horas
    # BAJA    -> 48 horas
    #
    # Posteriormente podremos configurar estos valores
    # desde Preferencias del sistema.
    #
    # ======================================================

    sla_horas = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Cantidad de horas asignadas para el SLA."
    )

    sla_fecha_limite = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora límite de atención según SLA."
    )

    sla_cumplido = models.BooleanField(
        null=True,
        blank=True,
        help_text=(
            "Indica si el ticket fue resuelto "
            "dentro del SLA establecido."
        )
    )


    # ======================================================
    # ESTADO DEL TICKET
    # ======================================================

    estado = models.ForeignKey(
        EstadoTicket,
        on_delete=models.PROTECT,
        related_name="tickets"
    )


    # ======================================================
    # RESPONSABLE PRINCIPAL
    # ======================================================

    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tickets_asignados",
        null=True,
        blank=True
    )


    # ======================================================
    # ESPECIALISTAS DE APOYO
    # ======================================================

    especialistas_apoyo = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tickets_apoyo",
        blank=True
    )


    # ======================================================
    # DIAGNÓSTICO
    # ======================================================

    diagnostico = models.TextField(
        blank=True
    )

    plan_solucion = models.TextField(
        blank=True
    )

    solucion = models.TextField(
        blank=True
    )


    # ======================================================
    # COMPRA
    # ======================================================

    requiere_compra = models.BooleanField(
        default=False
    )

    componente_requerido = models.CharField(
        max_length=200,
        blank=True
    )

    especificaciones_tecnicas = models.TextField(
        blank=True
    )

    costo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    codigo_compra_vinculada = models.CharField(
        max_length=30,
        blank=True
    )


    # ------------------------------------------------------
    # BPMN: "Requiere compra?" -> Especialista solicita con
    # cotización -> Jefe UTIC evalúa viabilidad -> si es
    # viable, se genera el expediente (que luego sigue el
    # subproceso normal de Compra Caja Chica, con su propio
    # visto bueno del Director ya existente en ese módulo).
    # Este campo rastrea esa evaluación previa de viabilidad,
    # separada del estado principal del ticket.
    # ------------------------------------------------------

    ESTADOS_COMPRA_COMPONENTE = [
        ("SOLICITADA", "Solicitada"),
        ("NO_VIABLE", "No viable"),
        ("VIABLE", "Viable"),
    ]

    estado_compra_componente = models.CharField(
        max_length=20,
        choices=ESTADOS_COMPRA_COMPONENTE,
        blank=True
    )

    motivo_no_viable = models.TextField(
        blank=True
    )


    # ======================================================
    # RESULTADOS
    # ======================================================

    resultado_pruebas = models.TextField(
        blank=True
    )

    conformidad_usuario = models.BooleanField(
        null=True,
        blank=True
    )

    observaciones_usuario = models.TextField(
        blank=True
    )

    informe_final = models.TextField(
        blank=True
    )


    # ======================================================
    # FECHAS DEL WORKFLOW
    # ======================================================
    #
    # Estas fechas nos permitirán construir:
    #
    # - Línea de tiempo.
    # - Bitácora.
    # - Indicadores.
    # - Cumplimiento SLA.
    # - Tiempo promedio de resolución.
    #
    # ======================================================

    validado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que UTIC recibió y validó el ticket."
    )

    clasificado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se clasificó prioridad y SLA."
    )

    asignado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se designó al especialista."
    )

    inicio_atencion_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de inicio de la atención técnica."
    )

    pruebas_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se registraron las pruebas técnicas."
    )

    verificado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de verificación del funcionamiento."
    )

    conformidad_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que el solicitante informó conformidad."
    )


    # ======================================================
    # CONTROL Y AUDITORÍA
    # ======================================================

    rework_count = models.PositiveIntegerField(
        default=0
    )

    activo = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    cerrado_en = models.DateTimeField(
        null=True,
        blank=True
    )


    # ======================================================
    # PROPIEDADES ÚTILES
    # ======================================================

    @property
    def tiene_sla(self):

        return (
            self.sla_horas is not None
            and
            self.sla_fecha_limite is not None
        )


    @property
    def esta_cerrado(self):

        if not self.estado_id:
            return False

        return (
            self.estado.codigo
            in [
                "CERRADO",
                "ANULADO",
            ]
        )


    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __str__(self):

        return (
            f"{self.codigo} - "
            f"{self.titulo}"
        )