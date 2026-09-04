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
            {{
              vista === 'PENDIENTES'
                ? 'Solicitudes'
                : 'Historial'
            }}
          </h1>

          <p v-if="vista === 'PENDIENTES'">
            {{ conteos.PENDIENTES }}
            {{ conteos.PENDIENTES === 1 ? 'solicitud' : 'solicitudes' }}
            de compra y Caja Chica pendientes de su decisión.
          </p>

          <p v-else>
            {{ conteos.APROBADA }}
            {{ conteos.APROBADA === 1 ? 'aprobada' : 'aprobadas' }}
            y
            {{ conteos.RECHAZADA }}
            {{ conteos.RECHAZADA === 1 ? 'rechazada' : 'rechazadas' }}.
            Solo consulta.
          </p>
        </div>

        <div class="header-actions">

          <select
            v-if="vista === 'HISTORIAL'"
            v-model="filtroHistorial"
            class="filtro-estado"
          >
            <option value="">Aprobadas y rechazadas</option>
            <option value="APROBADA">Solo aprobadas</option>
            <option value="RECHAZADA">Solo rechazadas</option>
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
        {{ mensajeVacio }}
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


                <!--
                  En el historial la fila debe explicar POR SÍ
                  SOLA cómo terminó la solicitud, sin obligar a
                  abrir el detalle de cada una.
                -->

                <p
                  v-if="vista === 'HISTORIAL' && compra.motivo_rechazo"
                  class="resolucion-motivo"
                >
                  <b>Motivo del rechazo:</b>
                  {{ compra.motivo_rechazo }}
                </p>

                <p
                  v-else-if="vista === 'HISTORIAL'"
                  class="resolucion-estado"
                >
                  {{ compra.estado_nombre || 'Sin detalle de estado' }}
                </p>

              </div>

            </div>


            <div class="request-side">

              <span
                :class="['status', claseBucket(bucketEstado(compra.estado))]"
              >
                {{ etiquetaBucket(bucketEstado(compra.estado)) }}
              </span>

              <div class="row-actions">

                <button
                  class="view"
                  @click="verDetalle(compra)"
                >
                  Ver detalle
                </button>

              </div>

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
          <div class="documento-header-titulo">

            <IconoSigta class="documento-header-icono" nombre="auditoria" :tamano="22" />

            <div>
              <h3>{{ compraSeleccionada?.codigo }}</h3>
              <small>{{ compraSeleccionada?.titulo }}</small>
            </div>

          </div>

          <button
            class="detalle-modal-close"
            @click="cerrarDetalle"
          >✕</button>
        </div>

        <div class="documento-body">

          <!--
            CABECERA DE DECISIÓN: los tres datos con los que el
            Director aprueba o rechaza (cuánto, por qué vía y si
            el expediente está completo), antes del detalle.
          -->

          <div class="decision-header">

            <div class="decision-dato">
              <b>Monto</b>
              <strong class="decision-monto">
                {{
                  compraSeleccionada?.monto_estimado
                    ? `Bs ${Number(compraSeleccionada.monto_estimado).toFixed(2)}`
                    : 'No indicado'
                }}
              </strong>
            </div>

            <div class="decision-dato">
              <b>Vía de adquisición</b>
              <strong>
                {{ compraSeleccionada?.via_nombre || 'No indicada' }}
              </strong>
            </div>

            <div class="decision-dato">
              <b>Expediente</b>
              <strong
                :class="[
                  'decision-expediente',
                  resumenExpediente.completo ? 'ok' : 'falta'
                ]"
              >
                {{ resumenExpediente.completo ? '✓' : '⚠' }}
                {{ resumenExpediente.adjuntos }} de
                {{ resumenExpediente.total }} documentos
              </strong>
            </div>

          </div>

          <div
            :class="['estado-banner', claseBucket(bucketEstado(compraSeleccionada?.estado))]"
          >
            <span class="estado-banner-icono">
              {{ iconoBucket(bucketEstado(compraSeleccionada?.estado)) }}
            </span>

            <div>
              <strong>{{ etiquetaBucket(bucketEstado(compraSeleccionada?.estado)) }}</strong>
              <span class="estado-banner-descripcion">
                {{ descripcionBucket(bucketEstado(compraSeleccionada?.estado)) }}
              </span>
            </div>
          </div>


          <div class="documento-seccion">

            <div class="documento-titulo-fila">
              <IconoSigta class="documento-icono" nombre="almacen" :tamano="22" />
              <span class="documento-titulo">
                Producto o servicio a comprar
              </span>
            </div>

            <h4>{{ compraSeleccionada?.titulo || 'Sin título' }}</h4>

            <p>{{ compraSeleccionada?.descripcion || 'Sin descripción registrada.' }}</p>


            <div class="documento-fila documento-fila-2">

              <div>
                <b>Tipo</b>
                <span>{{ compraSeleccionada?.tipo_nombre || compraSeleccionada?.tipo || 'No indicado' }}</span>
              </div>

              <div>
                <b>Cantidad</b>
                <span>{{ compraSeleccionada?.cantidad || 1 }}</span>
              </div>

            </div>

            <div
              v-if="especificacionesDistintas"
              class="documento-bloque"
            >
              <b>Especificaciones</b>
              <span>{{ compraSeleccionada?.especificaciones }}</span>
            </div>

            <div class="documento-bloque">
              <b>Justificación</b>
              <span>{{ compraSeleccionada?.justificacion || 'No registrada.' }}</span>
            </div>

          </div>


          <div class="documento-seccion">

            <div class="documento-titulo-fila">
              <IconoSigta class="documento-icono" nombre="solicitudes" :tamano="22" />
              <span class="documento-titulo">
                Datos del expediente
              </span>
            </div>

            <div class="documento-fila">

              <div>
                <b>Solicitante</b>
                <button
                  v-if="compraSeleccionada?.solicitante"
                  type="button"
                  class="solicitante-link"
                  @click="abrirSolicitante(compraSeleccionada.solicitante)"
                >
                  <span>
                    {{
                      compraSeleccionada?.solicitante_nombre
                      || 'Sin información'
                    }}
                  </span>
                  <small v-if="compraSeleccionada?.solicitante_email">
                    {{ compraSeleccionada.solicitante_email }}
                  </small>
                </button>
                <span v-else>Sin información</span>
              </div>

              <div>
                <b>Área</b>
                <span>{{ compraSeleccionada?.area_nombre || 'No indicada' }}</span>
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


          <div class="documento-seccion">

            <div class="documento-titulo-fila">
              <IconoSigta class="documento-icono" nombre="auditoria" :tamano="22" />
              <span class="documento-titulo">
                Documentos del expediente
              </span>
            </div>

            <div class="documento-lista">

              <template
                v-for="doc in documentosExpediente"
                :key="doc.label"
              >

                <a
                  v-if="doc.url"
                  :href="doc.url"
                  target="_blank"
                  class="documento-item ok"
                >
                  <IconoSigta class="documento-item-icono" nombre="auditoria" :tamano="22" />
                  <span class="documento-item-label">{{ doc.label }}</span>
                  <span class="documento-item-accion">
                    Ver archivo
                    <span class="documento-item-ojo">👁</span>
                  </span>
                </a>

                <div
                  v-else
                  class="documento-item falta"
                >
                  <IconoSigta class="documento-item-icono" nombre="auditoria" :tamano="22" />
                  <span class="documento-item-label">{{ doc.label }}</span>
                  <small>{{ doc.pendienteTexto || 'No adjuntado' }}</small>
                </div>

              </template>

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


        </div>


        <!--
          ACCIONES: viven FUERA de .documento-body (el que tiene
          el scroll) para quedar ancladas al pie del modal. Así
          la decisión está siempre visible y no hay que bajar
          hasta el final del expediente para aprobar o rechazar.
        -->

        <div
          v-if="bucketEstado(compraSeleccionada?.estado) === 'EN_ESPERA'"
          class="documento-acciones"
        >

          <p
            v-if="errorAccion"
            class="accion-error"
          >
            {{ errorAccion }}
          </p>

          <!--
            Mientras la DAF no emita la certificación
            presupuestaria, el Director no tiene nada que
            autorizar: la autorización es el paso siguiente.
            Puede rechazar, eso sí, que es válido en este estado.
          -->

          <p
            v-if="!mostrarFormRechazo && esperandoCertificacionDaf"
            class="nota-tramite"
          >
            Este expediente espera la certificación
            presupuestaria de la DAF. Podrá autorizarlo cuando
            la DAF la emita.
          </p>

          <div
            v-if="!mostrarFormRechazo"
            class="acciones-botones"
          >
            <button
              v-if="!esperandoCertificacionDaf"
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
            v-else-if="mostrarFormRechazo"
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

        </div>

      </div>
    </div>


    <!-- =================================================
         DATOS DEL SOLICITANTE
    ================================================== -->

    <div
      v-if="mostrarSolicitante"
      class="solicitante-modal-backdrop"
      @click.self="cerrarSolicitante"
    >
      <div class="detalle-modal">

        <div class="detalle-modal-header">
          <div>
            <h3>Datos del solicitante</h3>
          </div>

          <button
            class="detalle-modal-close"
            @click="cerrarSolicitante"
          >✕</button>
        </div>

        <div class="detalle-modal-body">

          <p
            v-if="cargandoSolicitante"
            class="detalle-vacio"
          >
            Cargando...
          </p>

          <template v-else-if="solicitanteDetalle">

            <div class="documento-fila">

              <div>
                <b>Nombre completo</b>
                <span>{{ solicitanteDetalle.nombre_completo || '—' }}</span>
              </div>

              <div>
                <b>Correo</b>
                <span>{{ solicitanteDetalle.email || '—' }}</span>
              </div>

            </div>

            <div class="documento-fila">

              <div>
                <b>Usuario</b>
                <span>{{ solicitanteDetalle.username || '—' }}</span>
              </div>

              <div>
                <b>Estado de la cuenta</b>
                <span>{{ solicitanteDetalle.is_active ? 'Activa' : 'Inactiva' }}</span>
              </div>

            </div>

            <div class="detalle-campo">
              <b>Roles</b>
              <span>
                {{
                  (solicitanteDetalle.roles || [])
                    .map(rol => rol.rol_nombre || rol.nombre)
                    .join(', ')
                  || 'Sin rol asignado'
                }}
              </span>
            </div>

          </template>

          <p
            v-else
            class="detalle-vacio"
          >
            No fue posible cargar los datos del solicitante.
          </p>

        </div>

      </div>
    </div>

  </div>
