<template>
  <div class="layout">

    <AdminMenu />

    <main class="main">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->
      <header class="page-header">

        <div>
          <h1>
            Solicitudes
          </h1>

          <p>
            Registros de solicitudes de compra y Caja Chica.
          </p>
        </div>

        <div class="header-actions">

          <select
            v-model="filtroEstado"
            class="filtro-estado"
          >
            <option value="">Todas las solicitudes</option>
            <option value="APROBADA">Solicitudes aprobadas</option>
            <option value="RECHAZADA">Solicitudes rechazadas</option>
          </select>

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

        </div>

      </header>


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
           SIN REGISTROS
      ================================================== -->
      <div
        v-else-if="compras.length === 0"
        class="empty"
      >
        No existen solicitudes de compra registradas.
      </div>


      <div
        v-else-if="comprasFiltradas.length === 0"
        class="empty"
      >
        No hay {{ etiquetaFiltroVacio(filtroEstado) }}.
      </div>


      <!-- =================================================
           LISTADO
      ================================================== -->
      <section
        v-else
        class="requests-card"
      >

        <div class="request-list">

          <article
            v-for="compra in comprasFiltradas"
            :key="compra.id"
            class="request"
          >

            <div class="request-main">

              <div class="request-code">
                <strong>
                  {{ compra.codigo }}
                </strong>

                <small>
                  {{ compra.area_nombre || 'Área no indicada' }}
                </small>
              </div>


              <div class="request-info">

                <h3>
                  {{
                    compra.titulo
                    || compra.descripcion
                    || 'Solicitud de compra'
                  }}
                </h3>

                <div class="meta">

                  <span>
                    {{
                      compra.solicitante_nombre
                      || compra.solicitante_email
                      || 'Sin información'
                    }}
                  </span>

                  <span>
                    {{
                      compra.via_nombre
                      || 'Vía no indicada'
                    }}
                  </span>

                  <span v-if="compra.creado_en">
                    {{ formatearFecha(compra.creado_en) }}
                  </span>

                </div>

              </div>

            </div>


            <div class="request-side">

              <span
                :class="['status', claseBucket(bucketEstado(compra.estado))]"
              >
                {{ etiquetaBucket(bucketEstado(compra.estado)) }}
              </span>

              <button
                class="view"
                @click="verDetalle(compra)"
              >
                Ver detalle
              </button>

            </div>

          </article>

        </div>

      </section>

    </main>


    <!-- =================================================
         DOCUMENTO DE DETALLE
    ================================================== -->

    <div
      v-if="mostrarDetalle"
      class="detalle-modal-backdrop"
      @click.self="cerrarDetalle"
    >
      <div class="detalle-modal documento-modal">

        <div class="detalle-modal-header">
          <div>
            <h3>{{ compraSeleccionada?.codigo }}</h3>
            <small>{{ compraSeleccionada?.titulo }}</small>
          </div>

          <button
            class="detalle-modal-close"
            @click="cerrarDetalle"
          >✕</button>
        </div>

        <div class="documento-body">

          <div
            :class="['estado-banner', claseBucket(bucketEstado(compraSeleccionada?.estado))]"
          >
            {{ etiquetaBucket(bucketEstado(compraSeleccionada?.estado)) }}
          </div>


          <div class="documento-seccion">

            <span class="documento-titulo">
              Producto o servicio a comprar
            </span>

            <h4>{{ compraSeleccionada?.titulo || 'Sin título' }}</h4>

            <p>{{ compraSeleccionada?.descripcion || 'Sin descripción registrada.' }}</p>


            <div class="documento-fila">

              <div>
                <b>Tipo</b>
                <span>{{ compraSeleccionada?.tipo_nombre || compraSeleccionada?.tipo || 'No indicado' }}</span>
              </div>

              <div>
                <b>Cantidad</b>
                <span>{{ compraSeleccionada?.cantidad || 1 }}</span>
              </div>

              <div>
                <b>Monto estimado</b>
                <span>
                  {{
                    compraSeleccionada?.monto_estimado
                      ? `Bs ${Number(compraSeleccionada.monto_estimado).toFixed(2)}`
                      : 'No indicado'
                  }}
                </span>
              </div>

            </div>


            <b>Especificaciones</b>
            <p>{{ compraSeleccionada?.especificaciones || 'No registradas.' }}</p>

            <b>Justificación</b>
            <p>{{ compraSeleccionada?.justificacion || 'No registrada.' }}</p>

          </div>


          <div class="documento-seccion">

            <span class="documento-titulo">
              Datos del expediente
            </span>

            <div class="documento-fila">

              <div>
                <b>Solicitante</b>
                <span>
                  {{
                    compraSeleccionada?.solicitante_nombre
                    || compraSeleccionada?.solicitante_email
                    || 'Sin información'
                  }}
                </span>
              </div>

              <div>
                <b>Área</b>
                <span>{{ compraSeleccionada?.area_nombre || 'No indicada' }}</span>
              </div>

              <div>
                <b>Vía de adquisición</b>
                <span>{{ compraSeleccionada?.via_nombre || 'No indicada' }}</span>
              </div>

            </div>

            <div class="documento-fila">

              <div>
                <b>Fecha de registro</b>
                <span>{{ formatearFecha(compraSeleccionada?.creado_en) }}</span>
              </div>

              <div v-if="compraSeleccionada?.monto_desembolsado">
                <b>Monto desembolsado</b>
                <span>Bs {{ Number(compraSeleccionada.monto_desembolsado).toFixed(2) }}</span>
              </div>

            </div>

          </div>


          <div
            class="documento-seccion motivo-rechazo"
            v-if="compraSeleccionada?.motivo_rechazo"
          >
            <span class="documento-titulo">
              Motivo de rechazo
            </span>

            <p>{{ compraSeleccionada.motivo_rechazo }}</p>
          </div>


          <!-- ACCIONES -->

          <div
            v-if="bucketEstado(compraSeleccionada?.estado) === 'EN_ESPERA'"
            class="documento-acciones"
          >

            <template v-if="puedeDecidir(compraSeleccionada)">

              <p
                v-if="errorAccion"
                class="accion-error"
              >
                {{ errorAccion }}
              </p>

              <div
                v-if="!mostrarFormRechazo"
                class="acciones-botones"
              >
                <button
                  class="btn-aprobar"
                  :disabled="procesando"
                  @click="aprobarCompra"
                >
                  Aprobar
                </button>

                <button
                  class="btn-rechazar"
                  :disabled="procesando"
                  @click="abrirFormRechazo"
                >
                  Rechazar
                </button>
              </div>

              <div
                v-else
                class="form-rechazo"
              >
                <label>
                  Motivo del rechazo
                  <span>*</span>
                </label>

                <textarea
                  v-model="motivoRechazoTexto"
                  rows="3"
                  placeholder="Explique por qué se rechaza esta solicitud..."
                ></textarea>

                <div class="acciones-botones">

                  <button
                    class="btn-cancelar"
                    :disabled="procesando"
                    @click="cancelarRechazo"
                  >
                    Cancelar
                  </button>

                  <button
                    class="btn-rechazar"
                    :disabled="procesando"
                    @click="confirmarRechazo"
                  >
                    Confirmar rechazo
                  </button>

                </div>
              </div>

            </template>

            <p
              v-else
              class="nota-tramite"
            >
              Este expediente está en trámite interno (documentación de
              DAF/Tesorería) y todavía no requiere una decisión de aprobación.
            </p>

          </div>

        </div>

      </div>
    </div>

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
// FILTRO
// ==========================================================

