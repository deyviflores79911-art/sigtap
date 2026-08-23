<template>
  <div class="layout">

    <AdminMenu />

    <main class="main">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->
      <header class="page-header">

        <div>
          <span class="breadcrumb">
            SIGTA / Operación / Compras
          </span>

          <h1>
            Compras
          </h1>

          <p>
            Gestión y seguimiento de solicitudes de compra,
            Caja Chica y adquisición institucional.
          </p>
        </div>

        <button
          class="refresh-button"
          type="button"
          :disabled="cargando"
          @click="cargarCompras"
        >
          {{
            cargando
              ? 'Actualizando...'
              : 'Actualizar'
          }}
        </button>

      </header>


      <!-- =================================================
           INDICADORES
      ================================================== -->
      <section class="metrics">

        <article>
          <span>
            Solicitudes de compra
          </span>

          <strong>
            {{ compras.length }}
          </strong>

          <small>
            Solicitudes registradas
          </small>
        </article>


        <article>
          <span>
            Caja Chica
          </span>

          <strong>
            {{ cajaChica }}
          </strong>

          <small>
            Solicitudes hasta Bs 1.500
          </small>
        </article>


        <article>
          <span>
            Finanzas
          </span>

          <strong>
            {{ fueraCaja }}
          </strong>

          <small>
            Solicitudes mayores a Bs 1.500
          </small>
        </article>


        <article>
          <span>
            Cerradas
          </span>

          <strong>
            {{ cerradas }}
          </strong>

          <small>
            Solicitudes concluidas
          </small>
        </article>

      </section>


      <!-- =================================================
           FLUJO BPMN
      ================================================== -->
      <section class="flow-summary">

        <div>
          <span class="section-label">
            FLUJO DE COMPRAS
          </span>

          <strong>
            Seguimiento del proceso de adquisición
          </strong>

          <p>
            La interfaz utiliza las mismas actividades
            institucionales definidas en el BPMN de Compras.
          </p>
        </div>

        <div class="flow-steps">
          <span>Cargar expediente de compra</span>
          <span>Autorizar gasto</span>
          <span>Certificar presupuesto disponible</span>
          <span>Derivar trámite</span>
          <span>Registrar verificación de componentes</span>
          <span>Registrar desembolso de dinero</span>
          <span>Registrar ingreso al almacén</span>
          <span>Registrar despacho desde almacén</span>
        </div>

      </section>


      <!-- =================================================
           CARGANDO
      ================================================== -->
      <div
        v-if="cargando"
        class="loading"
      >
        Cargando solicitudes de compra...
      </div>


      <!-- =================================================
           TABLERO
      ================================================== -->
      <section
        v-else
        class="board-section"
      >

        <div class="board-header">

          <div>
            <span class="section-label">
              SEGUIMIENTO DE SOLICITUDES
            </span>

            <h2>
              Estado de las compras
            </h2>
          </div>

          <span class="result-count">
            {{ compras.length }} solicitud(es)
          </span>

        </div>


        <div class="board-scroll">

          <div class="kanban">

            <section
              v-for="columna in columnas"
              :key="columna.codigo"
              class="column"
            >

              <header class="column-header">

                <div>
                  <strong>
                    {{ columna.nombre }}
                  </strong>

                  <small>
                    {{ columna.descripcion }}
                  </small>
                </div>

                <span>
                  {{ comprasPorEstado(columna.codigo).length }}
                </span>

              </header>


              <div class="column-body">

                <article
                  v-for="compra in comprasPorEstado(columna.codigo)"
                  :key="compra.id"
                  class="card"
                >

                  <div class="card-top">

                    <strong class="code">
                      {{ compra.codigo }}
                    </strong>

                    <span
                      :class="[
                        'via-badge',
                        claseVia(compra.via_adquisicion)
                      ]"
                    >
                      {{ textoVia(compra) }}
                    </span>

                  </div>


                  <h3>
                    {{
                      compra.titulo
                      || compra.descripcion
                      || 'Solicitud de compra'
                    }}
                  </h3>


                  <div class="card-info">

                    <div>
                      <span>
                        Área solicitante
                      </span>

                      <strong>
                        {{
                          compra.area_nombre
                          || 'No indicada'
                        }}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Tipo
                      </span>

                      <strong>
                        {{
                          compra.tipo_nombre
                          || compra.tipo
                          || 'No indicado'
                        }}
                      </strong>
                    </div>


                    <div>
                      <span>
                        Cantidad
                      </span>

                      <strong>
                        {{
                          compra.cantidad
                          || 1
                        }}
                      </strong>
                    </div>

                  </div>


                  <div class="amount">
                    Bs
                    {{
                      Number(
                        compra.monto_estimado || 0
                      ).toFixed(2)
                    }}
                  </div>


                  <div class="card-footer">

                    <div>
                      <span>
                        Solicitante
                      </span>

                      <strong>
                        {{
                          compra.solicitante_nombre
                          || compra.solicitante_email
                          || 'Sin información'
                        }}
                      </strong>
                    </div>

                    <span class="state-badge">
                      {{
                        compra.estado_nombre
                        || nombreEstado(compra.estado)
                      }}
                    </span>

                  </div>

                </article>


                <div
                  v-if="comprasPorEstado(columna.codigo).length === 0"
                  class="empty-column"
                >
                  Sin solicitudes
                </div>

              </div>

            </section>

          </div>

        </div>

      </section>


      <!-- =================================================
           SIN REGISTROS
      ================================================== -->
      <div
        v-if="
          !cargando
          && compras.length === 0
        "
        class="empty"
      >
        No existen solicitudes de compra registradas.
      </div>

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