</template>


<script setup>
import IconoSigta from '../components/IconoSigta.vue'

import {
  computed,
  onMounted,
  ref
} from 'vue'

import {
  useRoute,
  useRouter
} from 'vue-router'

import AdminMenu
  from '../components/AdminMenu.vue'


const router =
  useRouter()

const route =
  useRoute()


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

// La bandeja se parte en dos entradas de menú que comparten
// este componente: "Solicitudes" (/admin/compras) es la cola
// de trabajo real del Director —lo que aún espera decisión— e
// "Historial" (/admin/historial) es el archivo de lo ya
// resuelto. Antes ambas cosas convivían en una sola lista, así
// que una solicitud aprobada o rechazada seguía apareciendo
// entre las que faltaban por atender y la bandeja crecía sin
// fin. Cuál toca se lee de meta.vista de la ruta.

const vista =
  computed(() =>
    route.meta.vista === 'HISTORIAL'
      ? 'HISTORIAL'
      : 'PENDIENTES'
  )

const filtroHistorial =
  ref('')


const conteos =
  computed(() => {

    const total = {
      PENDIENTES: 0,
      APROBADA: 0,
      RECHAZADA: 0,
    }

    for (const compra of compras.value) {

      const bucket =
        bucketEstado(compra.estado)

      if (bucket === 'EN_ESPERA') {
        total.PENDIENTES += 1
      }

      else if (bucket === 'APROBADA') {
        total.APROBADA += 1
      }

      else if (bucket === 'RECHAZADA') {
        total.RECHAZADA += 1
      }
    }

    total.HISTORIAL =
      total.APROBADA
      + total.RECHAZADA

    return total
  })