const filtroEstado =
  ref('')

const comprasFiltradas =
  computed(() => {

    if (!filtroEstado.value) {
      return compras.value
    }

    return compras.value.filter(
      compra =>
        bucketEstado(compra.estado)
        === filtroEstado.value
    )
  })


// ==========================================================
// DETALLE (DOCUMENTO)
// ==========================================================

const mostrarDetalle =
  ref(false)

const compraSeleccionada =
  ref(null)

const procesando =
  ref(false)

const mostrarFormRechazo =
  ref(false)

const motivoRechazoTexto =
  ref('')

const errorAccion =
  ref('')


function verDetalle(
  compra
) {

  compraSeleccionada.value =
    compra

  mostrarDetalle.value =
    true

  mostrarFormRechazo.value =
    false

  motivoRechazoTexto.value =
    ''

  errorAccion.value =
    ''
}


function cerrarDetalle() {

  mostrarDetalle.value =
    false

  compraSeleccionada.value =
    null

  mostrarFormRechazo.value =
    false

  motivoRechazoTexto.value =
    ''

  errorAccion.value =
    ''
}


// ==========================================================
// DECISIÓN (APROBAR / RECHAZAR)
// ==========================================================
//
// Solo hay una decisión simple de sí/no en dos momentos del
// flujo: la evaluación inicial de DAF (CREADO_PENDIENTE_DAF)
// y el visto bueno final del Director (VERIFICADO_PENDIENTE_
// AUTORIZACION). Los pasos intermedios (certificación DAF con
// PDF, verificación de Tesorería con 5 documentos) requieren
// más que un botón y se completan en sus propios flujos.
// ==========================================================

