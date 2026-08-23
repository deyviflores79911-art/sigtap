<template>

  <div class="usuario-layout">

    <SolicitanteMenu />

    <main class="usuario-content">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="topbar">

        <div>

          <span class="breadcrumb">
            SIGTA / Portal Solicitante / Inicio
          </span>

          <h1>
            Bienvenido a SIGTA
          </h1>

          <p>
            Registre, consulte y dé seguimiento
            a sus requerimientos institucionales.
          </p>

        </div>


        <div class="user-card">

          <div class="user-avatar">
            {{ inicialesUsuario }}
          </div>

          <div>

            <strong>
              {{
                usuario?.nombre
                || usuario?.nombre_completo
                || 'Usuario solicitante'
              }}
            </strong>

            <span>
              {{ usuario?.email || '' }}
            </span>

          </div>

        </div>

      </header>


      <!-- =================================================
           RESUMEN
      ================================================== -->

      <section class="stats-grid">

        <article class="stat-card">

          <span>
            Requerimientos de soporte
          </span>

          <strong>
            {{ soporte.length }}
          </strong>

          <small>
            Solicitudes de soporte registradas
          </small>

        </article>


        <article class="stat-card">

          <span>
            Requerimientos de mantenimiento
          </span>

          <strong>
            {{ mantenimiento.length }}
          </strong>

          <small>
            Requerimientos de mantenimiento registrados
          </small>

        </article>


        <article class="stat-card">

          <span>
            Solicitudes de compra
          </span>

          <strong>
            {{ compras.length }}
          </strong>

          <small>
            Solicitudes de adquisición registradas
          </small>

        </article>


        <article class="stat-card">

          <span>
            Total
          </span>

          <strong>
            {{ total }}
          </strong>

          <small>
            Requerimientos y solicitudes registradas
          </small>

        </article>

      </section>


      <!-- =================================================
           ACCIONES PRINCIPALES
      ================================================== -->

      <section class="portal-card">

        <div class="section-header">

          <div>

            <h2>
              ¿Qué necesita registrar?
            </h2>

            <p>
              Seleccione el proceso institucional
              que corresponde a su requerimiento.
            </p>

          </div>

        </div>


        <div class="cards">

          <!-- SOPORTE TÉCNICO -->

          <button
            class="action-card"
            @click="
              router.push(
                '/usuario/soporte'
              )
            "
          >

            <div class="card-header">

              <div class="card-icon">
                ST
              </div>

              <span class="tag">
                SOPORTE
              </span>

            </div>


            <h3>
              Soporte Técnico
            </h3>


            <p>
              Registre una solicitud de soporte para
              problemas de hardware, software, red,
              proyectores, conectividad o sistemas
              institucionales.
            </p>


            <div class="card-footer">

              <strong>
                Registrar solicitud de soporte
              </strong>

              <span>
                →
              </span>

            </div>

          </button>


          <!-- MANTENIMIENTO -->

          <button
            class="action-card"
            @click="
              router.push(
                '/usuario/mantenimiento'
              )
            "
          >

            <div class="card-header">

              <div class="card-icon">
                MT
              </div>

              <span class="tag">
                MANTENIMIENTO
              </span>

            </div>


            <h3>
              Mantenimiento
            </h3>


            <p>
              Registre un requerimiento de mantenimiento
              preventivo o correctivo para infraestructura,
              bienes o activos institucionales.
            </p>


            <div class="card-footer">

              <strong>
                Registrar requerimiento de mantenimiento
              </strong>

              <span>
                →
              </span>

            </div>

          </button>


          <!-- COMPRAS -->

          <button
            class="action-card"
            @click="
              router.push(
                '/usuario/compras'
              )
            "
          >

            <div class="card-header">

              <div class="card-icon">
                CP
              </div>

              <span class="tag">
                COMPRAS
              </span>

            </div>


            <h3>
              Compras
            </h3>


            <p>
              Registre una solicitud de compra para
              la adquisición de bienes, equipos,
              componentes o materiales institucionales.
            </p>


            <div class="card-footer">

              <strong>
                Registrar solicitud de compra
              </strong>

              <span>
                →
              </span>

            </div>

          </button>

        </div>

      </section>


      <!-- =================================================
           SOLICITUDES RECIENTES
      ================================================== -->

      <section class="recent">

        <div class="recent-header">

          <div>

            <h2>
              Mis requerimientos recientes
            </h2>

            <p>
              Últimos registros de Soporte Técnico,
              Mantenimiento y Compras.
            </p>

          </div>


          <button
            class="view-all"
            @click="
              router.push(
                '/usuario/mis-solicitudes'
              )
            "
          >
            Ver todos
          </button>

        </div>


        <!-- CARGANDO -->

        <div
          v-if="cargando"
          class="empty"
        >
          Cargando requerimientos...
        </div>


        <!-- ERROR -->

        <div
          v-else-if="mensajeError"
          class="error-box"
        >
          {{ mensajeError }}
        </div>


        <!-- SIN SOLICITUDES -->

        <div
          v-else-if="
            recientes.length === 0
          "
          class="empty-state"
        >

          <div class="empty-icon">
            SG
          </div>

          <h3>
            Todavía no tiene requerimientos registrados
          </h3>

          <p>
            Cuando registre una solicitud de soporte,
            un requerimiento de mantenimiento o una
            solicitud de compra, aparecerá aquí para
            que pueda consultar su estado.
          </p>

        </div>


        <!-- LISTA -->

        <div
          v-else
          class="ticket-list"
        >

          <article
            v-for="item in recientes.slice(0, 6)"
            :key="`${item.modulo}-${item.id}`"
          >

            <div class="ticket-main">

              <div class="ticket-code">

                <span
                  class="status-dot"
                  :class="
                    claseEstadoGeneral(
                      item.estado_codigo
                    )
                  "
                ></span>


                <strong>
                  {{
                    item.codigo
                    || `Registro #${item.id}`
                  }}
                </strong>

              </div>


              <h3>
                {{
                  item.titulo
                  || 'Requerimiento institucional'
                }}
              </h3>


              <div class="ticket-meta">

                <span>
                  {{ item.modulo }}
                </span>

                <span
                  v-if="item.area_nombre"
                >
                  {{ item.area_nombre }}
                </span>

                <span
                  v-if="item.ubicacion"
                >
                  {{ item.ubicacion }}
                </span>

              </div>

            </div>


            <div class="ticket-actions">

              <span
                class="estado"
                :class="
                  claseEstadoGeneral(
                    item.estado_codigo
                  )
                "
              >
                {{
                  item.estado_nombre
                  || item.estado_codigo
                  || 'Registrado'
                }}
              </span>


              <button
                @click="
                  router.push(
                    '/usuario/mis-solicitudes'
                  )
                "
              >
                Ver
              </button>

            </div>

          </article>

        </div>

      </section>

    </main>

  </div>

