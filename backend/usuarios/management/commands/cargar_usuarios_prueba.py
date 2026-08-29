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
            "nombre_completo": "Superusuario SIGTA",
            "rol": "SUPERUSER",
            "password": "SIGTA_Superuser#2026!",
            "must_change_password": False,
        },
        {
            "email": "servicios.generales@emi.edu.bo",
            "nombre_completo": "Servicios Generales",
            "rol": "SERVICIOS_GENERALES",
            "password": "SIGTA_ServiciosGrales#2026!",
            "must_change_password": False,
        },
        {
            "email": "auxiliar.sg@emi.edu.bo",
            "nombre_completo": "Auxiliar de Servicios Generales",
            "rol": "AUXILIAR_SERVICIOS_GENERALES",
            "password": "SIGTA_AuxiliarSG#2026!",
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
            usuario.must_change_password = datos["must_change_password"]
            usuario.is_active = True
            usuario.failed_attempts = 0
            usuario.locked_until = None
            usuario.save()

            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol,
                area=None,
                defaults={"activo": True},
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Creado' if creado else 'Actualizado'}: "
                    f"{usuario.email} ({datos['rol']})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Cuentas de prueba listas."))