function puedeDecidir(
  compra
) {

  const estado =
    compra?.estado

  return (
    estado === 'CREADO_PENDIENTE_DAF'
    ||
    estado === 'VERIFICADO_PENDIENTE_AUTORIZACION'
  )
}


function abrirFormRechazo() {

  mostrarFormRechazo.value =
    true

  motivoRechazoTexto.value =
    ''

  errorAccion.value =
    ''
}


function cancelarRechazo() {

  mostrarFormRechazo.value =
    false

  motivoRechazoTexto.value =
    ''

  errorAccion.value =
    ''
}


async function aprobarCompra() {

  if (!compraSeleccionada.value) {
    return
  }

  const confirmar =
    window.confirm(
      `¿Confirma aprobar la solicitud ${compraSeleccionada.value.codigo}?`
    )

  if (!confirmar) {
    return
  }

  const estado =
    compraSeleccionada.value.estado

  const endpoint =
    estado === 'CREADO_PENDIENTE_DAF'
      ? 'evaluar-daf'
      : 'visto-bueno-director'

  const body =
    estado === 'CREADO_PENDIENTE_DAF'
      ? { califica: true }
      : {}

  await ejecutarAccion(
    endpoint,
    body,
    'aprobar'
  )
}


async function confirmarRechazo() {

  const motivo =
    motivoRechazoTexto.value.trim()

  if (!motivo) {

    errorAccion.value =
      'Debe indicar el motivo del rechazo.'

    return
  }

  const estado =
    compraSeleccionada.value.estado

  const endpoint =
    estado === 'CREADO_PENDIENTE_DAF'
      ? 'evaluar-daf'
      : 'rechazar'

  const body =
    estado === 'CREADO_PENDIENTE_DAF'
      ? { califica: false, motivo }
      : { motivo }

  await ejecutarAccion(
    endpoint,
    body,
    'rechazar'
  )
}