</template>


<script setup>

import {
  computed,
  onMounted,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'

import SolicitanteMenu
  from '../components/SolicitanteMenu.vue'


const router =
  useRouter()


// ==========================================================
// DATOS
// ==========================================================

const usuario =
  ref(null)

const soporte =
  ref([])

const mantenimiento =
  ref([])

const compras =
  ref([])

const cargando =
  ref(true)

const mensajeError =
  ref('')


// ==========================================================
// TOKEN
// ==========================================================

const token = () =>
  localStorage.getItem(
    'sigta_token'
  )


// ==========================================================
// INICIALES
// ==========================================================

const inicialesUsuario =
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
      .slice(0, 2)
      .map(
        palabra =>
          palabra
            .charAt(0)
            .toUpperCase()
      )
      .join('')
  })


// ==========================================================
// TOTAL
// ==========================================================

const total =
  computed(() => {

    return (
      soporte.value.length
      +
      mantenimiento.value.length
      +
      compras.value.length
    )
  })


// ==========================================================
// INICIO
// ==========================================================

onMounted(
  async () => {

    const guardado =
      localStorage.getItem(
        'sigta_usuario'
      )


    if (
      !guardado
      ||
      !token()
    ) {

      router.push(
        '/login'
      )

      return
    }


    try {

      usuario.value =
        JSON.parse(
          guardado
        )

    } catch (error) {

      console.error(
        'Usuario guardado inválido:',
        error
      )


      cerrarSesion()

      return
    }


    await cargarTodo()
  }
)


// ==========================================================
// NORMALIZAR LISTA
// ==========================================================

function convertirLista(
  datos
) {

  if (
    Array.isArray(datos)
  ) {

    return datos
  }


  if (
    Array.isArray(
      datos?.results
    )
  ) {

    return datos.results
  }


  return []
}


// ==========================================================
// CARGAR TODO
// ==========================================================

async function cargarTodo() {

  cargando.value =
    true

  mensajeError.value =
    ''


  try {

    await Promise.all([
      cargarSoporte(),
      cargarMantenimiento(),
      cargarCompras(),
    ])


  } catch (error) {

    console.error(
      'Error cargando portal:',
      error
    )


    mensajeError.value =
      'No fue posible cargar todos sus requerimientos.'


  } finally {

    cargando.value =
      false
  }
}


