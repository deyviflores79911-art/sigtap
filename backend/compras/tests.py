from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from usuarios.models import Area, Rol, Usuario, UsuarioRol


class FlujoCajaChicaTests(APITestCase):
    def setUp(self):
        self.area = Area.objects.create(codigo="TEST", nombre="Área de prueba")
        self.usuarios = {}
        for codigo in ("SOLICITANTE", "DAF", "TESORERIA", "DIRECTOR", "ENCARGADO_COMPRAS_ALMACEN"):
            rol = Rol.objects.create(codigo=codigo, nombre=codigo, activo=True)
            usuario = Usuario.objects.create_user(
                username=codigo.lower(), email=f"{codigo.lower()}@emi.edu.bo",
                nombre_completo=codigo, password="Prueba#2026",
            )
            UsuarioRol.objects.create(usuario=usuario, rol=rol, activo=True)
            self.usuarios[codigo] = usuario

    def archivo(self, nombre="archivo.pdf"):
        return SimpleUploadedFile(nombre, b"contenido de prueba", content_type="application/pdf")

    def autenticar(self, rol):
        self.client.force_authenticate(self.usuarios[rol])

    def test_ciclo_completo_caja_chica(self):
        self.autenticar("SOLICITANTE")
        respuesta = self.client.post("/api/compras/solicitudes/", {
            "titulo": "Compra de prueba", "descripcion": "Prueba integral",
            "area": self.area.id, "tipo": "BIEN", "cantidad": 1,
            "especificaciones": "Especificaciones", "justificacion": "Necesario",
            "monto_estimado": "100.00", "informe": self.archivo("informe.pdf"),
            "poa": self.archivo("poa.pdf"), "pedido": self.archivo("pedido.pdf"),
            "proforma": self.archivo("proforma.pdf"),
        }, format="multipart")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        pk = respuesta.data["id"]
        self.assertEqual(respuesta.data["estado"], "CREADO_PENDIENTE_DAF")

        self.autenticar("DAF")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/evaluar-daf/", {"califica": True}, format="json")
        self.assertEqual(r.data["estado"], "EVALUADO_PENDIENTE_CERTIFICACION")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/certificar-daf/", {"certificacion_presupuestaria": self.archivo("certificacion.pdf")}, format="multipart")
        self.assertEqual(r.data["estado"], "CERTIFICADO_PENDIENTE_VERIFICACION")

        self.autenticar("TESORERIA")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/verificar-tesoreria/", {}, format="json")
        self.assertEqual(r.data["estado"], "VERIFICADO_PENDIENTE_AUTORIZACION")

        self.autenticar("DIRECTOR")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/visto-bueno-director/", {}, format="json")
        self.assertEqual(r.data["estado"], "APROBADO_PARA_DESEMBOLSO")

        self.autenticar("TESORERIA")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/desembolsar/", {"monto_desembolsado": "100.00", "responsable_adquisicion": "Almacén"}, format="json")
        self.assertEqual(r.data["estado"], "FONDOS_DESEMBOLSADOS")

        self.autenticar("ENCARGADO_COMPRAS_ALMACEN")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/registrar-compra/", {"monto_real": "100.00", "proveedor": "Proveedor"}, format="json")
        self.assertEqual(r.data["estado"], "COMPRA_REGISTRADA")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/registrar-entrega/", {}, format="json")
        self.assertEqual(r.data["estado"], "COMPRADO_Y_ENTREGADO")

        self.autenticar("SOLICITANTE")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/presentar-descargo/", {
            "factura": self.archivo("factura.pdf"), "acta_conformidad": self.archivo("acta.pdf"),
            "fotograma": self.archivo("foto.pdf"),
        }, format="multipart")
        self.assertEqual(r.data["estado"], "DESCARGO_PENDIENTE_LIQUIDACION")

        self.autenticar("TESORERIA")
        r = self.client.post(f"/api/compras/solicitudes/{pk}/cerrar-archivar/", {}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["estado"], "CERRADO_ARCHIVADO")
        self.assertTrue(r.data["cerrado_inmutable"])
