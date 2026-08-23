from django.conf import settings
from django.db import models

from usuarios.models import Area


class SolicitudCompra(models.Model):

    ESTADOS = [
        ("NUEVO", "Nuevo"),
        ("EN_COTIZACION", "En cotización"),
        ("EN_APROBACION", "En aprobación"),
        ("APROBADO", "Aprobado"),
        ("ORDEN_EMITIDA", "Orden emitida"),
        ("EN_TRANSITO", "En tránsito"),
        ("RECIBIDO", "Recibido"),
        ("EN_VERIFICACION", "En verificación"),
        ("CERRADO", "Cerrado"),
        ("RECHAZADO", "Rechazado"),
        ("ANULADO", "Anulado"),
    ]

    TIPOS = [
        ("BIEN", "Bien"),
        ("SERVICIO", "Servicio"),
        ("ACTIVO_FIJO", "Activo fijo"),
        ("COMPONENTE", "Componente"),
    ]

    VIAS = [
        ("PENDIENTE", "Pendiente de evaluación"),
        ("CAJA_CHICA", "Caja Chica"),
        ("FINANZAS", "Finanzas"),
    ]

    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    titulo = models.CharField(
        max_length=200
    )

    descripcion = models.TextField()

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="compras_solicitadas"
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="solicitudes_compra"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    cantidad = models.PositiveIntegerField(
        default=1
    )

    especificaciones = models.TextField()

    justificacion = models.TextField()

    centro_costo = models.CharField(
        max_length=100,
        blank=True
    )

    monto_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    via_adquisicion = models.CharField(
        max_length=20,
        choices=VIAS,
        default="PENDIENTE"
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="NUEVO"
    )

    ticket_soporte_vinculado = models.CharField(
        max_length=30,
        blank=True
    )

    observaciones = models.TextField(
        blank=True
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

    def save(self, *args, **kwargs):

        # Regla EMI utilizada para Caja Chica.
        if self.monto_estimado is not None:

            if self.monto_estimado <= 1500:
                self.via_adquisicion = "CAJA_CHICA"

            else:
                self.via_adquisicion = "FINANZAS"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"