async function ejecutarAccion(
  endpoint,
  body,
  tipo
) {

  procesando.value =
    true

  errorAccion.value =
    ''

  try {

    const respuesta =
      await fetch(
        `/api/compras/solicitudes/${compraSeleccionada.value.id}/${endpoint}/`,
        {
          method: 'POST',
          headers: {
            Authorization: `Token ${token()}`,
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: JSON.stringify(body),
        }
      )

    let datos = {}

    try {
      datos = await respuesta.json()
    } catch {
      datos = {}
    }

    if (
      respuesta.status === 401
      ||
      respuesta.status === 403
    ) {

      cerrarSesion()

      return
    }

    if (!respuesta.ok) {

      errorAccion.value =
        datos.detalle
        || `No fue posible ${tipo === 'aprobar' ? 'aprobar' : 'rechazar'} la solicitud.`

      return
    }

    cerrarDetalle()

    await cargarCompras()

  } catch (error) {

    console.error(
      'Error ejecutando la decisión:',
      error
    )

    errorAccion.value =
      'No fue posible comunicarse con el servidor.'

  } finally {

    procesando.value =
      false
  }
}


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
      .sort(
        (a, b) => {

          const fechaA =
            new Date(a.creado_en || 0).getTime()

          const fechaB =
            new Date(b.creado_en || 0).getTime()

          return fechaB - fechaA
        }
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
// ESTADO (AGRUPACIÓN VISUAL SIMPLIFICADA)
// ==========================================================
//
// Estados reales del modelo SolicitudCompra (flujo de Caja
// Chica): CREADO_PENDIENTE_DAF, EVALUADO_PENDIENTE_CERTIFICACION,
// CERTIFICADO_PENDIENTE_VERIFICACION, VERIFICADO_PENDIENTE_AUTORIZACION,
// APROBADO_PARA_DESEMBOLSO, FONDOS_DESEMBOLSADOS, COMPRA_REGISTRADA,
// COMPRADO_Y_ENTREGADO, DESCARGO_PENDIENTE_LIQUIDACION,
// CERRADO_ARCHIVADO, RECHAZADO, ANULADO.
//
// Se agrupan en 3 buckets para el solicitante/administrador:
// EN_ESPERA, APROBADA, RECHAZADA.
// ==========================================================

function bucketEstado(
  estado
) {

  const codigo =
    String(
      estado
      || ''
    )
      .trim()
      .toUpperCase()


  if (
    codigo === 'RECHAZADO'
    ||
    codigo === 'ANULADO'
  ) {

    return 'RECHAZADA'
  }


  if (
    codigo === 'APROBADO_PARA_DESEMBOLSO'
    ||
    codigo === 'FONDOS_DESEMBOLSADOS'
    ||
    codigo === 'COMPRA_REGISTRADA'
    ||
    codigo === 'COMPRADO_Y_ENTREGADO'
    ||
    codigo === 'DESCARGO_PENDIENTE_LIQUIDACION'
    ||
    codigo === 'CERRADO_ARCHIVADO'
  ) {

    return 'APROBADA'
  }


  return 'EN_ESPERA'
}


function etiquetaBucket(
  bucket
) {

  return (
    {
      EN_ESPERA: 'Aprobación en espera',
      APROBADA: 'Aprobada',
      RECHAZADA: 'Rechazada',
    }[bucket]
    || bucket
  )
}


function etiquetaFiltroVacio(
  bucket
) {

  return (
    {
      APROBADA: 'solicitudes aprobadas',
      RECHAZADA: 'solicitudes rechazadas',
    }[bucket]
    || 'solicitudes'
  )
}


function claseBucket(
  bucket
) {

  return (
    {
      EN_ESPERA: 'working',
      APROBADA: 'closed',
      RECHAZADA: 'cancelled',
    }[bucket]
    || 'working'
  )
}


// ==========================================================
// FECHA
// ==========================================================

function formatearFecha(
  fecha
) {

  if (!fecha) {

    return ''
  }


  try {

    return new Date(
      fecha
    ).toLocaleString(
      'es-BO',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      }
    )

  } catch {

    return ''
  }
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


.page-header h1 {
  margin: 0;
  color: #17324a;
  font-size: 33px;
}


.page-header p {
  margin: 5px 0 0;
  color: #718294;
  font-size: 17px;
}


.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}


.filtro-estado {
  min-height: 41px;
  padding: 0 12px;
  border: 1px solid #d0dae2;
  border-radius: 7px;
  background: white;
  color: #17324a;
  font-family: inherit;
  font-size: 15px;
  outline: none;
}


.refresh-button {
  min-height: 41px;
  padding: 0 15px;
  border: 1px solid #073b6f;
  border-radius: 7px;
  background: white;
  color: #073b6f;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
}


.refresh-button:disabled {
  opacity: .6;
  cursor: not-allowed;
}


/* =========================================================
   LISTADO
========================================================= */

.requests-card {
  overflow: hidden;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
}


.request-list {
  display: flex;
  flex-direction: column;
}


.request {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 17px 20px;
  border-bottom: 1px solid #edf0f2;
}


.request:last-child {
  border-bottom: none;
}


.request-main {
  flex: 1;
  min-width: 0;
  display: grid;
  grid-template-columns: 155px 1fr;
  gap: 15px;
}


.request-code strong {
  display: block;
  color: #07518d;
  font-size: 15px;
}


.request-code small {
  display: block;
  margin-top: 4px;
  color: #81909c;
  font-size: 13px;
}


.request-info h3 {
  margin: 0 0 5px;
  color: #29475e;
  font-size: 18px;
}


.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}


.meta span {
  padding: 4px 6px;
  border-radius: 4px;
  background: #f3f6f8;
  color: #687986;
  font-size: 13px;
}


.request-side {
  flex-shrink: 0;
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  gap: 9px;
}


/* =========================================================
   ESTADO
========================================================= */

.status {
  display: inline-block;
  padding: 5px 8px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 800;
}


.status.working {
  background: #fff6d9;
  color: #866400;
}


