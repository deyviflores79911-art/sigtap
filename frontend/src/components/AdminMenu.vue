<template>
  <aside class="sidebar">

    <!-- =====================================================
         MARCA
    ====================================================== -->

    <div class="brand">

      <div class="logo">
        EMI
      </div>

      <div class="brand-text">
        <h2>SIGTA</h2>

        <span>
          Sistema Integral de Gestión
        </span>
      </div>

    </div>


    <!-- =====================================================
         USUARIO AUTENTICADO
    ====================================================== -->

    <div class="admin-info">

      <div class="avatar">
        {{ iniciales }}
      </div>

      <div class="admin-data">

        <strong>
          {{ nombreUsuario }}
        </strong>

        <span>
          {{ nombreRol }}
        </span>

        <small>
          {{ nombreArea }}
        </small>

      </div>

    </div>


    <!-- =====================================================
         OPERACIÓN
    ====================================================== -->

    <div class="section-title">
      OPERACIÓN
    </div>

    <nav>

      <!-- DASHBOARD -->

      <router-link
        v-if="puede('VER_DASHBOARD_ADMIN')"
        to="/admin/dashboard"
        class="menu-item"
      >
        <span class="icon">
          ▦
        </span>

        <span>
          Dashboard
        </span>
      </router-link>


      <!-- SOPORTE TÉCNICO -->

      <router-link
        v-if="puede('VER_SOPORTE_TECNICO')"
        to="/admin/soporte"
        class="menu-item"
      >
        <span class="icon">
          ST
        </span>

        <span>
          Soporte Técnico
        </span>
      </router-link>


      <!-- MANTENIMIENTO -->

      <router-link
        v-if="puede('VER_MANTENIMIENTO')"
        to="/admin/mantenimiento"
        class="menu-item"
      >
        <span class="icon">
          MT
        </span>

        <span>
          Mantenimiento
        </span>
      </router-link>


      <!-- COMPRAS -->

      <router-link
        v-if="puede('VER_COMPRAS')"
        to="/admin/compras"
        class="menu-item"
      >
        <span class="icon">
          CP
        </span>

        <span>
          Compras
        </span>
      </router-link>

    </nav>


    <!-- =====================================================
         AUTOSERVICIO
    ====================================================== -->

    <template
      v-if="puede('VER_PORTAL_SOLICITANTE')"
    >

      <div class="section-title">
        AUTOSERVICIO
      </div>


      <nav>

        <router-link
          to="/admin/portal-solicitante"
          class="menu-item"
        >
          <span class="icon">
            PS
          </span>

          <span>
            Portal Solicitante
          </span>
        </router-link>

      </nav>

    </template>


    <!-- =====================================================
         ADMINISTRACIÓN
    ====================================================== -->

    <template
      v-if="mostrarAdministracion"
    >

      <div class="section-title">
        ADMINISTRACIÓN
      </div>


      <nav>

        <!-- USUARIOS -->

        <router-link
          v-if="puede('GESTIONAR_USUARIOS')"
          to="/admin/usuarios"
          class="menu-item"
        >
          <span class="icon">
            U
          </span>

          <span>
            Usuarios
          </span>
        </router-link>


        <!-- ROLES / PERMISOS / ÁREAS -->

        <router-link
          v-if="puede('GESTIONAR_ROLES_PERMISOS')"
          to="/admin/roles-areas"
          class="menu-item"
        >
          <span class="icon">
            RP
          </span>

          <span>
            Roles, permisos y áreas
          </span>
        </router-link>


        <!--
          Conservamos la ruta existente para no romper
          la pantalla que ya tienes.

          Después revisaremos AdminTicketsView.vue para
          determinar si debe quedar como consulta general
          de tickets de Soporte Técnico.
        -->

        <router-link
          v-if="puede('CONSULTAR_TICKETS')"
          to="/admin/tickets"
          class="menu-item"
        >
          <span class="icon">
            T
          </span>

          <span>
            Consulta de tickets
          </span>
        </router-link>


        <!-- BITÁCORA -->

        <router-link
          v-if="puede('CONSULTAR_BITACORA')"
          to="/admin/bitacora"
          class="menu-item"
        >
          <span class="icon">
            B
          </span>

          <span>
            Bitácora
          </span>
        </router-link>


        <!-- SMTP -->

        <router-link
          v-if="puede('CONFIGURAR_SMTP')"
          to="/admin/smtp"
          class="menu-item"
        >
          <span class="icon">
            @
          </span>

          <span>
            Correo SMTP
          </span>
        </router-link>


        <!-- PREFERENCIAS -->

        <router-link
          v-if="puede('CONFIGURAR_PREFERENCIAS')"
          to="/admin/preferencias"
          class="menu-item"
        >
          <span class="icon">
            P
          </span>

          <span>
            Preferencias
          </span>
        </router-link>

      </nav>

    </template>


    <!-- =====================================================
         INFORMACIÓN DE SEGURIDAD
    ====================================================== -->

    <div class="access-box">

      <div class="access-title">

        <span class="status-dot"></span>

        <strong>
          CONTROL DE ACCESO ACTIVO
        </strong>

      </div>

      <small>
        Las opciones visibles dependen del rol
        y sus permisos.
      </small>

    </div>


    <!-- =====================================================
         CERRAR SESIÓN
    ====================================================== -->

    <button
      class="logout"
      type="button"
      @click="cerrarSesion"
    >
      Cerrar sesión
    </button>

  </aside>