import AdminMenu
  from '../components/AdminMenu.vue'


const router =
  useRouter()


// ==========================================================
// DATOS
// ==========================================================

const compras =
  ref([])

const cargando =
  ref(true)


// ==========================================================
// COLUMNAS DEL ESTADO ACTUAL DEL BACKEND
// ==========================================================
//
// IMPORTANTE:
// Se conservan los códigos existentes del modelo de Compras.
// Solo se modifica el lenguaje visible de la interfaz.
//
// ==========================================================

const columnas = [

  {
    codigo: 'NUEVO',
    nombre: 'Solicitud registrada',
    descripcion: 'Cargar expediente de compra',
  },

  {
    codigo: 'EN_COTIZACION',
    nombre: 'En cotización',
    descripcion: 'Preparación del expediente',
  },

  {
    codigo: 'EN_APROBACION',
    nombre: 'En aprobación',
    descripcion: 'Autorizar gasto',
  },

  {
    codigo: 'APROBADO',
    nombre: 'Aprobado',
    descripcion: 'Presupuesto autorizado',
  },

  {
    codigo: 'ORDEN_EMITIDA',
    nombre: 'Orden emitida',
    descripcion: 'Derivar trámite',
  },

  {
    codigo: 'EN_TRANSITO',
    nombre: 'En proceso de compra',
    descripcion: 'Adquisición / desembolso',
  },

  {
    codigo: 'RECIBIDO',
    nombre: 'Recibido',
    descripcion: 'Registrar ingreso al almacén',
  },

  {
    codigo: 'EN_VERIFICACION',
    nombre: 'En verificación',
    descripcion: 'Verificar componentes',
  },

  {
    codigo: 'CERRADO',
    nombre: 'Cerrado',
    descripcion: 'Registrar despacho desde almacén',
  },

]


// ==========================================================
// TOKEN
// ==========================================================

function token() {

  return localStorage.getItem(
    'sigta_token'
  )
}


// ==========================================================
// INICIO
// ==========================================================

onMounted(
  async () => {

    if (!token()) {

      router.push(
        '/login'
      )

      return
    }


    await cargarCompras()
  }
)


// ==========================================================
// NORMALIZAR
// ==========================================================

