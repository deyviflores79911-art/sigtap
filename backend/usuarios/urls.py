from django.urls import (
    path,
    include,
)

from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    AreaViewSet,
    RolViewSet,
    UsuarioViewSet,
    UsuarioRolViewSet,
    PermisoViewSet,
    RolPermisoViewSet,
    login_view,
    mi_contexto,
    cambiar_password_obligatorio,
)


# ==========================================================
# ROUTER
# ==========================================================

router = DefaultRouter()


# ==========================================================
# ÁREAS
# ==========================================================

router.register(
    r"areas",
    AreaViewSet,
    basename="area"
)


# ==========================================================
# ROLES
# ==========================================================

router.register(
    r"roles",
    RolViewSet,
    basename="rol"
)


# ==========================================================
# PERMISOS
# ==========================================================

router.register(
    r"permisos",
    PermisoViewSet,
    basename="permiso"
)


# ==========================================================
# ROL - PERMISO
# ==========================================================

router.register(
    r"rol-permisos",
    RolPermisoViewSet,
    basename="rol-permiso"
)


# ==========================================================
# USUARIOS
# ==========================================================

router.register(
    r"usuarios",
    UsuarioViewSet,
    basename="usuario"
)


# ==========================================================
# USUARIO - ROL
# ==========================================================

router.register(
    r"usuario-roles",
    UsuarioRolViewSet,
    basename="usuario-rol"
)


# ==========================================================
# URLS ESPECIALES
# ==========================================================

urlpatterns = [

    # ------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------

    path(
        "login/",
        login_view,
        name="login"
    ),


    # ------------------------------------------------------
    # CONTEXTO DEL USUARIO AUTENTICADO
    # ------------------------------------------------------
    #
    # Devuelve:
    #
    # usuario
    # roles
    # áreas
    # permisos
    #
    # GET /api/usuarios/mi-contexto/
    #
    # ------------------------------------------------------

    path(
        "mi-contexto/",
        mi_contexto,
        name="mi-contexto"
    ),


    # ------------------------------------------------------
    # CAMBIO OBLIGATORIO DE CONTRASEÑA
    # ------------------------------------------------------

    path(
        "cambiar-password-obligatorio/",
        cambiar_password_obligatorio,
        name="cambiar-password-obligatorio"
    ),


    # ------------------------------------------------------
    # ROUTER DRF
    # ------------------------------------------------------

    path(
        "",
        include(
            router.urls
        )
    ),
]