.status.closed {
  background: #e8f6ee;
  color: #237345;
}


.status.cancelled {
  background: #fdeaea;
  color: #a53232;
}


.view {
  padding: 6px 8px;
  border: none;
  border-radius: 5px;
  background: #edf3f8;
  color: #435a6e;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}


/* =========================================================
   VACÍOS
========================================================= */

.loading,
.empty {
  padding: 45px 20px;
  text-align: center;
  color: #798793;
  font-size: 16px;
}


.empty {
  border-radius: 10px;
  background: white;
}


/* =========================================================
   DOCUMENTO DE DETALLE
========================================================= */

.documento-modal {
  max-width: 620px;
}


.documento-body {
  padding: 18px 22px 22px;
}


.estado-banner {
  margin-bottom: 18px;
  padding: 12px 16px;
  border-radius: 8px;
  text-align: center;
  font-size: 16px;
  font-weight: 800;
}


.estado-banner.working {
  background: #fff6d9;
  color: #866400;
}


.estado-banner.closed {
  background: #e8f6ee;
  color: #237345;
}


.estado-banner.cancelled {
  background: #fdeaea;
  color: #a53232;
}


.documento-seccion {
  padding: 16px 0;
  border-top: 1px solid #edf0f2;
}


.documento-seccion:first-of-type {
  border-top: none;
  padding-top: 0;
}


.documento-titulo {
  display: block;
  margin-bottom: 8px;
  color: #8592a0;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.documento-seccion h4 {
  margin: 0 0 6px;
  color: #17324a;
  font-size: 18px;
}


.documento-seccion > p {
  margin: 0 0 10px;
  color: #354d60;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
}


.documento-seccion b {
  display: block;
  margin-bottom: 4px;
  color: #8592a0;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .5px;
  text-transform: uppercase;
}


.documento-fila {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 12px;
  margin-bottom: 12px;
}


.documento-fila > div span {
  display: block;
  color: #26333f;
  font-size: 14px;
}


.motivo-rechazo {
  padding: 14px;
  border: none;
  border-radius: 8px;
  background: #fdecec;
}


.motivo-rechazo .documento-titulo {
  color: #a53232;
}


.motivo-rechazo p {
  margin: 0;
  color: #7a2828;
  font-size: 14px;
  line-height: 1.5;
}


/* =========================================================
   ACCIONES DE DECISIÓN
========================================================= */

.documento-acciones {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #edf0f2;
}


.nota-tramite {
  margin: 0;
  padding: 12px 14px;
  border-radius: 7px;
  background: #eef3f8;
  color: #536575;
  font-size: 14px;
  line-height: 1.5;
}


.accion-error {
  margin: 0 0 10px;
  padding: 10px 12px;
  border-radius: 7px;
  background: #fdecec;
  color: #a53232;
  font-size: 14px;
}


.acciones-botones {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}


.btn-aprobar,
.btn-rechazar,
.btn-cancelar {
  min-height: 40px;
  padding: 0 16px;
  border: none;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}


.btn-aprobar {
  background: #237345;
  color: white;
}


.btn-rechazar {
  background: #a53232;
  color: white;
}


.btn-cancelar {
  background: #edf0f2;
  color: #435a6e;
}


.btn-aprobar:disabled,
.btn-rechazar:disabled,
.btn-cancelar:disabled {
  opacity: .6;
  cursor: not-allowed;
}


.form-rechazo label {
  display: block;
  margin-bottom: 6px;
  color: #344a5d;
  font-size: 14px;
  font-weight: 700;
}


.form-rechazo label span {
  color: #a53232;
}


.form-rechazo textarea {
  width: 100%;
  margin-bottom: 10px;
  padding: 10px 12px;
  border: 1px solid #d0dae2;
  border-radius: 7px;
  background: white;
  color: #26333f;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  outline: none;
}


/* =========================================================
   RESPONSIVE
========================================================= */

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


  .header-actions {
    width: 100%;
  }


  .filtro-estado {
    flex: 1;
  }


  .request {
    align-items: flex-start;
    flex-direction: column;
  }


  .request-main {
    grid-template-columns: 1fr;
  }


  .request-side {
    width: 100%;
    align-items: flex-start;
  }


  .documento-fila {
    grid-template-columns: 1fr;
  }

}

</style>
