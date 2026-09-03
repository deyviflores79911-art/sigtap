from django.core.management.base import BaseCommand
from django.db import transaction

from usuarios.models import Rol, Usuario, UsuarioRol


class Command(BaseCommand):

    help = (
        "Crea/actualiza las cuentas de prueba de SIGTA para "
        "los roles que todavía no tenían credenciales en "
        "CREDENCIALES_PRUEBA.md, y una cuenta nueva pendiente "
        "de cambio de contraseña para probar HU-01/HU-02."
    )

    USUARIOS = [
        {
            "email": "superuser@emi.edu.bo",
            "nombre_completo": "Admin (superuser)",
            "rol": "SUPERUSER",
            "password": "SIGTA_Superuser#2026!",
            "must_change_password": False,
        },
        {
            "email": "admin@emi.edu.bo",
            "nombre_completo": "Director",
            "rol": "ADMIN",
            "password": "SIGTA_Admin#2026!",
            "must_change_password": False,
        },
        {
            "email": "jefe.utic@emi.edu.bo",
            "nombre_completo": "Jefe UTIC",
            "rol": "JEFE_UTIC",
            "password": "SIGTA_JefeUTIC#2026!",
            "must_change_password": False,
        },
        {
            "email": "servicios.generales@emi.edu.bo",
            "nombre_completo": "Jefe Mantenimiento",
            "rol": "SERVICIOS_GENERALES",
            "password": "SIGTA_ServiciosGrales#2026!",
            "must_change_password": False,
        },
        {
            "email": "daf@emi.edu.bo",
            "nombre_completo": "Técnico de la DAF",
            "rol": "DAF",
            "password": "SIGTA_DAF#2026!",
            "must_change_password": False,
        },
        {
            "email": "almacen@emi.edu.bo",
            "nombre_completo": "Técnico de Almacén y Compras",
            "rol": "ENCARGADO_COMPRAS_ALMACEN",
            "password": "SIGTA_Almacen#2026!",
            "must_change_password": False,
        },
        {
            "email": "tesoreria@emi.edu.bo",
            "nombre_completo": "Técnico de Tesorería",
            "rol": "TESORERIA",
            "password": "SIGTA_Tesoreria#2026!",
            "must_change_password": False,
        },
        {
            "email": "especialista@emi.edu.bo",
            "nombre_completo": "Técnico de Soporte Técnico",
            "rol": "ESPECIALISTA",
            "password": "SIGTA_Especialista#2026!",
            "must_change_password": False,
        },
        {
            "email": "auxiliar.sg@emi.edu.bo",
            "nombre_completo": "Técnico de Mantenimiento",
            "rol": "AUXILIAR_SERVICIOS_GENERALES",
            "password": "SIGTA_AuxiliarSG#2026!",
            "must_change_password": False,
        },
        {
            "email": "solicitante@emi.edu.bo",
            "nombre_completo": "Usuario",
            "rol": "SOLICITANTE",
            "password": "SIGTA_Usuario#2026!",
            "must_change_password": False,
        },
        {
            "email": "nuevo.ingreso@emi.edu.bo",
            "nombre_completo": "Usuario Recien Creado",
            "rol": "SOLICITANTE",
            "password": "SIGTA_Temporal#2026!",
            "must_change_password": True,
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        for datos in self.USUARIOS:

            rol = Rol.objects.get(codigo=datos["rol"])

            usuario, creado = Usuario.objects.get_or_create(
                email=datos["email"],
                defaults={
                    "username": datos["email"].split("@")[0],
                    "nombre_completo": datos["nombre_completo"],
                    "is_active": True,
                },
            )

            usuario.set_password(datos["password"])
            usuario.nombre_completo = datos["nombre_completo"]
            usuario.must_change_password = datos["must_change_password"]
            usuario.is_active = True
            usuario.failed_attempts = 0
            usuario.locked_until = None
            usuario.save()

            # El esqueleto oficial define un único perfil por cuenta.
            UsuarioRol.objects.filter(
                usuario=usuario,
                activo=True,
            ).exclude(rol=rol).update(activo=False)

            asignacion = UsuarioRol.objects.filter(
                usuario=usuario,
                rol=rol,
                area=None,
            ).first()
            if asignacion:
                if not asignacion.activo:
                    asignacion.activo = True
                    asignacion.save(update_fields=["activo"])
            else:
                UsuarioRol.objects.create(
                    usuario=usuario,
                    rol=rol,
                    area=None,
                    activo=True,
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Creado' if creado else 'Actualizado'}: "
                    f"{usuario.email} ({datos['rol']})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Cuentas de prueba listas."))