const comprasFiltradas =
  computed(() => {

    if (vista.value === 'PENDIENTES') {

      return compras.value.filter(
        compra =>
          bucketEstado(compra.estado)
          === 'EN_ESPERA'
      )
    }

    return compras.value.filter(
      compra => {

        const bucket =
          bucketEstado(compra.estado)

        if (bucket === 'EN_ESPERA') {
          return false
        }

        if (!filtroHistorial.value) {
          return true
        }

        return bucket === filtroHistorial.value
      }
    )
  })


// ==========================================================
// DETALLE (DOCUMENTO)
// ==========================================================

const mostrarDetalle =
  ref(false)

const compraSeleccionada =
  ref(null)

const documentosExpediente =
  computed(() => {

    const c =
      compraSeleccionada.value

    if (!c) {
      return []
    }

    return [
      { label: 'Informe', url: c.informe },
      { label: 'POA', url: c.poa },
      { label: 'Pedido', url: c.pedido },
      { label: 'Proforma', url: c.proforma },
      {
        label: 'Certificación presupuestaria',
        url: c.certificacion_presupuestaria,
        pendienteTexto: 'Pendiente (la genera OAF/DAF)',
      },
    ]
  })


// Semáforo del expediente que se muestra en la cabecera de
// decisión. Solo cuentan los cuatro documentos que adjunta la
// Unidad Solicitante: la certificación presupuestaria la
// genera OAF/DAF más adelante en el flujo, así que tenerla
// pendiente no significa que el expediente venga incompleto.