function normalizarLista(
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
// CARGAR COMPRAS
// ==========================================================

async function cargarCompras() {

  cargando.value =
    true


  try {

    const respuesta =
      await fetch(
        '/api/compras/solicitudes/',
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

      return
    }


    if (!respuesta.ok) {

      console.error(
        'Compras:',
        respuesta.status
      )

      compras.value = []

      return
    }


    const datos =
      await respuesta.json()


    compras.value =
      normalizarLista(
        datos
      )


  } catch (error) {

    console.error(
      'Error cargando compras:',
      error
    )

    compras.value = []


  } finally {

    cargando.value =
      false
  }
}


// ==========================================================
// INDICADORES
// ==========================================================

const cajaChica =
  computed(() => {

    return compras.value.filter(
      compra => {

        if (
          compra.via_adquisicion
          ===
          'CAJA_CHICA'
        ) {

          return true
        }


        return Number(
          compra.monto_estimado
          || 0
        ) <= 1500
      }
    ).length
  })


const fueraCaja =
  computed(() => {

    return compras.value.filter(
      compra => {

        if (
          compra.via_adquisicion
          ===
          'FINANZAS'
        ) {

          return true
        }


        return Number(
          compra.monto_estimado
          || 0
        ) > 1500
      }
    ).length
  })


const cerradas =
  computed(() => {

    return compras.value.filter(
      compra =>
        compra.estado
        ===
        'CERRADO'
    ).length
  })


// ==========================================================
// ESTADOS
// ==========================================================

function comprasPorEstado(
  estado
) {

  return compras.value.filter(
    compra =>
      String(
        compra.estado
        || ''
      )
        .trim()
        .toUpperCase()
      ===
      estado
  )
}


function nombreEstado(
  estado
) {

  const nombres = {

    NUEVO:
      'Solicitud registrada',

    EN_COTIZACION:
      'En cotización',

    EN_APROBACION:
      'En aprobación',

    APROBADO:
      'Aprobado',

    ORDEN_EMITIDA:
      'Orden emitida',

    EN_TRANSITO:
      'En proceso de compra',

    RECIBIDO:
      'Recibido',

    EN_VERIFICACION:
      'En verificación',

    CERRADO:
      'Cerrado',

    RECHAZADO:
      'Rechazado',

    ANULADO:
      'Anulado',
  }


  return (
    nombres[estado]
    ||
    estado
    ||
    'Sin estado'
  )
}


// ==========================================================
// VÍA DE ADQUISICIÓN
// ==========================================================

function textoVia(
  compra
) {

  if (
    compra.via_nombre
  ) {

    return compra.via_nombre
  }


  if (
    compra.via_adquisicion
    ===
    'CAJA_CHICA'
  ) {

    return 'Caja Chica'
  }


  if (
    compra.via_adquisicion
    ===
    'FINANZAS'
  ) {

    return 'Finanzas'
  }


  return Number(
    compra.monto_estimado
    || 0
  ) <= 1500
    ? 'Caja Chica'
    : 'Finanzas'
}


function claseVia(
  via
) {

  if (
    via ===
    'CAJA_CHICA'
  ) {

    return 'small-purchase'
  }


  if (
    via ===
    'FINANZAS'
  ) {

    return 'finance'
  }


  return 'pending'
}


// ==========================================================
// SESIÓN
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

.layout {
  min-height: 100vh;
  display: flex;
  background: #f2f5f9;
  font-family: Arial, Helvetica, sans-serif;
}


.main {
  flex: 1;
  min-width: 0;
  padding: 27px;
  overflow-x: hidden;
}


/* =========================================================
   HEADER
========================================================= */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  margin-bottom: 20px;
}


.breadcrumb {
  display: block;
  margin-bottom: 6px;
  color: #8594a1;
  font-size: 9px;
}


.page-header h1 {
  margin: 0;
  color: #17324a;
  font-size: 27px;
}


.page-header p {
  margin: 5px 0 0;
  color: #718294;
  font-size: 11px;
}


.refresh-button {
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid #073b6f;
  border-radius: 7px;
  background: white;
  color: #073b6f;
  font-size: 9px;
  font-weight: 800;
  cursor: pointer;
}


.refresh-button:disabled {
  opacity: .6;
  cursor: not-allowed;
}


/* =========================================================
   MÉTRICAS
========================================================= */

.metrics {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 13px;
  margin-bottom: 17px;
}


.metrics article {
  min-height: 105px;
  padding: 17px;
  border-top: 4px solid #f2c400;
  border-radius: 9px;
  background: white;
  box-shadow: 0 3px 12px rgba(0,0,0,.05);
}


.metrics span,
.metrics small {
  display: block;
}


.metrics span {
  color: #718294;
  font-size: 8px;
  font-weight: 800;
  text-transform: uppercase;
}


.metrics strong {
  display: block;
  margin: 7px 0 4px;
  color: #073b6f;
  font-size: 26px;
}


.metrics small {
  color: #8593a0;
  font-size: 8px;
}


/* =========================================================
   FLUJO
========================================================= */

.flow-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 17px;
  padding: 15px 17px;
  border-left: 4px solid #f2c400;
  border-radius: 8px;
  background: white;
}


