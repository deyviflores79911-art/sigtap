<template>

  <aside class="sidebar">

    <!-- =====================================================
         MARCA
    ====================================================== -->

    <div class="brand">

      <div class="logo">
        EMI
      </div>

      <div>

        <h2>
          SIGTA
        </h2>

        <span>
          Sistema Integral de Gestión
        </span>

      </div>

    </div>


    <!-- =====================================================
         USUARIO
    ====================================================== -->

    <div class="user-box">

      <div class="avatar">
        {{ iniciales }}
      </div>


      <div class="user-data">

        <strong>
          {{
            usuario?.nombre
            ||
            usuario?.nombre_completo
            ||
            'Usuario solicitante'
          }}
        </strong>

        <span>
          {{ areaUsuario }}
        </span>

      </div>

    </div>


    <!-- =====================================================
         MENÚ
    ====================================================== -->

    <div class="section-title">
      MI PORTAL
    </div>


    <nav>

      <!-- INICIO -->

      <router-link
        to="/usuario/dashboard"
        class="menu-item"
      >

        <span class="icon">
          ▦
        </span>

        Inicio

      </router-link>


      <!-- SOPORTE TÉCNICO -->

      <router-link
        to="/usuario/soporte"
        class="menu-item"
      >

        <span class="icon">
          ST
        </span>

        Soporte Técnico

      </router-link>


      <!-- MANTENIMIENTO -->

      <router-link
        to="/usuario/mantenimiento"
        class="menu-item"
      >

        <span class="icon">
          MT
        </span>

        Mantenimiento

      </router-link>


      <!-- COMPRAS -->

      <router-link
        to="/usuario/compras"
        class="menu-item"
      >

        <span class="icon">
          CP
        </span>

        Compras

      </router-link>


      <!-- MIS SOLICITUDES -->

      <router-link
        to="/usuario/mis-solicitudes"
        class="menu-item"
      >

        <span class="icon">
          ≡
        </span>

        Mis solicitudes

      </router-link>


      <!-- NOTIFICACIONES -->

      <router-link
        to="/usuario/notificaciones"
        class="menu-item"
      >

        <span class="icon">
          N
        </span>

        Notificaciones

      </router-link>


      <!-- PERFIL -->

      <router-link
        to="/usuario/perfil"
        class="menu-item"
      >

        <span class="icon">
          P
        </span>

        Mi perfil

      </router-link>

    </nav>


    <!-- =====================================================
         INFORMACIÓN DEL SISTEMA
    ====================================================== -->

    <div class="system-card">

      <div class="status-row">

        <span class="status-dot"></span>

        <strong>
          SIGTA ACTIVO
        </strong>

      </div>


      <small>
        Sistema Integral de Gestión
      </small>

    </div>


    <!-- =====================================================
         CERRAR SESIÓN
    ====================================================== -->

    <button
      class="logout"
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


// ==========================================================
// USUARIO
// ==========================================================

const usuario =
  ref(null)


const guardado =
  localStorage.getItem(
    'sigta_usuario'
  )


if (guardado) {

  try {

    usuario.value =
      JSON.parse(
        guardado
      )

  } catch (error) {

    console.error(
      'Error leyendo usuario:',
      error
    )
  }
}


// ==========================================================
// INICIALES
// ==========================================================

const iniciales =
  computed(() => {

    const nombre =
      usuario.value?.nombre
      ||
      usuario.value?.nombre_completo
      ||
      'Usuario'


    return nombre
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(
        parte =>
          parte
            .charAt(0)
            .toUpperCase()
      )
      .join('')
  })


// ==========================================================
// ÁREA DEL USUARIO
// ==========================================================

const areaUsuario =
  computed(() => {

    const roles =
      usuario.value?.roles


    if (
      Array.isArray(roles)
      &&
      roles.length > 0
    ) {

      const primerRol =
        roles[0]


      if (
        typeof primerRol?.area
        ===
        'object'
      ) {

        return (
          primerRol.area?.nombre
          ||
          primerRol.nombre
          ||
          'Solicitante'
        )
      }


      return (
        primerRol?.area
        ||
        primerRol?.nombre
        ||
        'Solicitante'
      )
    }


    return 'Solicitante'
  })