const resumenExpediente =
  computed(() => {

    const docs =
      documentosExpediente.value
        .filter(
          doc =>
            doc.label !== 'Certificación presupuestaria'
        )

    const adjuntos =
      docs.filter(doc => doc.url).length

    return {
      adjuntos,
      total: docs.length,
      completo:
        docs.length > 0
        && adjuntos === docs.length,
    }
  })


// La descripción y las especificaciones suelen venir con el
// mismo texto (el formulario del solicitante repite el dato);
// mostrarlo dos veces en la ficha del Director es ruido.

const especificacionesDistintas =
  computed(() => {

    const c =
      compraSeleccionada.value

    if (!c?.especificaciones) {
      return false
    }

    return (
      String(c.especificaciones).trim().toLowerCase()
      !== String(c.descripcion || '').trim().toLowerCase()
    )
  })

const procesando =
  ref(false)

const mostrarFormRechazo =
  ref(false)

const motivoRechazoTexto =
  ref('')

const errorAccion =
  ref('')


// La certificación presupuestaria la emite la DAF (endpoint
// certificar-daf, permiso CERTIFICAR_PRESUPUESTO). El Director
// autoriza DESPUÉS, sobre el expediente ya certificado, así que
// mientras la solicitud siga en este estado no se le ofrece
// "Aprobar": no le corresponde a él adjuntar ese PDF.

const esperandoCertificacionDaf =
  computed(() =>
    compraSeleccionada.value?.estado
    === 'EVALUADO_PENDIENTE_CERTIFICACION'
  )


function resetearFormularios() {

  mostrarFormRechazo.value =
    false

  motivoRechazoTexto.value =
    ''

  errorAccion.value =
    ''
}


function verDetalle(
  compra
) {

  compraSeleccionada.value =
    compra

  mostrarDetalle.value =
    true

  resetearFormularios()
}


function cerrarDetalle() {

  mostrarDetalle.value =
    false

  compraSeleccionada.value =
    null

  resetearFormularios()
}


// ==========================================================
// DATOS DEL SOLICITANTE
// ==========================================================

const mostrarSolicitante =
  ref(false)

const solicitanteDetalle =
  ref(null)

const cargandoSolicitante =
  ref(false)


