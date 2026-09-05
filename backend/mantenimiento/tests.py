from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.test import APITestCase

from usuarios.models import Area, Rol, Usuario, UsuarioRol

from compras.models import SolicitudCompra

from .models import RequerimientoMantenimiento


class FlujoMantenimientoTests(APITestCase):
    """Recorre el BPMN de Mantenimiento: registro, validación,
    clasificación, designación, diagnóstico, compra, reparación,
    pruebas, verificación, conformidad e informe final."""

    def setUp(self):
        call_command("cargar_permisos_sigta")

        self.area = Area.objects.create(codigo="TEST", nombre="Área de prueba")
        self.usuarios = {}

        for codigo in (
            "SOLICITANTE",
            "SERVICIOS_GENERALES",
            "AUXILIAR_SERVICIOS_GENERALES",
            "ENCARGADO_COMPRAS_ALMACEN",
            "DAF",
            "TESORERIA",
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

    def autenticar(self, rol):
        self.client.force_authenticate(self.usuarios[rol])

    def imagen(self):
        return SimpleUploadedFile("evidencia.jpg", b"\xff\xd8\xff", content_type="image/jpeg")

    def archivo(self, nombre="archivo.pdf"):
        return SimpleUploadedFile(nombre, b"contenido de prueba", content_type="application/pdf")

    def registrar(self, titulo="Aire acondicionado sin enfriar"):
        self.autenticar("SOLICITANTE")
        r = self.client.post("/api/mantenimiento/requerimientos/", {
            "titulo": titulo,
            "descripcion": "No enfría desde ayer",
            "ubicacion": "Aula C0-07",
            "evidencia_archivo": self.imagen(),
        }, format="multipart")
        self.assertEqual(r.status_code, 201, r.data)
        return r.data["requerimiento"]["id"]

    def test_ticket_invalido_no_procede(self):
        pk = self.registrar("Solicitud incompleta")

        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/validar-ticket/",
            {"es_valido": False, "motivo_rechazo": "No indica el equipo afectado."},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "RECHAZADO")

    def test_solicitante_registra_campos_comunes_sin_adjunto(self):
        self.autenticar("SOLICITANTE")
        r = self.client.post("/api/mantenimiento/requerimientos/", {
            "titulo": "Luminaria averiada",
            "descripcion": "La luminaria parpadea durante la jornada.",
            "area": self.area.id,
            "ubicacion": "Aula C0-07",
            "referencia_ubicacion": "Bloque C, planta baja",
            "equipo_afectado": "Luminaria del aula",
            "tipo": "CORRECTIVO",
        }, format="multipart")

        self.assertEqual(r.status_code, 201, r.data)
        creado = r.data["requerimiento"]
        self.assertEqual(creado["solicitante"], self.usuarios["SOLICITANTE"].id)
        self.assertEqual(creado["estado_codigo"], "RECIBIDO")
        self.assertEqual(creado["referencia_ubicacion"], "Bloque C, planta baja")
        self.assertEqual(creado["equipo_afectado"], "Luminaria del aula")

    def test_flujo_completo_sin_compra(self):
        pk = self.registrar()

        # Jefatura: validar, clasificar y designar.
        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(f"/api/mantenimiento/requerimientos/{pk}/validar-ticket/", {"es_valido": True}, format="json")
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "VALIDADO", r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/clasificar-prioridad/",
            {"prioridad": "ALTA", "criterio_prioridad": "Aula en uso permanente."},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/designar-revision/",
            {"tecnico_id": self.usuarios["AUXILIAR_SERVICIOS_GENERALES"].id},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "DERIVADO", r.data)

        # Técnico: diagnóstico, reparación y pruebas.
        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-diagnostico/",
            {"diagnostico": "Filtro saturado", "plan_solucion": "Limpieza profunda"},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "EN_MANTENIMIENTO", r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/realizar-mantenimiento/",
            {"trabajo_realizado": "Se limpió el filtro y se recargó gas."},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/pruebas-tecnicas/",
            {"resultado_pruebas": "Enfría correctamente."},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-informe/",
            {"informe_trabajo": "Mantenimiento correctivo concluido."},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "INFORME_REGISTRADO", r.data)

        # Jefatura: verificación con ciclo de retorno.
        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/verificar-funcionamiento/",
            {"problema_resuelto": False},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "EN_MANTENIMIENTO", r.data)
        self.assertEqual(r.data["requerimiento"]["rework_count"], 1)

        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/pruebas-tecnicas/",
            {"resultado_pruebas": "Segunda prueba conforme."}, format="json",
        )
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-informe/",
            {"informe_trabajo": "Se sustituyó el termostato."}, format="json",
        )

        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/verificar-funcionamiento/",
            {"problema_resuelto": True},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        r = self.client.post(f"/api/mantenimiento/requerimientos/{pk}/informar-conformidad/", {}, format="json")
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "CONFORMIDAD_INFORMADA", r.data)

        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/elaborar-informe-final/",
            {"informe_final": "Informe consolidado del mantenimiento."},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertTrue(r.data["requerimiento"]["informe_elevado_en"])

        # Dirección: recibe el informe y el proceso termina.
        self.autenticar("DIRECTOR")
        r = self.client.post(f"/api/mantenimiento/requerimientos/{pk}/recibir-informe/", {}, format="json")
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "FINALIZADO", r.data)
        self.assertTrue(r.data["requerimiento"]["proceso_finalizado_en"])

    def test_requerimiento_con_compra_no_viable(self):
        pk = self.registrar("Requiere compresor nuevo")

        self.autenticar("SERVICIOS_GENERALES")
        self.client.post(f"/api/mantenimiento/requerimientos/{pk}/validar-ticket/", {"es_valido": True}, format="json")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/clasificar-prioridad/",
            {"prioridad": "MEDIA", "criterio_prioridad": "Puede esperar."}, format="json",
        )
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/designar-revision/",
            {"tecnico_id": self.usuarios["AUXILIAR_SERVICIOS_GENERALES"].id}, format="json",
        )

        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-diagnostico/",
            {"diagnostico": "Compresor quemado", "plan_solucion": "Reemplazar"}, format="json",
        )
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/solicitar-requerimiento/",
            {
                "producto_requerido": "Compresor 12000 BTU",
                "especificacion_producto": "Marca X",
                "cantidad_requerida": 1,
                "costo_estimado": "4500",
            },
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "EN_ESPERA_COMPRA", r.data)

        # El técnico no puede continuar mientras la compra esté en curso.
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/realizar-mantenimiento/",
            {"trabajo_realizado": "x"}, format="json",
        )
        self.assertIn(r.status_code, (400, 409), r.data)

        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/evaluar-viabilidad-compra/",
            {"viable": False, "motivo_no_viable": "Excede el presupuesto disponible."},
            format="json",
        )
        self.assertEqual(r.data["requerimiento"]["estado_codigo"], "CERRADO_SIN_COMPRA", r.data)

    def test_requerimiento_con_compra_viable_genera_expediente(self):
        pk = self.registrar("Requiere repuesto")

        self.autenticar("SERVICIOS_GENERALES")
        self.client.post(f"/api/mantenimiento/requerimientos/{pk}/validar-ticket/", {"es_valido": True}, format="json")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/clasificar-prioridad/",
            {"prioridad": "ALTA", "criterio_prioridad": "Urgente."}, format="json",
        )
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/designar-revision/",
            {"tecnico_id": self.usuarios["AUXILIAR_SERVICIOS_GENERALES"].id}, format="json",
        )

        self.autenticar("AUXILIAR_SERVICIOS_GENERALES")
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/registrar-diagnostico/",
            {"diagnostico": "Falta repuesto", "plan_solucion": "Comprar"}, format="json",
        )
        self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/solicitar-requerimiento/",
            {"producto_requerido": "Ventilador", "cantidad_requerida": 1, "costo_estimado": "300"},
            format="json",
        )

        self.autenticar("SERVICIOS_GENERALES")
        r = self.client.post(
            f"/api/mantenimiento/requerimientos/{pk}/evaluar-viabilidad-compra/",
            {"viable": True}, format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)

        codigo = r.data["requerimiento"]["codigo_compra_vinculada"]
        self.assertTrue(codigo)

        solicitud = SolicitudCompra.objects.get(codigo=codigo)
        self.assertEqual(solicitud.origen_modulo, "MANTENIMIENTO")
        self.assertEqual(solicitud.requerimiento_mantenimiento_id, pk)
        self.assertEqual(solicitud.estado, "CREADO_PENDIENTE_DAF")

        requerimiento = RequerimientoMantenimiento.objects.get(pk=pk)
        self.assertEqual(requerimiento.estado_compra_componente, "VIABLE")
