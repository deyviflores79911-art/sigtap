from django.conf import settings
from django.db import models

from usuarios.models import Area


class SolicitudCompra(models.Model):

    ESTADOS = [
        ("CREADO_PENDIENTE_DAF", "Creado - pendiente DAF"),
        ("EVALUADO_PENDIENTE_CERTIFICACION", "Evaluado - pendiente de certificación"),
        ("CERTIFICADO_PENDIENTE_VERIFICACION", "Certificado - pendiente de verificación"),
        ("VERIFICADO_PENDIENTE_AUTORIZACION", "Verificado - pendiente de autorización"),
        ("APROBADO_PARA_DESEMBOLSO", "Aprobado para desembolso"),
        ("FONDOS_DESEMBOLSADOS", "Fondos desembolsados"),
        ("COMPRA_REGISTRADA", "Compra realizada - pendiente de entrega"),
        ("COMPRADO_Y_ENTREGADO", "Comprado y entregado"),
        ("DESCARGO_PENDIENTE_LIQUIDACION", "Descargo pendiente de liquidación"),
        ("CERRADO_ARCHIVADO", "Cerrado y archivado"),
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
        max_length=50,
        choices=ESTADOS,
        default="CREADO_PENDIENTE_DAF"
    )

    ticket_soporte_vinculado = models.CharField(
        max_length=30,
        blank=True
    )

    observaciones = models.TextField(
        blank=True
    )

    informe = models.FileField(upload_to="compras/expedientes/informes/", null=True, blank=True)
    poa = models.FileField(upload_to="compras/expedientes/poa/", null=True, blank=True)
    pedido = models.FileField(upload_to="compras/expedientes/pedidos/", null=True, blank=True)
    proforma = models.FileField(upload_to="compras/expedientes/proformas/", null=True, blank=True)
    certificacion_presupuestaria = models.FileField(upload_to="compras/certificaciones/", null=True, blank=True)
    factura = models.FileField(upload_to="compras/descargos/facturas/", null=True, blank=True)
    acta_conformidad = models.FileField(upload_to="compras/descargos/actas/", null=True, blank=True)
    fotograma = models.FileField(upload_to="compras/descargos/fotogramas/", null=True, blank=True)

    motivo_rechazo = models.TextField(blank=True)
    monto_desembolsado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    responsable_adquisicion = models.CharField(max_length=150, blank=True)
    monto_real = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    proveedor = models.CharField(max_length=180, blank=True)
    cerrado_inmutable = models.BooleanField(default=False)

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