async function abrirSolicitante(
  usuarioId
) {

  mostrarSolicitante.value =
    true

  cargandoSolicitante.value =
    true

  solicitanteDetalle.value =
    null

  try {

    const respuesta =
      await fetch(
        `/api/usuarios/usuarios/${usuarioId}/`,
        {
          headers: {
            Authorization: `Token ${token()}`,
            Accept: 'application/json',
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

    if (respuesta.ok) {

      solicitanteDetalle.value =
        await respuesta.json()
    }

  } catch (error) {

    console.error(
      'Error cargando datos del solicitante:',
      error
    )

  } finally {

    cargandoSolicitante.value =
      false
  }
}


function cerrarSolicitante() {

  mostrarSolicitante.value =
    false

  solicitanteDetalle.value =
    null
}


// ==========================================================
// DECISIÓN (APROBAR / RECHAZAR)
// ==========================================================
//
// El BPMN de Compra Caja Chica exige, antes de aprobar, el
// expediente completo: INFORME, POA, PEDIDO y PROFORMA (los
// sube la Unidad Solicitante al crear la solicitud) y la
// CERTIFICACIÓN PRESUPUESTARIA (la genera OAF/DAF, en PDF).
// Cuando la solicitud está en EVALUADO_PENDIENTE_CERTIFICACION,
// "Aprobar" pide adjuntar ese PDF (DAF se lo hace llegar al
// administrador) en vez de un simple sí/no. Rechazar, en
// cambio, no necesita ningún documento adicional y está
// disponible en cualquier estado "en espera".
//
// La decisión vive SOLO en el documento de detalle: desde la
// lista únicamente se puede "Ver detalle". Así el Director no
// puede aprobar ni rechazar sin haber abierto el expediente.
// ==========================================================

function abrirFormRechazo() {

  resetearFormularios()

  mostrarFormRechazo.value =
    true
}


function cancelarRechazo() {

  resetearFormularios()
}


async function aprobarCompra() {

  if (!compraSeleccionada.value) {
    return
  }

  const confirmar =
    await window.sigtaConfirm(
      `¿Confirma aprobar la solicitud ${compraSeleccionada.value.codigo}?`
    )

  if (!confirmar) {
    return
  }

  const estado =
    compraSeleccionada.value.estado

  const endpointsPorEstado = {
    CREADO_PENDIENTE_DAF: 'evaluar-daf',
    VERIFICADO_PENDIENTE_AUTORIZACION: 'visto-bueno-director',
  }

  const endpoint =
    endpointsPorEstado[estado]

  if (!endpoint) {
    return
  }

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
  tipo,
  esArchivo = false
) {

  procesando.value =
    true

  errorAccion.value =
    ''

  try {

    const headers = {
      Authorization: `Token ${token()}`,
      Accept: 'application/json',
    }

    if (!esArchivo) {
      headers['Content-Type'] = 'application/json'
    }

    const respuesta =
      await fetch(
        `/api/compras/solicitudes/${compraSeleccionada.value.id}/${endpoint}/`,
        {
          method: 'POST',
          headers,
          body: esArchivo ? body : JSON.stringify(body),
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
// VERIFICADO_PENDIENTE_AUTORIZACION,
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


const mensajeVacio =
  computed(() => {

    if (vista.value === 'PENDIENTES') {
      return 'No hay solicitudes pendientes de decisión.'
    }

    return (
      {
        APROBADA: 'Todavía no hay solicitudes aprobadas.',
        RECHAZADA: 'Todavía no hay solicitudes rechazadas.',
      }[filtroHistorial.value]
      || 'Todavía no hay solicitudes resueltas.'
    )
  })


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


function iconoBucket(
  bucket
) {

  return (
    {
      EN_ESPERA: '⏳',
      APROBADA: '✅',
      RECHAZADA: '❌',
    }[bucket]
    || '⏳'
  )
}


function descripcionBucket(
  bucket
) {

  return (
    {
      EN_ESPERA: 'La solicitud se encuentra pendiente de aprobación.',
      APROBADA: 'La solicitud fue aprobada.',
      RECHAZADA: 'La solicitud fue rechazada.',
    }[bucket]
    || ''
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
  background: var(--sigta-azul-tenue);
  font-family: var(--sigta-fuente);
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
  color: var(--sigta-texto);
  font-size: 33px;
}


.page-header p {
  margin: 5px 0 0;
  color: var(--sigta-texto-suave);
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
  border: 1px solid var(--sigta-borde);
  border-radius: 7px;
  background: white;
  color: var(--sigta-texto);
  font-family: inherit;
  font-size: 15px;
  outline: none;
}


.resolucion-motivo,
.resolucion-estado {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.45;
  color: var(--sigta-texto-suave);
}


.resolucion-motivo b {
  color: var(--sigta-error);
}


.refresh-button {
  min-height: 41px;
  padding: 0 15px;
  border: 1px solid var(--sigta-azul);
  border-radius: 7px;
  background: white;
  color: var(--sigta-azul);
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
  border-bottom: 1px solid var(--sigta-azul-tenue);
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
  color: var(--sigta-azul);
  font-size: 15px;
}


.request-code small {
  display: block;
  margin-top: 4px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
}


.request-info h3 {
  margin: 0 0 5px;
  color: var(--sigta-azul);
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
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
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
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza-oscuro);
}


.status.closed {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}


.status.cancelled {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}


.row-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}


.view {
  padding: 6px 8px;
  border: none;
  border-radius: 5px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}


.view {
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
}


/* =========================================================
   VACÍOS
========================================================= */

.loading,
.empty {
  padding: 45px 20px;
  text-align: center;
  color: var(--sigta-texto-suave);
  font-size: 16px;
}


.empty {
  border-radius: 10px;
  background: white;
}


/* =========================================================
   DOCUMENTO DE DETALLE
========================================================= */

/*
  El scroll deja de estar en el modal entero (regla global
  .detalle-modal) y pasa a .documento-body, para que la
  cabecera y la barra de decisión queden fijas.
*/

.documento-modal {
  max-width: 700px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}


.documento-modal .detalle-modal-header h3 {
  font-size: 20px;
}


.documento-modal .detalle-modal-header small {
  font-size: 13px;
}


.documento-body {
  padding: 18px 22px 22px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}


/* =========================================================
   CABECERA DE DECISIÓN
========================================================= */

.decision-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 14px;
  margin-bottom: 16px;
  padding: 16px 18px;
  border-radius: 10px;
  background: var(--sigta-azul-tenue);
  border-left: 5px solid var(--sigta-mostaza);
}


.decision-dato b {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-texto-suave);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.decision-dato strong {
  display: block;
  color: var(--sigta-azul-oscuro);
  font-size: 17px;
  line-height: 1.3;
}


.decision-monto {
  font-size: 26px;
  letter-spacing: -.5px;
}


.decision-expediente {
  font-size: 15px;
}


.decision-expediente.ok {
  color: var(--sigta-exito);
}


.decision-expediente.falta {
  color: var(--sigta-alerta);
}


.estado-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
  padding: 14px 16px;
  border-radius: 8px;
}


.estado-banner-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,.6);
  font-size: 19px;
}


.estado-banner strong {
  display: block;
  font-size: 18px;
  font-weight: 800;
}


.estado-banner-descripcion {
  display: block;
  margin-top: 2px;
  font-size: 15px;
  font-weight: 500;
  opacity: .85;
}


.estado-banner.working {
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza-oscuro);
}


.estado-banner.closed {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}


.estado-banner.cancelled {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}


.documento-seccion {
  padding: 16px 0;
  border-top: 1px solid var(--sigta-azul-tenue);
}


.documento-seccion:first-of-type {
  border-top: none;
  padding-top: 0;
}


.documento-header-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
}


