from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.test import APITestCase

from usuarios.models import Area, Rol, Usuario, UsuarioRol

from compras.models import SolicitudCompra

class FlujoMantenimientoTests(APITestCase):
    """Cubre el BPMN de Mantenimiento de punta a punta,
    incluyendo el disparo real del subproceso de Compra
    Caja Chica cuando no hay producto en almacén."""

    def setUp(self):
        call_command("cargar_permisos_sigta")

        # Los estados (RECIBIDO, DERIVADO, ...) ya se siembran
        # con la migración de datos mantenimiento.0002_seed_estados.

        self.area = Area.objects.create(codigo="TEST", nombre="Área de prueba")

        self.usuarios = {}
        for codigo in (
            "SOLICITANTE",
            "SERVICIOS_GENERALES",
            "AUXILIAR_SERVICIOS_GENERALES",
            "ENCARGADO_COMPRAS_ALMACEN",
            "DIRECTOR",
        ):
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

    def test_flujo_completo_con_derivacion_a_compras(self):
        # 1. Unidad Solicitante registra el requerimiento.
        self.autenticar("SOLICITANTE")
        respuesta = self.client.post("/api/mantenimiento/requerimientos/", {
            "titulo": "Impresora no enciende",
            "descripcion": "La impresora del área no enciende.",
            "area": self.area.id,
            "ubicacion": "Oficina 3",
            "tipo": "CORRECTIVO",
            "evidencia_archivo": SimpleUploadedFile(
                "evidencia.jpg", b"contenido-de-prueba", content_type="image/jpeg"
            ),
        }, format="multipart")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        pk = respuesta.data["requerimiento"]["id"]
        self.assertEqual(respuesta.data["requerimiento"]["estado_codigo"], "RECIBIDO")

        # 2. Servicios Generales deriva a su auxiliar.
        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/derivar-auxiliar/",
            {"auxiliar_id": self.usuarios["AUXILIAR_SERVICIOS_GENERALES"].id},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "DERIVADO", r.data)

        # 3. Auxiliar: requiere reposición de almacén.
        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/verificar-reposicion/",
            {
                "requiere_reposicion": True,
                "producto_requerido": "Fuente de poder",
                "cantidad_requerida": 1,
                "especificacion_producto": "Fuente 220V para impresora HP",
            },
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "REVISION_ALMACEN", r.data)

        # 4. Encargado de Compras y Almacén: no hay producto ->
        # debe crearse automáticamente un expediente real en Compras.
        self.autenticar("ENCARGADO_COMPRAS_ALMACEN")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/reportar-existencia/",
            {"producto_disponible": False, "observacion_almacen": "Sin stock"},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "EN_ESPERA_COMPRA", r.data)

        codigo_compra = r.data["requerimiento"]["codigo_compra_vinculada"]
        self.assertTrue(codigo_compra)

        solicitud = SolicitudCompra.objects.get(codigo=codigo_compra)
        self.assertEqual(solicitud.origen_modulo, "MANTENIMIENTO")
        self.assertEqual(solicitud.requerimiento_mantenimiento_id, pk)
        self.assertEqual(solicitud.solicitante_id, self.usuarios["AUXILIAR_SERVICIOS_GENERALES"].id)
        self.assertEqual(solicitud.estado, "CREADO_PENDIENTE_DAF")

        # 5. Todavía no se puede confirmar la compra: el
        # expediente de Compras aún no fue cerrado.
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-compra/",
            {}, format="json",
        )
        self.assertEqual(r.status_code, 409, r.data)

        # Se simula el cierre del expediente en Compras (el ciclo
        # completo DAF->Tesorería->Director->Almacén ya se cubre
        # en compras.tests.FlujoCajaChicaTests).
        solicitud.estado = "CERRADO_ARCHIVADO"
        solicitud.cerrado_inmutable = True
        solicitud.save(update_fields=["estado", "cerrado_inmutable"])

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-compra/",
            {}, format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "EN_MANTENIMIENTO", r.data)
        self.assertEqual(r.data["requerimiento"]["codigo_compra_vinculada"], solicitud.codigo)

        # 6. Auxiliar realiza el mantenimiento y registra el informe.
        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/realizar-mantenimiento/",
            {"trabajo_realizado": "Se reemplazó la fuente de poder."},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-informe/",
            {"informe_trabajo": "Impresora operativa nuevamente."},
            format="multipart",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "INFORME_REGISTRADO", r.data)

        # 7. Servicios Generales recibe el expediente y lo archiva.
        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/finalizar/",
            {}, format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "FINALIZADO", r.data)

        # 8. Director: solo lectura de lo finalizado + reporte mensual.
        self.autenticar("DIRECTOR")
        r = self.client.get("/api/mantenimiento/requerimientos/")
        self.assertEqual(r.status_code, 200, r.data)
        codigos = [item["id"] for item in r.data]
        self.assertIn(pk, codigos)

        r = self.client.get("/api/mantenimiento/requerimientos/reporte-mensual/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertGreaterEqual(r.data["total_finalizados"], 1)

    def test_registrar_compra_sin_solicitud_vinculada(self):
        self.autenticar("SOLICITANTE")
        respuesta = self.client.post("/api/mantenimiento/requerimientos/", {
            "titulo": "Aire acondicionado con fuga",
            "descripcion": "Fuga de agua en el equipo de aire.",
            "area": self.area.id,
            "ubicacion": "Sala de servidores",
            "tipo": "CORRECTIVO",
            "evidencia_archivo": SimpleUploadedFile(
                "evidencia.jpg", b"contenido-de-prueba", content_type="image/jpeg"
            ),
        }, format="multipart")
        pk = respuesta.data["requerimiento"]["id"]

        self.autenticar("SERVICIOS_GENERALES")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/derivar-auxiliar/",
            {"auxiliar_id": self.usuarios["AUXILIAR_SERVICIOS_GENERALES"].id},
            format="json",
        )

        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/verificar-reposicion/",
            {"requiere_reposicion": False},
            format="json",
        )

        # El requerimiento nunca pasó por EN_ESPERA_COMPRA, por lo
        # que registrar-compra debe rechazar por estado, no por
        # falta de código a mano.
        self.autenticar("ENCARGADO_COMPRAS_ALMACEN")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-compra/",
            {}, format="json",
        )
        self.assertEqual(r.status_code, 400, r.data)