// ==========================================================
// FETCH AUXILIAR
// ==========================================================

async function cargarEndpoint(
  url
) {

  const respuesta =
    await fetch(
      url,
      {
        headers: {

          Authorization:
            `Token ${token()}`,

          Accept:
            'application/json',
        }
      }
    )


  if (
    respuesta.status === 401
    ||
    respuesta.status === 403
  ) {

    cerrarSesion()

    throw new Error(
      'Sesión no autorizada.'
    )
  }


  if (
    !respuesta.ok
  ) {

    throw new Error(
      `Error ${respuesta.status}`
    )
  }


  return convertirLista(
    await respuesta.json()
  )
}


// ==========================================================
// SOPORTE
// ==========================================================

async function cargarSoporte() {

  try {

    soporte.value =
      await cargarEndpoint(
        '/api/soporte/tickets/'
      )


  } catch (error) {

    console.error(
      'Error cargando soporte:',
      error
    )

    soporte.value = []
  }
}


// ==========================================================
// MANTENIMIENTO
// ==========================================================

async function cargarMantenimiento() {

  try {

    mantenimiento.value =
      await cargarEndpoint(
        '/api/mantenimiento/requerimientos/'
      )


  } catch (error) {

    console.error(
      'Error cargando mantenimiento:',
      error
    )

    mantenimiento.value = []
  }
}


// ==========================================================
// COMPRAS
// ==========================================================

async function cargarCompras() {

  try {

    compras.value =
      await cargarEndpoint(
        '/api/compras/solicitudes/'
      )


  } catch (error) {

    console.error(
      'Error cargando compras:',
      error
    )

    compras.value = []
  }
}


// ==========================================================
// RECIENTES UNIFICADOS
// ==========================================================

const recientes =
  computed(() => {

    const st =
      soporte.value.map(
        item => ({

          ...item,

          modulo:
            'Soporte Técnico',

          estado_codigo:
            item.estado_codigo
            || item.estado,

          estado_nombre:
            item.estado_nombre
            || item.estado_codigo
            || item.estado,

          fecha_orden:
            item.creado_en
            || item.fecha_creacion
            || item.created_at
            || null,
        })
      )


    const mt =
      mantenimiento.value.map(
        item => ({

          ...item,

          modulo:
            'Mantenimiento',

          estado_codigo:
            item.estado_codigo
            || item.estado,

          estado_nombre:
            item.estado_nombre
            || item.estado_codigo
            || item.estado,

          fecha_orden:
            item.creado_en
            || item.created_at
            || null,
        })
      )


    const cp =
      compras.value.map(
        item => ({

          ...item,

          modulo:
            'Compras',

          titulo:
            item.titulo
            || item.descripcion
            || 'Solicitud de compra',

          estado_codigo:
            item.estado
            || item.estado_codigo,

          estado_nombre:
            item.estado_nombre
            || item.estado
            || 'Registrado',

          fecha_orden:
            item.creado_en
            || item.created_at
            || null,
        })
      )


    return [
      ...st,
      ...mt,
      ...cp
    ]
      .sort(
        (a, b) => {

          const fechaA =
            new Date(
              a.fecha_orden
              || 0
            ).getTime()

          const fechaB =
            new Date(
              b.fecha_orden
              || 0
            ).getTime()


          if (
            fechaA
            &&
            fechaB
          ) {

            return fechaB - fechaA
          }


          return (
            Number(b.id || 0)
            -
            Number(a.id || 0)
          )
        }
      )
  })


// ==========================================================
// ESTILO ESTADO GENERAL
// ==========================================================

function claseEstadoGeneral(
  valor
) {

  const estado =
    String(
      valor
      || ''
    )
      .toUpperCase()
      .replaceAll(' ', '_')


  if (
    estado.includes(
      'ANUL'
    )
    ||
    estado.includes(
      'RECHAZ'
    )
  ) {

    return 'status-cancelled'
  }


  if (
    estado === 'CERRADO'
    ||
    estado === 'RESUELTO'
    ||
    estado === 'FINALIZADO'
  ) {

    return 'status-closed'
  }


  if (
    estado === 'NUEVO'
    ||
    estado === 'RECIBIDO'
  ) {

    return 'status-new'
  }


  if (
    estado.includes('EJEC')
    ||
    estado.includes('ANAL')
    ||
    estado.includes('ASIGN')
    ||
    estado.includes('VERIFIC')
    ||
    estado.includes('DERIV')
    ||
    estado.includes('MANTENIMIENTO')
    ||
    estado.includes('APROB')
    ||
    estado.includes('COTIZ')
    ||
    estado.includes('TRANSITO')
    ||
    estado.includes('ESPERA')
  ) {

    return 'status-process'
  }


  return 'status-default'
}


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
   LAYOUT