.documento-header-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--sigta-mostaza-suave);
  font-size: 17px;
}


.documento-titulo-fila {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}


.documento-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
  font-size: 13px;
}


.documento-titulo {
  display: block;
  margin-bottom: 8px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.documento-titulo-fila .documento-titulo {
  margin-bottom: 0;
}


.documento-seccion h4 {
  margin: 0 0 6px;
  color: var(--sigta-texto);
  font-size: 20px;
}


.documento-seccion > p {
  margin: 0 0 10px;
  color: var(--sigta-azul);
  font-size: 16px;
  line-height: 1.5;
  white-space: pre-wrap;
}


.documento-seccion b {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
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


.documento-fila-2 {
  grid-template-columns: repeat(2, 1fr);
}


/*
  Los textos largos (especificaciones, justificación) van a
  ancho completo: en una columna estrecha se parten palabra a
  palabra y cuesta leerlos.
*/

.documento-bloque {
  margin-bottom: 12px;
}


.documento-bloque b {
  display: block;
  margin-bottom: 3px;
  color: var(--sigta-texto-suave);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.documento-bloque span {
  display: block;
  color: var(--sigta-texto);
  font-size: 16px;
  line-height: 1.5;
}


.documento-fila > div span {
  display: block;
  color: var(--sigta-texto);
  font-size: 16px;
}


.solicitante-link {
  display: block;
  width: 100%;
  padding: 0;
  border: none;
  background: transparent;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
}


.solicitante-link span {
  display: block;
  color: var(--sigta-azul);
  font-size: 14px;
  font-weight: 700;
  text-decoration: underline;
}


.solicitante-link:hover span {
  color: var(--sigta-azul);
}


.solicitante-link small {
  display: block;
  margin-top: 2px;
  color: var(--sigta-texto);
  font-size: 13px;
}


.solicitante-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(10, 20, 35, .55);
}


.documento-lista {
  display: flex;
  flex-direction: column;
  gap: 8px;
}


.documento-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  border-radius: 7px;
  font-family: inherit;
  text-align: left;
  text-decoration: none;
}


.documento-item-icono {
  flex-shrink: 0;
  font-size: 16px;
}


.documento-item-label {
  flex: 1;
  color: var(--sigta-texto);
  font-size: 14px;
  font-weight: 700;
}


.documento-item small {
  font-size: 13px;
}


.documento-item-accion {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}


.documento-item-ojo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255,255,255,.6);
  font-size: 11px;
}


