import {
  createRouter,
  createWebHistory
} from 'vue-router'


/* =========================================================
   AUTENTICACIÓN
========================================================= */

import LoginView
  from '../views/LoginView.vue'

import CambiarPasswordView
  from '../views/CambiarPasswordView.vue'

import RecuperarPasswordView
  from '../views/RecuperarPasswordView.vue'


/* =========================================================
   ADMINISTRADOR - YA EXISTENTES
========================================================= */

import AdminDashboardView
  from '../views/AdminDashboardView.vue'

import AdminUsuariosView
  from '../views/AdminUsuariosView.vue'

import AdminRolesAreasView
  from '../views/AdminRolesAreasView.vue'

import AdminTicketsView
  from '../views/AdminTicketsView.vue'

import AdminBitacoraView
  from '../views/AdminBitacoraView.vue'

import AdminSMTPView
  from '../views/AdminSMTPView.vue'

import AdminPreferenciasView
  from '../views/AdminPreferenciasView.vue'


/* =========================================================
   ADMINISTRADOR - NUEVOS MÓDULOS
========================================================= */

import AdminSoporteView
  from '../views/AdminSoporteView.vue'

import AdminComprasView
  from '../views/AdminComprasView.vue'

import AdminMantenimientoView
  from '../views/AdminMantenimientoView.vue'

import AdminPortalSolicitanteView
  from '../views/AdminPortalSolicitanteView.vue'


/* =========================================================
   SOLICITANTE
========================================================= */

import SolicitanteDashboardView
  from '../views/SolicitanteDashboardView.vue'

import SolicitanteSoporteView
  from '../views/SolicitanteSoporteView.vue'

import MisSolicitudesView
  from '../views/MisSolicitudesView.vue'

import SolicitanteComprasView
  from '../views/SolicitanteComprasView.vue'

import SolicitanteMantenimientoView
  from '../views/SolicitanteMantenimientoView.vue'

import NotificacionesView
  from '../views/NotificacionesView.vue'

import PerfilView
  from '../views/PerfilView.vue'


/* =========================================================
   ROUTER
========================================================= */

const router = createRouter({

  history:
    createWebHistory(
      import.meta.env.BASE_URL
    ),

  routes: [

    /* =====================================================
       GENERAL
    ===================================================== */

    {
      path: '/',
      redirect: '/login',
    },

    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        publica: true,
      },
    },

    {
      path: '/cambiar-contrasena',
      name: 'cambiar-contrasena',
      component: CambiarPasswordView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/recuperar-contrasena',
      name: 'recuperar-contrasena',
      component: RecuperarPasswordView,
      meta: {
        publica: true,
      },
    },


    /* =====================================================
       ADMINISTRADOR
    ===================================================== */

    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       NUEVO KANBAN DE SOPORTE
    ----------------------------------------------------- */

    {
      path: '/admin/soporte',
      name: 'admin-soporte',
      component: AdminSoporteView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       MANTENIMIENTO
    ----------------------------------------------------- */

    {
      path: '/admin/mantenimiento',
      name: 'admin-mantenimiento',
      component: AdminMantenimientoView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       COMPRAS
    ----------------------------------------------------- */

    {
      path: '/admin/compras',
      name: 'admin-compras',
      component: AdminComprasView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       PORTAL SOLICITANTE - VISTA ADMIN
    ----------------------------------------------------- */

    {
      path: '/admin/portal-solicitante',
      name: 'admin-portal-solicitante',
      component: AdminPortalSolicitanteView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       CRUD USUARIOS
    ----------------------------------------------------- */

    {
      path: '/admin/usuarios',
      name: 'admin-usuarios',
      component: AdminUsuariosView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       ROLES Y ÁREAS
    ----------------------------------------------------- */

    {
      path: '/admin/roles-areas',
      name: 'admin-roles-areas',
      component: AdminRolesAreasView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       MANTENEMOS TU PANTALLA ANTERIOR DE TICKETS
    ----------------------------------------------------- */

    {
      path: '/admin/tickets',
      name: 'admin-tickets',
      component: AdminTicketsView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       BITÁCORA
    ----------------------------------------------------- */

    {
      path: '/admin/bitacora',
      name: 'admin-bitacora',
      component: AdminBitacoraView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       SMTP
    ----------------------------------------------------- */

    {
      path: '/admin/smtp',
      name: 'admin-smtp',
      component: AdminSMTPView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* -----------------------------------------------------
       PREFERENCIAS
    ----------------------------------------------------- */

    {
      path: '/admin/preferencias',
      name: 'admin-preferencias',
      component: AdminPreferenciasView,
      meta: {
        requiereAuth: true,
        admin: true,
      },
    },


    /* =====================================================
       SOLICITANTE
    ===================================================== */

    {
      path: '/usuario/dashboard',
      name: 'usuario-dashboard',
      component: SolicitanteDashboardView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/soporte',
      name: 'usuario-soporte',
      component: SolicitanteSoporteView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/mantenimiento',
      name: 'usuario-mantenimiento',
      component: SolicitanteMantenimientoView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/mis-solicitudes',
      name: 'usuario-mis-solicitudes',
      component: MisSolicitudesView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/compras',
      name: 'usuario-compras',
      component: SolicitanteComprasView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/notificaciones',
      name: 'usuario-notificaciones',
      component: NotificacionesView,
      meta: {
        requiereAuth: true,
      },
    },

    {
      path: '/usuario/perfil',
      name: 'usuario-perfil',
      component: PerfilView,
      meta: {
        requiereAuth: true,
      },
    },


    /* =====================================================
       RUTA NO ENCONTRADA
    ===================================================== */

    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})


/* =========================================================
   PROTECCIÓN DE RUTAS
========================================================= */

router.beforeEach(
  (to) => {

    const token =
      localStorage.getItem(
        'sigta_token'
      )


    const usuarioTexto =
      localStorage.getItem(
        'sigta_usuario'
      )


    let usuario = null


    try {

      usuario =
        usuarioTexto
          ? JSON.parse(usuarioTexto)
          : null

    } catch {

      usuario = null
    }


    /* -----------------------------------------------------
       RUTA QUE REQUIERE LOGIN
    ----------------------------------------------------- */

    if (
      to.meta.requiereAuth
      &&
      !token
    ) {

      return '/login'
    }


    /* -----------------------------------------------------
       RUTAS ADMIN
    ----------------------------------------------------- */

    if (to.meta.admin) {

      const roles =
        Array.isArray(usuario?.roles)
          ? usuario.roles.map(
              rol =>
                String(
                  rol.codigo || ''
                ).toUpperCase()
            )
          : []


      if (
        !roles.includes('ADMIN')
      ) {

        return '/usuario/dashboard'
      }
    }


    /* -----------------------------------------------------
       USUARIO LOGUEADO EN LOGIN
    ----------------------------------------------------- */

    if (
      to.path === '/login'
      &&
      token
      &&
      usuario
    ) {

      const roles =
        Array.isArray(usuario.roles)
          ? usuario.roles.map(
              rol =>
                String(
                  rol.codigo || ''
                ).toUpperCase()
            )
          : []


      if (
        roles.includes('ADMIN')
      ) {

        return '/admin/dashboard'
      }
    }


    return true
  }
)


export default router