========================================================= */

.usuario-layout {

  min-height: 100vh;

  display: flex;

  background: #eef3f8;

  font-family:
    Arial,
    Helvetica,
    sans-serif;
}


.usuario-content {

  flex: 1;

  min-width: 0;

  padding:
    28px
    30px;

  overflow-x: hidden;
}


/* =========================================================
   TOPBAR
========================================================= */

.topbar {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  gap: 20px;

  margin-bottom: 22px;
}


.breadcrumb {

  display: block;

  margin-bottom: 7px;

  color: #8494a2;

  font-size: 9px;
}


.topbar h1 {

  margin: 0;

  color: #17324a;

  font-size: 28px;
}


.topbar p {

  margin:
    5px
    0
    0;

  color: #71818f;

  font-size: 12px;
}


/* =========================================================
   USUARIO
========================================================= */

.user-card {

  min-width: 190px;

  display: flex;

  align-items: center;

  justify-content:
    flex-end;

  gap: 9px;

  padding:
    10px
    13px;

  border-radius: 8px;

  background: white;

  box-shadow:
    0
    3px
    10px
    rgba(0,0,0,.06);
}


.user-avatar {

  width: 34px;

  height: 34px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  background: #f2c400;

  color: #073b6f;

  font-size: 9px;

  font-weight: 900;
}


.user-card strong,
.user-card span {

  display: block;
}


.user-card strong {

  color: #17324a;

  font-size: 10px;
}


.user-card span {

  margin-top: 2px;

  color: #7b8995;

  font-size: 8px;
}


/* =========================================================
   ESTADÍSTICAS
========================================================= */

.stats-grid {

  display: grid;

  grid-template-columns:
    repeat(4,1fr);

  gap: 13px;

  margin-bottom: 19px;
}


.stat-card {

  min-height: 105px;

  padding: 16px;

  border-top:
    3px solid #f2c400;

  border-radius: 9px;

  background: #ffffff;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.05);
}


.stat-card span {

  display: block;

  color: #637789;

  font-size: 9px;

  font-weight: 800;

  text-transform:
    uppercase;
}


.stat-card strong {

  display: block;

  margin:
    7px
    0;

  color: #073b6f;

  font-size: 25px;
}


.stat-card small {

  color: #8996a1;

  font-size: 8px;
}


/* =========================================================
   PANEL PRINCIPAL
========================================================= */

.portal-card {

  margin-bottom: 20px;

  padding: 21px;

  border-radius: 10px;

  background: #ffffff;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.section-header h2 {

  margin: 0;

  color: #17324a;

  font-size: 17px;
}


.section-header p {

  margin:
    4px
    0
    17px;

  color: #788794;

  font-size: 10px;
}


/* =========================================================
   ACCIONES
========================================================= */

.cards {

  display: grid;

  grid-template-columns:
    repeat(3,1fr);

  gap: 15px;
}


.action-card {

  min-height: 210px;

  display: flex;

  flex-direction: column;

  padding: 19px;

  border:
    1px solid #dae2e8;

  border-radius: 9px;

  background: #fbfcfd;

  text-align: left;

  cursor: pointer;

  transition:
    border-color .2s,
    box-shadow .2s,
    transform .1s;
}


.action-card:hover {

  border-color: #0b5795;

  box-shadow:
    0
    5px
    14px
    rgba(0,0,0,.06);
}


.action-card:active {

  transform:
    scale(.995);
}


.card-header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 10px;
}


.card-icon {

  width: 38px;

  height: 38px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 7px;

  background: #153f73;

  color: white;

  font-size: 9px;

  font-weight: 900;
}


.tag {

  display: inline-block;

  padding:
    5px
    8px;

  border-radius: 5px;

  background: #edf4fa;

  color: #07518d;

  font-size: 8px;

  font-weight: 800;
}


.action-card h3 {

  margin:
    15px
    0
    7px;

  color: #17324a;

  font-size: 17px;
}


.action-card p {

  flex: 1;

  margin: 0;

  color: #6f7f8d;

  font-size: 10px;

  line-height: 1.55;
}


.card-footer {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 10px;

  margin-top: 16px;

  padding-top: 12px;

  border-top:
    1px solid #e9edf1;

  color: #07518d;

  font-size: 10px;
}


/* =========================================================
   RECIENTES
========================================================= */