.documento-item.ok {
  background: var(--sigta-exito-fondo);
}


.documento-item.ok .documento-item-accion {
  color: var(--sigta-exito);
  font-weight: 700;
}


.documento-item.falta {
  background: var(--sigta-azul-tenue);
}


.documento-item.falta small {
  color: var(--sigta-texto-suave);
}


.motivo-rechazo {
  padding: 14px;
  border: none;
  border-radius: 8px;
  background: var(--sigta-error-fondo);
}


.motivo-rechazo .documento-titulo {
  color: var(--sigta-error);
}


.motivo-rechazo p {
  margin: 0;
  color: var(--sigta-error);
  font-size: 14px;
  line-height: 1.5;
}


/* =========================================================
   ACCIONES DE DECISIÓN
========================================================= */

.documento-acciones {
  flex-shrink: 0;
  padding: 16px 22px;
  border-top: 1px solid var(--sigta-azul-tenue);
  background: var(--sigta-blanco);
  border-radius: 0 0 14px 14px;
}


.nota-tramite {
  margin: 0;
  padding: 12px 14px;
  border-radius: 7px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 14px;
  line-height: 1.5;
}


.accion-error {
  margin: 0 0 10px;
  padding: 10px 12px;
  border-radius: 7px;
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
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
  background: var(--sigta-exito);
  color: white;
}


.btn-rechazar {
  background: var(--sigta-error);
  color: white;
}


.btn-cancelar {
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
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
  color: var(--sigta-azul);
  font-size: 14px;
  font-weight: 700;
}


.form-rechazo label span {
  color: var(--sigta-error);
}


.form-rechazo textarea {
  width: 100%;
  margin-bottom: 10px;
  padding: 10px 12px;
  border: 1px solid var(--sigta-borde);
  border-radius: 7px;
  background: white;
  color: var(--sigta-texto);
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