</template>


<script setup>

import {
  computed,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'


const router =
  useRouter()


/* =========================================================
   USUARIO
========================================================= */

const usuario =
  ref(null)


const usuarioGuardado =
  localStorage.getItem(
    'sigta_usuario'
  )


if (usuarioGuardado) {

  try {

    usuario.value =
      JSON.parse(
        usuarioGuardado
      )

  } catch (error) {

    console.error(
      'No se pudo leer sigta_usuario:',
      error
    )

    usuario.value = null
  }
}


/* =========================================================
   DATOS DEL USUARIO
========================================================= */

const nombreUsuario =
  computed(() => {

    return (
      usuario.value?.nombre
      ||
      usuario.value?.nombre_completo
      ||
      'Administrador SIGTA'
    )
  })


const iniciales =
  computed(() => {

    const nombre =
      nombreUsuario.value


    return nombre
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map(
        palabra =>
          palabra
            .charAt(0)
            .toUpperCase()
      )
      .join('')
      ||
      'AS'
  })


/* =========================================================
   ROLES
========================================================= */

const rolesUsuario =
  computed(() => {

    const roles =
      usuario.value?.roles


    return Array.isArray(roles)
      ? roles
      : []
  })


const codigoRolPrincipal =
  computed(() => {

    const rol =
      rolesUsuario.value[0]


    return String(
      rol?.codigo
      ||
      rol?.rol_codigo
      ||
      rol?.nombre
      ||
      rol?.rol_nombre
      ||
      ''
    )
      .trim()
      .toUpperCase()
      .replace(/\s+/g, '_')
  })


const nombreRol =
  computed(() => {

    const rol =
      rolesUsuario.value[0]


    return (
      rol?.nombre
      ||
      rol?.rol_nombre
      ||
      (
        esAdministrador.value
          ? 'Administrador SIGTA'
          : 'Usuario'
      )
    )
  })


const nombreArea =
  computed(() => {

    const rol =
      rolesUsuario.value[0]


    return (
      rol?.area
      ||
      rol?.area_nombre
      ||
      (
        esAdministrador.value
          ? 'Global'
          : 'Sin área'
      )
    )
  })


/* =========================================================
   IDENTIFICAR ADMINISTRADOR
========================================================= */

const esAdministrador =
  computed(() => {

    const codigo =
      codigoRolPrincipal.value


    /*
      Soportamos varios nombres porque actualmente
      tu proyecto ya ha utilizado "ADMIN" y "Admin".
    */

    return [
      'ADMIN',
      'ADMINISTRADOR',
      'ADMINISTRADOR_SIGTA',
    ].includes(codigo)
  })


/* =========================================================
   PERMISOS

   Todavía no rompemos el sistema actual.

   - Si es ADMIN, obtiene acceso completo.
   - Cuando implementemos Permiso y RolPermiso en Django,
     el login devolverá usuario.permisos.
   - Desde ese momento este mismo componente empezará
     a utilizar esos permisos sin volver a rehacer el menú.
========================================================= */

const permisosUsuario =
  computed(() => {

    const permisos =
      usuario.value?.permisos


    if (!Array.isArray(permisos)) {
      return []
    }


    return permisos
      .map(
        permiso => {

          if (
            typeof permiso === 'string'
          ) {

            return permiso
              .trim()
              .toUpperCase()
          }


          return String(
            permiso?.codigo
            ||
            permiso?.permiso_codigo
            ||
            ''
          )
            .trim()
            .toUpperCase()
        }
      )
      .filter(Boolean)
  })


function puede(
  permiso
) {

  /*
   * El Administrador SIGTA conserva acceso total.
   *
   * Esto es importante ahora porque todavía no hemos
   * creado las tablas Permiso y RolPermiso.
   */

  if (
    esAdministrador.value
  ) {

    return true
  }


  return permisosUsuario.value.includes(
    String(permiso)
      .trim()
      .toUpperCase()
  )
}


/* =========================================================
   MOSTRAR BLOQUE ADMINISTRACIÓN
========================================================= */

const mostrarAdministracion =
  computed(() => {

    return (

      puede(
        'GESTIONAR_USUARIOS'
      )

      ||

      puede(
        'GESTIONAR_ROLES_PERMISOS'
      )

      ||

      puede(
        'CONSULTAR_TICKETS'
      )

      ||

      puede(
        'CONSULTAR_BITACORA'
      )

      ||

      puede(
        'CONFIGURAR_SMTP'
      )

      ||

      puede(
        'CONFIGURAR_PREFERENCIAS'
      )
    )
  })


/* =========================================================
   CERRAR SESIÓN
========================================================= */

function cerrarSesion() {

  localStorage.removeItem(
    'sigta_token'
  )

  localStorage.removeItem(
    'sigta_usuario'
  )

  router.push(
    '/login'
  )
}

</script>


<style scoped>

* {
  box-sizing: border-box;
}


/* =========================================================
   SIDEBAR
========================================================= */

.sidebar {

  position: sticky;

  top: 0;

  width: 255px;
  min-width: 255px;

  height: 100vh;

  display: flex;
  flex-direction: column;

  padding:
    20px
    14px;

  overflow-y: auto;
  overflow-x: hidden;

  background: #123f73;

  color: #ffffff;

  font-family:
    Arial,
    Helvetica,
    sans-serif;
}


/* Scroll discreto */

.sidebar::-webkit-scrollbar {
  width: 5px;
}

.sidebar::-webkit-scrollbar-thumb {

  border-radius: 10px;

  background:
    rgba(
      255,
      255,
      255,
      .18
    );
}


/* =========================================================
   MARCA
========================================================= */

.brand {

  display: flex;
  align-items: center;

  gap: 12px;

  padding:
    0
    8px
    20px;

  border-bottom:
    1px solid
    rgba(
      255,
      255,
      255,
      .17
    );
}


.logo {

  width: 48px;
  height: 48px;

  flex-shrink: 0;

  display: flex;

  align-items: center;
  justify-content: center;

  border-radius: 10px;

  background: #f2c400;

  color: #073b6f;

  font-size: 13px;

  font-weight: 900;
}


.brand-text {
  min-width: 0;
}


.brand h2 {

  margin: 0;

  font-size: 22px;
}


.brand span {

  display: block;

  margin-top: 3px;

  color: #c4d2df;

  font-size: 9px;

  line-height: 1.3;
}


/* =========================================================
   USUARIO
========================================================= */

.admin-info {

  display: flex;

  align-items: center;

  gap: 10px;

  padding:
    18px
    8px
    10px;
}


.avatar {

  width: 38px;
  height: 38px;

  flex-shrink: 0;

  display: flex;

  align-items: center;
  justify-content: center;

  border-radius: 50%;

  background: #f2c400;

  color: #073b6f;

  font-size: 10px;

  font-weight: 900;
}


.admin-data {
  min-width: 0;
}


.admin-info strong,
.admin-info span,
.admin-info small {

  display: block;
}


.admin-info strong {

  overflow: hidden;

  color: #ffffff;

  font-size: 10px;

  text-overflow: ellipsis;

  white-space: nowrap;
}


.admin-info span {

  margin-top: 3px;

  color: #d1dce6;

  font-size: 8px;
}


.admin-info small {

  margin-top: 2px;

  color: #94afc7;

  font-size: 8px;
}


/* =========================================================
   SECCIONES
========================================================= */

.section-title {

  margin:
    17px
    10px
    6px;

  color: #82a5c6;

  font-size: 8px;

  font-weight: 800;

  letter-spacing: 1px;
}


/* =========================================================
   NAVEGACIÓN
========================================================= */

nav {

  display: flex;

  flex-direction: column;

  gap: 3px;
}


.menu-item {

  position: relative;

  min-height: 42px;

  display: flex;

  align-items: center;

  gap: 9px;

  padding:
    0
    11px;

  border-radius: 7px;

  color: #e8eff6;

  text-decoration: none;

  font-size: 10px;

  transition:
    background .2s,
    color .2s,
    padding .2s;
}


.icon {

  width: 25px;

  flex-shrink: 0;

  color: #aac0d3;

  font-size: 8px;

  font-weight: 900;

  text-align: center;
}


.menu-item:hover {

  background:
    rgba(
      255,
      255,
      255,
      .08
    );

  color: #ffffff;
}


.menu-item.router-link-active {

  padding-left: 8px;

  border-left:
    3px solid #f2c400;

  background:
    rgba(
      255,
      255,
      255,
      .13
    );

  color: #f5d532;

  font-weight: 700;
}


.menu-item.router-link-active
.icon {

  color: #f2c400;
}


/* =========================================================
   CONTROL DE ACCESO
========================================================= */

.access-box {

  margin-top: 20px;

  padding: 10px;

  border:
    1px solid
    rgba(
      255,
      255,
      255,
      .16
    );

  border-radius: 7px;

  background:
    rgba(
      255,
      255,
      255,
      .06
    );
}


.access-title {

  display: flex;

  align-items: center;

  gap: 6px;
}


.status-dot {

  width: 7px;
  height: 7px;

  flex-shrink: 0;

  border-radius: 50%;

  background: #37c56a;
}


.access-title strong {

  color: #f2d334;

  font-size: 7px;
}


.access-box small {

  display: block;

  margin-top: 5px;

  color: #a8bed0;

  font-size: 7px;

  line-height: 1.45;
}


/* =========================================================
   CERRAR SESIÓN
========================================================= */

.logout {

  width: 100%;

  min-height: 43px;

  flex-shrink: 0;

  margin-top: 12px;

  border:
    1px solid
    rgba(
      255,
      255,
      255,
      .3
    );

  border-radius: 7px;

  background: transparent;

  color: #ffffff;

  font-size: 10px;

  font-weight: 700;

  cursor: pointer;

  transition:
    background .2s,
    border-color .2s;
}


.logout:hover {

  background:
    rgba(
      255,
      255,
      255,
      .1
    );

  border-color:
    rgba(
      255,
      255,
      255,
      .45
    );
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 760px
) {

  .sidebar {

    position: relative;

    width: 100%;
    min-width: 100%;

    height: auto;

    min-height: auto;
  }


  .logout {

    margin-top: 20px;
  }

}

</style>