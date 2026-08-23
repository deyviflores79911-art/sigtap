from django.conf import settings
from django.db import models

from usuarios.models import Area


# ==========================================================
# ESTADOS DEL PROCESO DE MANTENIMIENTO
# ==========================================================

class EstadoMantenimiento(models.Model):

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
# REQUERIMIENTO DE MANTENIMIENTO
# ==========================================================

class RequerimientoMantenimiento(models.Model):

    # ======================================================
    # TIPOS
    # ======================================================

    TIPOS_MANTENIMIENTO = [
        (
            "PREVENTIVO",
            "Preventivo"
        ),
        (
            "CORRECTIVO",
            "Correctivo"
        ),
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
        related_name="mantenimientos_solicitados"
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="requerimientos_mantenimiento"
    )

    ubicacion = models.CharField(
        max_length=200
    )


    # ======================================================
    # CLASIFICACIÓN
    # ======================================================

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_MANTENIMIENTO
    )


    # ======================================================
    # EVIDENCIA DEL SOLICITANTE
    # ======================================================

    evidencia = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Descripción adicional o referencia "
            "de la evidencia."
        )
    )

    evidencia_archivo = models.FileField(
        upload_to="mantenimiento/evidencias/%Y/%m/",
        blank=True,
        null=True,
        help_text=(
            "Imagen o documento cargado "
            "como evidencia."
        )
    )


    # ======================================================
    # ESTADO DEL PROCESO
    # ======================================================

    estado = models.ForeignKey(
        EstadoMantenimiento,
        on_delete=models.PROTECT,
        related_name="requerimientos"
    )


    # ======================================================
    # SERVICIOS GENERALES
    # ======================================================
    #
    # BPMN:
    # Servicios Generales recibe el requerimiento
    # y lo deriva a su auxiliar.
    #
    # ======================================================

    responsable_servicios_generales = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="mantenimientos_servicios_generales",
        null=True,
        blank=True
    )

    auxiliar_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="mantenimientos_asignados",
        null=True,
        blank=True
    )


    # ======================================================
    # REPOSICIÓN DE ALMACÉN
    # ======================================================
    #
    # BPMN:
    #
    # ¿Requiere reposición de almacén?
    #
    # SI  -> verificar existencia.
    # NO  -> realizar mantenimiento.
    #
    # ======================================================

    requiere_reposicion = models.BooleanField(
        null=True,
        blank=True
    )

    producto_requerido = models.CharField(
        max_length=200,
        blank=True
    )

    cantidad_requerida = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    especificacion_producto = models.TextField(
        blank=True
    )


    # ======================================================
    # EXISTENCIA EN ALMACÉN
    # ======================================================

    producto_disponible_almacen = models.BooleanField(
        null=True,
        blank=True
    )

    producto_entregado = models.BooleanField(
        default=False
    )

    observacion_almacen = models.TextField(
        blank=True
    )


    # ======================================================
    # COMPRA CAJA CHICA
    # ======================================================
    #
    # Si NO existe producto:
    # se deriva al subproceso de Compra Caja Chica.
    #
    # ======================================================

    derivado_compra = models.BooleanField(
        default=False
    )

    codigo_compra_vinculada = models.CharField(
        max_length=30,
        blank=True
    )

    compra_completada = models.BooleanField(
        default=False
    )


    # ======================================================
    # EJECUCIÓN DEL MANTENIMIENTO
    # ======================================================

    trabajo_realizado = models.TextField(
        blank=True
    )

    observaciones_trabajo = models.TextField(
        blank=True
    )


    # ======================================================
    # INFORME Y FOTOGRAFÍA
    # ======================================================
    #
    # BPMN:
    # "Realiza un informe, fotograma del trabajo realizado"
    #
    # ======================================================

    informe_trabajo = models.TextField(
        blank=True
    )

    fotografia_trabajo = models.FileField(
        upload_to="mantenimiento/trabajos/%Y/%m/",
        blank=True,
        null=True,
        help_text=(
            "Fotografía del trabajo "
            "de mantenimiento realizado."
        )
    )


    # ======================================================
    # CONTROL DE FECHAS DEL PROCESO
    # ======================================================

    recibido_en = models.DateTimeField(
        null=True,
        blank=True
    )

    derivado_en = models.DateTimeField(
        null=True,
        blank=True
    )

    revision_almacen_en = models.DateTimeField(
        null=True,
        blank=True
    )

    inicio_mantenimiento_en = models.DateTimeField(
        null=True,
        blank=True
    )

    informe_registrado_en = models.DateTimeField(
        null=True,
        blank=True
    )

    finalizado_en = models.DateTimeField(
        null=True,
        blank=True
    )


    # ======================================================
    # CONTROL GENERAL
    # ======================================================

    activo = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )


    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __str__(self):

        return (
            f"{self.codigo} - "
            f"{self.titulo}"
        )