.recent {

  padding: 21px;

  border-radius: 10px;

  background: white;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.recent-header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 15px;

  margin-bottom: 12px;
}


.recent-header h2 {

  margin: 0;

  color: #17324a;

  font-size: 17px;
}


.recent-header p {

  margin:
    4px
    0
    0;

  color: #788794;

  font-size: 9px;
}


.view-all {

  min-height: 34px;

  padding:
    0
    11px;

  border:
    1px solid #cdd7e0;

  border-radius: 6px;

  background: white;

  color: #07518d;

  font-size: 9px;

  font-weight: 700;

  cursor: pointer;
}


/* =========================================================
   LISTA RECIENTE
========================================================= */

.ticket-list {

  display: flex;

  flex-direction: column;
}


.ticket-list article {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 15px;

  padding:
    13px
    4px;

  border-top:
    1px solid #edf0f2;
}


.ticket-main {

  min-width: 0;

  flex: 1;
}


.ticket-code {

  display: flex;

  align-items: center;

  gap: 6px;
}


.ticket-list strong {

  color: #07518d;

  font-size: 9px;
}


.ticket-list h3 {

  margin:
    5px
    0;

  color: #314a5e;

  font-size: 12px;
}


.ticket-meta {

  display: flex;

  flex-wrap: wrap;

  gap: 6px;
}


.ticket-meta span {

  padding:
    4px
    6px;

  border-radius: 4px;

  background: #f0f4f7;

  color: #82909b;

  font-size: 7px;
}


.ticket-actions {

  flex-shrink: 0;

  display: flex;

  align-items: center;

  gap: 8px;
}


.ticket-actions button {

  padding:
    6px
    9px;

  border: none;

  border-radius: 5px;

  background: #eaf3fb;

  color: #07518d;

  font-size: 8px;

  font-weight: 700;

  cursor: pointer;
}


/* =========================================================
   ESTADOS
========================================================= */

.estado {

  padding:
    5px
    8px;

  border-radius: 20px;

  font-size: 8px;

  font-weight: 700;
}


.status-dot {

  width: 7px;

  height: 7px;

  flex-shrink: 0;

  border-radius: 50%;
}


.estado.status-new,
.status-dot.status-new {

  background: #e8f2fb;

  color: #07518d;
}


.status-dot.status-new {

  background: #2782c5;
}


.estado.status-process {

  background: #fff3d7;

  color: #946700;
}


.status-dot.status-process {

  background: #e7a70b;
}


.estado.status-closed {

  background: #e8f7ef;

  color: #267449;
}


.status-dot.status-closed {

  background: #2baa62;
}


.estado.status-cancelled {

  background: #fdecec;

  color: #a83232;
}


.status-dot.status-cancelled {

  background: #db4545;
}


.estado.status-default {

  background: #eef2f5;

  color: #687c8d;
}


.status-dot.status-default {

  background: #8798a6;
}


/* =========================================================
   ESTADO VACÍO
========================================================= */

.empty {

  padding: 30px;

  text-align: center;

  color: #788794;

  font-size: 10px;
}


.empty-state {

  padding:
    35px
    20px;

  text-align: center;
}


.empty-icon {

  width: 42px;

  height: 42px;

  margin:
    0
    auto
    10px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  background: #eaf3fb;

  color: #07518d;

  font-size: 9px;

  font-weight: 900;
}


.empty-state h3 {

  margin: 0;

  color: #314a5e;

  font-size: 13px;
}


.empty-state p {

  max-width: 470px;

  margin:
    7px
    auto
    14px;

  color: #84929d;

  font-size: 9px;

  line-height: 1.5;
}


/* =========================================================
   ERROR
========================================================= */

.error-box {

  padding: 14px;

  border-radius: 7px;

  background: #fdecec;

  color: #a83232;

  font-size: 10px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 1100px
) {

  .cards {

    grid-template-columns:
      1fr;
  }

}


@media (
  max-width: 1000px
) {

  .stats-grid {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 760px
) {

  .usuario-layout {

    display: block;
  }


  .usuario-content {

    padding: 18px;
  }


  .topbar {

    align-items:
      flex-start;

    flex-direction:
      column;
  }


  .user-card {

    justify-content:
      flex-start;
  }


  .recent-header {

    align-items:
      flex-start;
  }


  .ticket-list article {

    align-items:
      flex-start;

    flex-direction:
      column;
  }


  .ticket-actions {

    width: 100%;

    justify-content:
      space-between;
  }

}


@media (
  max-width: 480px
) {

  .stats-grid {

    grid-template-columns:
      1fr;
  }

}

</style>
