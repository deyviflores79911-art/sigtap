from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.test import APITestCase

from usuarios.models import Area, Rol, Usuario, UsuarioRol

from compras.models import SolicitudCompra

from .models import CategoriaTicket


class FlujoSoporteCompraTests(APITestCase):
    """Cubre el disparo real del subproceso de Compra Caja Chica
    desde un ticket de Soporte Técnico ("¿Requiere compra?"), con
    la cadena Especialista solicita -> Jefe UTIC evalúa viabilidad
    que exige el BPMN oficial."""

    def setUp(self):
        call_command("cargar_permisos_sigta")

        # Los estados (NUEVO, EN_ANALISIS, ...) y categorías ya se
        # siembran con soporte.0006_seed_estados_categorias /
        # 0008_seed_estado_cerrado_sin_compra.
        self.categoria = CategoriaTicket.objects.get(codigo="HARDWARE")
        self.area = Area.objects.create(codigo="TEST", nombre="Área de prueba")

        self.usuarios = {}
        for codigo in ("SOLICITANTE", "JEFE_UTIC", "ESPECIALISTA"):
            rol = Rol.objects.get(codigo=codigo)
            usuario = Usuario.objects.create_user(
                username=codigo.lower(),
                email=f"{codigo.lower()}@emi.edu.bo",
                nombre_completo=codigo,
                password="Prueba#2026",
            )
            UsuarioRol.objects.create(usuario=usuario, rol=rol, activo=True)
            self.usuarios[codigo] = usuario

    def autenticar(self, codigo):
        self.client.force_authenticate(self.usuarios[codigo])

    def crear_ticket_en_ejecucion(self, titulo, equipo):
        """Lleva un ticket hasta EN_EJECUCION (registrado, validado,
        clasificado, asignado y diagnosticado) para poder probar el
        subflujo de compra de componente."""

        self.autenticar("SOLICITANTE")
        r = self.client.post("/api/soporte/tickets/", {
            "titulo": titulo,
            "descripcion": f"{titulo} - descripción de prueba.",
            "area": self.area.id,
            "ubicacion": "Laboratorio 2",
            "equipo_afectado": equipo,
            "categoria": self.categoria.id,
            "evidencia_archivo": SimpleUploadedFile(
                "evidencia.jpg", b"contenido-de-prueba", content_type="image/jpeg"
            ),
        }, format="multipart")
        self.assertEqual(r.status_code, 201, r.data)
        pk = r.data["ticket"]["id"] if "ticket" in r.data else r.data["id"]

        self.autenticar("JEFE_UTIC")
        r = self.client.post(f"/api/soporte/tickets/{pk}/validar-ticket/", {}, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(f"/api/soporte/tickets/{pk}/clasificar-prioridad/", {
            "prioridad": "ALTA",
            "criterio_tecnico": "Afecta clases del laboratorio.",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(f"/api/soporte/tickets/{pk}/designar-revision/", {
            "tecnico_id": self.usuarios["ESPECIALISTA"].id,
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        self.autenticar("ESPECIALISTA")
        r = self.client.post(f"/api/soporte/tickets/{pk}/registrar-diagnostico/", {
            "diagnostico": "Componente dañado, requiere reemplazo.",
            "plan_solucion": "Solicitar el componente y reemplazarlo.",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        return pk

    def test_especialista_solicita_jefe_aprueba_genera_expediente_vinculado(self):
        pk = self.crear_ticket_en_ejecucion("Monitor no enciende", "Monitor Dell")

        # El Especialista asignado solicita el componente con su
        # cotización — todavía no existe ningún expediente de compra.
        self.autenticar("ESPECIALISTA")
        r = self.client.post(f"/api/soporte/tickets/{pk}/solicitar-requerimiento-componente/", {
            "componente_requerido": "Fuente de monitor",
            "especificaciones_tecnicas": "Fuente 19V 2A",
            "costo_estimado": "250.00",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["ticket"]["estado_codigo"], "EN_EJECUCION")
        self.assertFalse(r.data["ticket"]["codigo_compra_vinculada"])

        # Mientras la viabilidad no se evalúe, no se puede reparar.
        r = self.client.post(f"/api/soporte/tickets/{pk}/registrar-intervencion/", {
            "solucion": "Se reemplazó la fuente.",
        }, format="json")
        self.assertEqual(r.status_code, 409, r.data)

        # Jefe de UTIC evalúa la viabilidad: al aprobarla, recién
        # ahí se genera el expediente real y vinculado en Compras.
        self.autenticar("JEFE_UTIC")
        r = self.client.post(f"/api/soporte/tickets/{pk}/evaluar-viabilidad-compra/", {
            "viable": True,
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        codigo_compra = r.data["ticket"]["codigo_compra_vinculada"]
        self.assertTrue(codigo_compra)

        solicitud = SolicitudCompra.objects.get(codigo=codigo_compra)
        self.assertEqual(solicitud.origen_modulo, "SOPORTE")
        self.assertEqual(solicitud.ticket_soporte_id, pk)
        self.assertEqual(solicitud.solicitante_id, self.usuarios["ESPECIALISTA"].id)

        # No se puede duplicar la solicitud de compra para el
        # mismo ticket.
        self.autenticar("ESPECIALISTA")
        r = self.client.post(f"/api/soporte/tickets/{pk}/solicitar-requerimiento-componente/", {
            "componente_requerido": "Otro componente",
        }, format="json")
        self.assertEqual(r.status_code, 409, r.data)

        # Con la compra ya autorizada, el Especialista puede reparar.
        self.autenticar("ESPECIALISTA")
        r = self.client.post(f"/api/soporte/tickets/{pk}/registrar-intervencion/", {
            "solucion": "Se reemplazó la fuente.",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

    def test_jefe_utic_marca_no_viable_cierra_ticket_sin_compra(self):
        pk = self.crear_ticket_en_ejecucion("Necesita GPU de alta gama", "PC laboratorio")

        self.autenticar("ESPECIALISTA")
        r = self.client.post(f"/api/soporte/tickets/{pk}/solicitar-requerimiento-componente/", {
            "componente_requerido": "GPU de alta gama",
            "costo_estimado": "9999.00",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        self.autenticar("JEFE_UTIC")
        r = self.client.post(f"/api/soporte/tickets/{pk}/evaluar-viabilidad-compra/", {
            "viable": False,
            "motivo_no_viable": "Excede el presupuesto de caja chica.",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["ticket"]["estado_codigo"], "CERRADO_SIN_COMPRA")
        self.assertFalse(r.data["ticket"]["activo"])
        self.assertFalse(SolicitudCompra.objects.filter(ticket_soporte_id=pk).exists())

    def test_solicitante_no_puede_solicitar_componente(self):
        pk = self.crear_ticket_en_ejecucion("Teclado dañado", "Teclado Logitech")

        self.autenticar("SOLICITANTE")
        r = self.client.post(f"/api/soporte/tickets/{pk}/solicitar-requerimiento-componente/", {
            "componente_requerido": "Teclado nuevo",
        }, format="json")
        self.assertEqual(r.status_code, 403, r.data)

    def test_especialista_no_puede_evaluar_viabilidad(self):
        pk = self.crear_ticket_en_ejecucion("Mouse dañado", "Mouse Logitech")

        self.autenticar("ESPECIALISTA")
        r = self.client.post(f"/api/soporte/tickets/{pk}/solicitar-requerimiento-componente/", {
            "componente_requerido": "Mouse nuevo",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(f"/api/soporte/tickets/{pk}/evaluar-viabilidad-compra/", {
            "viable": True,
        }, format="json")
        self.assertEqual(r.status_code, 403, r.data)