// ==========================================================
// CERRAR SESIÓN
// ==========================================================

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

  width: 235px;

  min-width: 235px;

  min-height: 100vh;


  display: flex;

  flex-direction: column;


  padding:
    18px
    12px;


  background:
    #153f73;

  color:
    #ffffff;


  font-family:
    Arial,
    Helvetica,
    sans-serif;
}


/* =========================================================
   MARCA
========================================================= */

.brand {

  display: flex;

  align-items: center;


  gap: 10px;


  padding:
    0
    7px
    18px;


  border-bottom:
    1px solid
    rgba(
      255,
      255,
      255,
      .16
    );
}


.logo {

  width: 43px;

  height: 43px;


  display: flex;

  align-items: center;

  justify-content: center;


  flex-shrink: 0;


  border-radius: 8px;


  background:
    #f2c400;

  color:
    #073b6f;


  font-size: 12px;

  font-weight: 900;
}


.brand h2 {

  margin: 0;


  font-size: 19px;
}


.brand span {

  display: block;


  margin-top: 2px;


  color:
    #afc2d4;


  font-size: 8px;
}


/* =========================================================
   USUARIO
========================================================= */

.user-box {

  display: flex;

  align-items: center;


  gap: 9px;


  padding:
    18px
    7px;
}


.avatar {

  width: 34px;

  height: 34px;


  flex-shrink: 0;


  display: flex;

  align-items: center;

  justify-content: center;


  border-radius: 50%;


  background:
    #f2c400;

  color:
    #073b6f;


  font-size: 10px;

  font-weight: 900;
}


.user-data {

  min-width: 0;
}


.user-data strong,
.user-data span {

  display: block;
}


.user-data strong {

  overflow: hidden;


  color:
    #ffffff;


  font-size: 10px;


  text-overflow: ellipsis;

  white-space: nowrap;
}


.user-data span {

  margin-top: 2px;


  color:
    #afc2d4;


  font-size: 8px;
}


/* =========================================================
   TÍTULO DE SECCIÓN
========================================================= */

.section-title {

  margin:
    12px
    8px
    6px;


  color:
    #82a5c6;


  font-size: 8px;

  font-weight: 800;


  letter-spacing: .9px;
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

  min-height: 42px;


  display: flex;

  align-items: center;


  gap: 9px;


  padding:
    0
    10px;


  border-radius: 7px;


  color:
    #e7eef5;


  text-decoration: none;


  font-size: 10px;


  transition:
    background .2s,
    color .2s;
}


.icon {

  width: 25px;


  flex-shrink: 0;


  color:
    #abc0d3;


  font-size: 8px;

  font-weight: 900;
}


.menu-item:hover {

  background:
    rgba(
      255,
      255,
      255,
      .08
    );
}


/* =========================================================
   OPCIÓN ACTIVA
========================================================= */

.menu-item.router-link-active {

  padding-left: 7px;


  border-left:
    3px solid
    #f2c400;


  background:
    rgba(
      255,
      255,
      255,
      .12
    );


  color:
    #f4d52f;


  font-weight: 700;
}


.menu-item.router-link-active
.icon {

  color:
    #f2c400;
}


/* =========================================================
   ESTADO DEL SISTEMA
========================================================= */

.system-card {

  margin-top: auto;


  padding: 11px;


  border:
    1px solid
    rgba(
      255,
      255,
      255,
      .18
    );


  border-radius: 7px;


  background:
    rgba(
      255,
      255,
      255,
      .07
    );
}


.status-row {

  display: flex;

  align-items: center;


  gap: 6px;
}


.status-dot {

  width: 7px;

  height: 7px;


  border-radius: 50%;


  background:
    #38c66b;
}


.system-card strong {

  color:
    #f2d334;


  font-size: 8px;
}


.system-card small {

  display: block;


  margin-top: 4px;


  color:
    #9db5ca;


  font-size: 7px;
}


/* =========================================================
   CERRAR SESIÓN
========================================================= */

.logout {

  width: 100%;

  min-height: 40px;


  margin-top: 9px;


  border:
    1px solid
    rgba(
      255,
      255,
      255,
      .27
    );


  border-radius: 6px;


  background:
    transparent;


  color:
    white;


  font-size: 9px;

  font-weight: 700;


  cursor: pointer;
}


.logout:hover {

  background:
    rgba(
      255,
      255,
      255,
      .08
    );
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 760px
) {

  .sidebar {

    width: 100%;

    min-width: 100%;

    min-height: auto;
  }


  .system-card {

    margin-top: 18px;
  }

}

</style>