.section-label {
  display: block;
  margin-bottom: 4px;
  color: #07518d;
  font-size: 7px;
  font-weight: 900;
  letter-spacing: .8px;
}


.flow-summary strong {
  color: #17324a;
  font-size: 11px;
}


.flow-summary p {
  margin: 4px 0 0;
  color: #778895;
  font-size: 8px;
}


.flow-steps {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 5px;
}


.flow-steps span {
  padding: 5px 7px;
  border-radius: 5px;
  background: #edf3f7;
  color: #557185;
  font-size: 7px;
}


/* =========================================================
   TABLERO
========================================================= */

.board-section {
  padding: 17px;
  border-radius: 9px;
  background: white;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
}


.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 13px;
}


.board-header h2 {
  margin: 0;
  color: #17324a;
  font-size: 16px;
}


.result-count {
  padding: 5px 8px;
  border-radius: 20px;
  background: #edf4fa;
  color: #07518d;
  font-size: 7px;
  font-weight: 800;
}


.board-scroll {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 12px;
}


.board-scroll::-webkit-scrollbar {
  height: 11px;
}


.board-scroll::-webkit-scrollbar-track {
  background: #dfe6ed;
  border-radius: 10px;
}


.board-scroll::-webkit-scrollbar-thumb {
  background: #66819c;
  border-radius: 10px;
}


.kanban {
  width: max-content;
  min-width: max-content;
  display: flex;
  gap: 10px;
}


.column {
  width: 225px;
  min-width: 225px;
  flex-shrink: 0;
}


.column-header {
  min-height: 57px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 7px;
  padding: 9px 10px;
  border-radius: 7px 7px 0 0;
  background: #dce8f5;
}


.column-header strong {
  display: block;
  color: #173a5b;
  font-size: 9px;
}


.column-header small {
  display: block;
  margin-top: 3px;
  color: #72889a;
  font-size: 7px;
}


.column-header > span {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #073b6f;
  color: white;
  font-size: 8px;
  font-weight: 900;
}


.column-body {
  min-height: 440px;
  padding: 8px;
  border-radius: 0 0 7px 7px;
  background: #e9eef5;
}


/* =========================================================
   TARJETA
========================================================= */

.card {
  margin-bottom: 8px;
  padding: 11px;
  border-left: 3px solid #073b6f;
  border-radius: 7px;
  background: white;
  box-shadow: 0 2px 7px rgba(0,0,0,.06);
}


.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}


.code {
  color: #07518d;
  font-size: 8px;
}


.card h3 {
  margin: 8px 0;
  color: #29475e;
  font-size: 10px;
  line-height: 1.4;
}


.card-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}


.card-info span,
.card-footer span {
  display: block;
  color: #93a0aa;
  font-size: 6px;
}


.card-info strong,
.card-footer strong {
  display: block;
  margin-top: 2px;
  color: #607587;
  font-size: 7px;
}


.amount {
  margin: 10px 0;
  padding: 8px;
  border-radius: 5px;
  background: #f4f7f9;
  color: #073b6f;
  font-size: 10px;
  font-weight: 900;
}


.card-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #edf0f3;
}


/* =========================================================
   VÍA
========================================================= */

.via-badge,
.state-badge {
  display: inline-block;
  padding: 4px 6px;
  border-radius: 5px;
  font-size: 6px;
  font-weight: 800;
}


.via-badge.small-purchase {
  background: #fff5d4;
  color: #765a00;
}


.via-badge.finance {
  background: #e8f2fa;
  color: #07518d;
}


.via-badge.pending {
  background: #edf0f2;
  color: #687986;
}


.state-badge {
  flex-shrink: 0;
  background: #edf3f7;
  color: #587183;
}


/* =========================================================
   VACÍOS
========================================================= */

.loading,
.empty,
.empty-column {
  padding: 28px 8px;
  color: #93a0ac;
  text-align: center;
  font-size: 8px;
}


.empty {
  margin-top: 14px;
  border-radius: 8px;
  background: white;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 1000px) {

  .metrics {
    grid-template-columns: repeat(2,1fr);
  }


  .flow-summary {
    align-items: flex-start;
    flex-direction: column;
  }


  .flow-steps {
    justify-content: flex-start;
  }
}


@media (max-width: 760px) {

  .layout {
    display: block;
  }


  .main {
    padding: 16px;
  }


  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }


  .metrics {
    grid-template-columns: 1fr;
  }
}

</style>
