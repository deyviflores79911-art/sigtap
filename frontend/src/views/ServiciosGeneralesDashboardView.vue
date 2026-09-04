<template>
  <div class="layout sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><b><img src="/img/emi.jpg" alt="EMI"></b><div><strong>SIGTA</strong><small>Mantenimiento</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="profile"><i>{{ iniciales }}</i><div><b>{{ nombre }}</b><small>Jefe de Mantenimiento</small></div></div>
      <p>GESTIÓN DE MANTENIMIENTO</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="irA(m.id)"><span class="icon-badge" :style="{background:m.color+'26',color:m.color}"><IconoSigta :nombre="m.icono" :tamano="16" /></span>{{ m.nombre }}<em v-if="m.total!==undefined">{{ m.total }}</em></button>
      <div class="bottom"><button @click="salir"><span>↪</span>Cerrar sesión</button></div>
    </aside>

    <main>
      <header>
        <div><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <button class="refresh" :disabled="cargando" @click="cargar">↻ Actualizar</button>
      </header>

      <!-- ============================ RESUMEN ============================ -->
      <section v-if="vista==='resumen'">
        <div class="hero">
          <div><small>JEFATURA DE MANTENIMIENTO</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Requerimientos que requieren su gestión hoy.</p></div>
          <span>MT</span>
        </div>
        <div class="stats">
          <article @click="irA('validar')"><i class="blue">VA</i><div><small>Por validar</small><b>{{ porValidar.length }}</b><p>tickets nuevos</p></div></article>
          <article @click="irA('clasificar')"><i class="gold">CL</i><div><small>Por clasificar</small><b>{{ porClasificar.length }}</b><p>prioridad</p></div></article>
          <article @click="irA('designar')"><i class="blue">DE</i><div><small>Por designar</small><b>{{ porDesignar.length }}</b><p>técnico</p></div></article>
          <article @click="irA('verificar')"><i class="green">VF</i><div><small>Por verificar</small><b>{{ porVerificar.length }}</b><p>funcionamiento</p></div></article>
        </div>
        <div class="panels">
          <section class="panel">
            <div class="panel-head"><div><small>FLUJO BPMN</small><h3>Proceso de mantenimiento</h3></div></div>
            <button class="flow" @click="irA('validar')"><i class="blue">1</i><div><b>Recibir y validar ticket</b><small>Confirmar que el requerimiento procede o rechazarlo</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('clasificar')"><i class="gold">2</i><div><b>Clasificar prioridad</b><small>Definir la urgencia del mantenimiento</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('designar')"><i class="blue">3</i><div><b>Designar revisión al equipo</b><small>Asignar el técnico responsable</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('compra')"><i class="gold">4</i><div><b>Recibir requerimiento y cotización</b><small>Evaluar la viabilidad de la compra</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('verificar')"><i class="green">5</i><div><b>Verificar funcionamiento</b><small>Confirmar si el problema quedó resuelto</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('informe')"><i class="gold">6</i><div><b>Conformidad e informe final</b><small>Cerrar el caso y elevarlo a la Dirección</small></div><strong>›</strong></button>
          </section>
          <section class="panel">
            <div class="panel-head"><div><small>SEGUIMIENTO</small><h3>Reporte mensual</h3></div></div>
            <p class="copy">Consolidado de los mantenimientos finalizados en el periodo.</p>
            <button class="wide primary" @click="irA('reporte')">Ver reporte mensual →</button>
          </section>
        </div>
      </section>

      <!-- ========================= 1. VALIDAR ========================= -->
      <section v-else-if="vista==='validar'">
        <div class="instruction"><b>¿Ticket válido?</b><span>Reciba y valide el requerimiento, o notifique el rechazo al solicitante.</span></div>
        <div v-if="cargando" class="empty">Consultando requerimientos…</div>
        <div v-else-if="porValidar.length" class="cards">
          <article v-for="r in porValidar" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <ul class="datos">
              <li><b>Ubicación</b><span>{{ r.ubicacion || 's/d' }}</span></li>
              <li><b>Solicitante</b><span>{{ r.solicitante_nombre || 's/d' }}</span></li>
            </ul>
            <p>{{ (r.descripcion||'').slice(0,130) }}</p>
            <a v-if="r.evidencia_archivo_url" class="adjunto" :href="r.evidencia_archivo_url" target="_blank">📎 Evidencia</a>
            <div class="actions">
              <button @click="verItem(r)">Ver detalle</button>
              <button class="reject" @click="rechazar(r)">Rechazar</button>
              <button class="primary" @click="validar(r)">Validar</button>
            </div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No hay requerimientos pendientes de validación.</p></div>
      </section>

      <!-- ======================= 2. CLASIFICAR ======================= -->
      <section v-else-if="vista==='clasificar'">
        <div class="instruction"><b>Clasificar prioridad</b><span>Defina la urgencia del mantenimiento y justifíquela.</span></div>
        <div v-if="!itemActivo" class="cards">
          <article v-for="r in porClasificar" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <div class="actions"><button class="primary" @click="abrir(r)">Clasificar</button></div>
          </article>
          <div v-if="!porClasificar.length" class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No hay requerimientos por clasificar.</p></div>
        </div>
        <div v-else class="panel">
          <h3>{{ itemActivo.codigo }} — {{ itemActivo.titulo }}</h3>
          <label class="campo">Prioridad
            <select v-model="formClasificar.prioridad">
              <option value="">Seleccione…</option>
              <option value="BAJA">Baja</option>
              <option value="MEDIA">Media</option>
              <option value="ALTA">Alta</option>
              <option value="URGENTE">Urgente</option>
            </select>
          </label>
          <label class="campo">Criterio de prioridad
            <textarea v-model="formClasificar.criterio_prioridad" rows="3" placeholder="Justifique la prioridad asignada"></textarea>
          </label>
          <div class="actions">
            <button @click="itemActivo=null">Cancelar</button>
            <button class="primary" :disabled="procesando||!formClasificar.prioridad||!formClasificar.criterio_prioridad.trim()" @click="clasificar">Guardar prioridad</button>
          </div>
        </div>
      </section>

      <!-- ======================== 3. DESIGNAR ======================== -->
      <section v-else-if="vista==='designar'">
        <div class="instruction"><b>Designar revisión al equipo</b><span>Seleccione al Técnico de Mantenimiento que atenderá el requerimiento.</span></div>
        <div v-if="!itemActivo" class="cards">
          <article v-for="r in porDesignar" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.prioridad_jefatura }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <div class="actions"><button class="primary" @click="abrir(r)">Designar</button></div>
          </article>
          <div v-if="!porDesignar.length" class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No hay requerimientos por designar.</p></div>
        </div>
        <div v-else class="panel">
          <h3>{{ itemActivo.codigo }} — {{ itemActivo.titulo }}</h3>
          <label class="campo">Técnico de Mantenimiento
            <select v-model="formDesignar.tecnico_id">
              <option value="">Seleccione…</option>
              <option v-for="t in tecnicos" :key="t.id" :value="t.id">{{ t.nombre_completo || t.email }}</option>
            </select>
          </label>
          <small v-if="!tecnicos.length">No hay técnicos activos disponibles.</small>
          <div class="actions">
            <button @click="itemActivo=null">Cancelar</button>
            <button class="primary" :disabled="procesando||!formDesignar.tecnico_id" @click="designar">Designar técnico</button>
          </div>
        </div>
      </section>

      <!-- ===================== 4. VIABILIDAD COMPRA ===================== -->
      <section v-else-if="vista==='compra'">
        <div class="instruction"><b>Recibir requerimiento y cotización</b><span>El técnico solicitó un componente. Confirme si la compra es viable antes de elevarla a la DAF.</span></div>
        <div v-if="!itemActivo" class="cards">
          <article v-for="r in porEvaluarCompra" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_compra_componente }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <ul class="datos">
              <li><b>Componente</b><span>{{ r.producto_requerido || 's/d' }}</span></li>
              <li><b>Cantidad</b><span>{{ r.cantidad_requerida || 1 }}</span></li>
              <li><b>Costo estimado</b><span>{{ r.costo_estimado ? `Bs. ${r.costo_estimado}` : 's/d' }}</span></li>
            </ul>
            <a v-if="r.cotizacion_archivo" class="adjunto" :href="r.cotizacion_archivo" target="_blank">📎 Cotización</a>
            <div class="actions"><button class="primary" @click="abrir(r)">Evaluar</button></div>
          </article>
          <div v-if="!porEvaluarCompra.length" class="empty"><span>✓</span><h3>Sin pendientes</h3><p>Ningún requerimiento espera evaluación de compra.</p></div>
        </div>
        <div v-else class="panel">
          <h3>{{ itemActivo.codigo }} — {{ itemActivo.titulo }}</h3>
          <p class="copy"><b>Componente:</b> {{ itemActivo.producto_requerido }}<br><b>Especificaciones:</b> {{ itemActivo.especificacion_producto || 's/d' }}<br><b>Costo estimado:</b> Bs. {{ itemActivo.costo_estimado || 's/d' }}</p>
          <label class="campo">¿Es viable la compra?
            <select v-model="formCompra.viable">
              <option :value="true">Sí, es viable</option>
              <option :value="false">No es viable</option>
            </select>
          </label>
          <label v-if="formCompra.viable===true" class="campo">POA (Programa Operativo Anual)
            <input type="file" accept=".pdf,.jpg,.jpeg,.png" @change="seleccionarPoa">
            <small v-if="formCompra.poa">{{ formCompra.poa.name }}</small>
          </label>
          <label v-if="formCompra.viable===false" class="campo">Motivo de no viabilidad
            <textarea v-model="formCompra.motivo_no_viable" rows="2"></textarea>
          </label>
          <div class="actions">
            <button @click="itemActivo=null">Cancelar</button>
            <button class="primary" :disabled="procesando||(formCompra.viable===false&&!formCompra.motivo_no_viable.trim())" @click="evaluarCompra">
              {{ formCompra.viable===false ? 'Cerrar sin compra' : 'Elevar informe a la DAF' }}
            </button>
          </div>
        </div>
      </section>

      <!-- ======================= 5. VERIFICAR ======================= -->
      <section v-else-if="vista==='verificar'">
        <div class="instruction"><b>Verificar funcionamiento</b><span>¿El problema quedó resuelto? Si no, el caso vuelve al técnico para una nueva intervención.</span></div>
        <div v-if="porVerificar.length" class="cards">
          <article v-for="r in porVerificar" :key="r.id" :class="{ retorno: Number(r.rework_count) > 0 }">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <div v-if="Number(r.rework_count) > 0" class="mini-alerta">⚠ Reproceso número {{ r.rework_count }}</div>
            <p>{{ (r.informe_trabajo||'').slice(0,130) }}</p>
            <div class="actions">
              <button @click="verItem(r)">Ver detalle</button>
              <button class="reject" @click="verificar(r,false)">No resuelto</button>
              <button class="primary" @click="verificar(r,true)">Problema resuelto</button>
            </div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No hay requerimientos pendientes de verificación.</p></div>
      </section>

      <!-- =============== 6. CONFORMIDAD E INFORME FINAL =============== -->
      <section v-else-if="vista==='informe'">
        <div class="instruction"><b>Conformidad e informe final</b><span>Informe la conformidad del mantenimiento y elabore el informe que se elevará a la Dirección.</span></div>

        <div v-if="porConformar.length" class="cards">
          <article v-for="r in porConformar" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>verificado</em></div>
            <h3>{{ r.titulo }}</h3>
            <p>Verificado el {{ fecha(r.verificado_en) }}. Informe la conformidad para continuar.</p>
            <div class="actions"><button class="primary" @click="conformar(r)">Informar conformidad</button></div>
          </article>
        </div>

        <div v-if="!itemActivo" class="cards">
          <article v-for="r in porInformar" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <div class="actions"><button class="primary" @click="abrir(r)">Elaborar informe final</button></div>
          </article>
          <div v-if="!porInformar.length && !porConformar.length" class="empty"><span>✓</span><h3>Sin pendientes</h3><p>No hay casos esperando conformidad ni informe final.</p></div>
        </div>
        <div v-else class="panel">
          <h3>{{ itemActivo.codigo }} — {{ itemActivo.titulo }}</h3>
          <label class="campo">Informe final
            <textarea v-model="formInforme.informe_final" rows="5" placeholder="Diagnóstico, trabajo realizado, repuestos, pruebas y resultado"></textarea>
          </label>
          <div class="actions">
            <button @click="itemActivo=null">Cancelar</button>
            <button class="primary" :disabled="procesando||!formInforme.informe_final.trim()" @click="elaborarInforme">Validar y elevar a la Dirección</button>
          </div>
        </div>
      </section>

      <!-- ====================== REPORTE MENSUAL ====================== -->
      <section v-else-if="vista==='reporte'">
        <div class="instruction"><b>Reporte mensual</b><span>Consolidado de los mantenimientos finalizados en el periodo.</span></div>
        <div class="panel">
          <div class="actions" style="border:0;margin:0">
            <label class="campo">Año<input v-model="periodo.anio" type="number" min="2020" max="2100"></label>
            <label class="campo">Mes<input v-model="periodo.mes" type="number" min="1" max="12"></label>
            <button class="primary" :disabled="procesando" @click="cargarReporte">Consultar</button>
          </div>
          <p v-if="reporte" class="copy"><b>{{ reporte.total_finalizados }}</b> mantenimiento(s) finalizado(s) en {{ reporte.mes }}/{{ reporte.anio }}.</p>
          <article v-for="r in (reporte?.requerimientos || [])" :key="`rep-${r.id}`" class="reporte-item">
            <b>{{ r.codigo }}</b> — {{ r.titulo }} <small>({{ fecha(r.finalizado_en) }})</small>
          </article>
        </div>
      </section>
    </main>

    <!-- ============================ DETALLE ============================ -->
    <div v-if="detalle" class="detalle-modal-backdrop" @click.self="detalle=null">
      <div class="detalle-modal">
        <div class="detalle-modal-header">
          <div><h3>{{ detalle.codigo }}</h3><small>{{ detalle.titulo }}</small></div>
          <button class="detalle-modal-close" @click="detalle=null">✕</button>
        </div>
        <div class="detalle-modal-body">
          <div class="detalle-fila">
            <div class="detalle-campo"><b>Estado</b><span>{{ detalle.estado_nombre || detalle.estado_codigo }}</span></div>
            <div class="detalle-campo"><b>Prioridad</b><span>{{ detalle.prioridad_jefatura || 's/d' }}</span></div>
          </div>
          <div class="detalle-fila">
            <div class="detalle-campo"><b>Solicitante</b><span>{{ detalle.solicitante_nombre }}</span></div>
            <div class="detalle-campo"><b>Técnico</b><span>{{ detalle.auxiliar_nombre || 's/d' }}</span></div>
          </div>
          <div class="detalle-campo"><b>Descripción</b><p>{{ detalle.descripcion }}</p></div>
          <div class="detalle-campo"><b>Ubicación</b><span>{{ detalle.ubicacion || 's/d' }}</span></div>
          <div class="detalle-campo" v-if="detalle.motivo_rechazo"><b>Motivo del rechazo</b><p>{{ detalle.motivo_rechazo }}</p></div>
          <div class="detalle-campo" v-if="detalle.diagnostico"><b>Diagnóstico</b><p>{{ detalle.diagnostico }}</p></div>
          <div class="detalle-campo" v-if="detalle.plan_solucion"><b>Plan de solución</b><p>{{ detalle.plan_solucion }}</p></div>
          <div class="detalle-campo" v-if="detalle.producto_requerido"><b>Componente requerido</b><p>{{ detalle.producto_requerido }} — Bs. {{ detalle.costo_estimado || 's/d' }}</p></div>
          <div class="detalle-campo" v-if="detalle.motivo_no_viable"><b>Compra no viable</b><p>{{ detalle.motivo_no_viable }}</p></div>
          <div class="detalle-campo" v-if="detalle.codigo_compra_vinculada"><b>Expediente de compra</b><span>{{ detalle.codigo_compra_vinculada }}</span></div>
          <div class="detalle-campo" v-if="detalle.trabajo_realizado"><b>Trabajo realizado</b><p>{{ detalle.trabajo_realizado }}</p></div>
          <div class="detalle-campo" v-if="detalle.resultado_pruebas"><b>Pruebas técnicas</b><p>{{ detalle.resultado_pruebas }}</p></div>
          <div class="detalle-campo" v-if="detalle.informe_trabajo"><b>Informe del técnico</b><p>{{ detalle.informe_trabajo }}</p></div>
          <div class="detalle-campo" v-if="detalle.informe_final"><b>Informe final</b><p>{{ detalle.informe_final }}</p></div>
          <div class="detalle-campo" v-if="detalle.evidencia_archivo_url"><b>Evidencia</b><a :href="detalle.evidencia_archivo_url" target="_blank">Abrir archivo →</a></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import IconoSigta from '../components/IconoSigta.vue'

const router = useRouter()
const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))
const vista = ref('resumen')
const menuAbierto = ref(false)
const items = ref([])
const tecnicos = ref([])
const cargando = ref(false)
const procesando = ref(false)
const itemActivo = ref(null)
const detalle = ref(null)
const reporte = ref(null)

const nombre = computed(() => usuario.value.nombre || usuario.value.nombre_completo || 'Jefe de Mantenimiento')
const primerNombre = computed(() => nombre.value.split(' ')[0])
const iniciales = computed(() => nombre.value.split(' ').slice(0, 2).map(x => x[0]).join('').toUpperCase())
const saludo = computed(() => new Date().getHours() < 12 ? 'Buenos días' : new Date().getHours() < 19 ? 'Buenas tardes' : 'Buenas noches')

/* Bandejas del BPMN */
const porValidar = computed(() => items.value.filter(r => r.estado_codigo === 'RECIBIDO'))
const porClasificar = computed(() => items.value.filter(r => r.estado_codigo === 'VALIDADO' && !r.prioridad_jefatura))
const porDesignar = computed(() => items.value.filter(r => r.estado_codigo === 'VALIDADO' && !!r.prioridad_jefatura))
const porEvaluarCompra = computed(() => items.value.filter(r => r.estado_compra_componente === 'SOLICITADA'))
const porVerificar = computed(() => items.value.filter(r => r.estado_codigo === 'INFORME_REGISTRADO' && !r.verificado_en))
const porConformar = computed(() => items.value.filter(r => r.estado_codigo === 'INFORME_REGISTRADO' && !!r.verificado_en))
const porInformar = computed(() => items.value.filter(r => r.estado_codigo === 'CONFORMIDAD_INFORMADA'))

const menu = computed(() => [
  { id: 'resumen', icono: 'inicio', nombre: 'Dashboard', color: '#F2C400' },
  { id: 'validar', icono: 'validar', nombre: 'Validar tickets', total: porValidar.value.length, color: '#2FA85C' },
  { id: 'clasificar', icono: 'prioridad', nombre: 'Clasificar prioridad', total: porClasificar.value.length, color: '#E08A1E' },
  { id: 'designar', icono: 'tecnico', nombre: 'Designar técnico', total: porDesignar.value.length, color: '#3E7BD6' },
  { id: 'compra', icono: 'compras', nombre: 'Evaluar compra', total: porEvaluarCompra.value.length, color: '#C79A1E' },
  { id: 'verificar', icono: 'verificar', nombre: 'Verificar funcionamiento', total: porVerificar.value.length, color: '#1FA396' },
  { id: 'informe', icono: 'conformidad', nombre: 'Conformidad e informe', total: porConformar.value.length + porInformar.value.length, color: '#7B6FD9' },
  { id: 'reporte', icono: 'reporte', nombre: 'Reporte mensual', color: '#D9538A' },
])

const titulo = computed(() => ({
  resumen: 'Dashboard del Jefe de Mantenimiento',
  validar: 'Recibir y validar tickets',
  clasificar: 'Clasificar prioridad',
  designar: 'Designar revisión al equipo',
  compra: 'Recibir requerimiento y cotización',
  verificar: 'Verificar funcionamiento',
  informe: 'Conformidad e informe final',
  reporte: 'Reporte mensual',
}[vista.value]))

const subtitulo = computed(() => ({
  resumen: 'Validación, clasificación y seguimiento de los requerimientos de mantenimiento.',
  validar: 'Requerimientos registrados por los usuarios, pendientes de validación.',
  clasificar: 'Defina la urgencia de cada requerimiento validado.',
  designar: 'Asigne el técnico responsable de la revisión.',
  compra: 'Evalúe la viabilidad de los componentes solicitados por el técnico.',
  verificar: 'Confirme si la intervención resolvió el problema reportado.',
  informe: 'Cierre del caso y elevación del informe a la Dirección.',
  reporte: 'Consolidado mensual de mantenimientos finalizados.',
}[vista.value]))

const base = '/api/mantenimiento/requerimientos'
const token = () => localStorage.getItem('sigta_token')

async function cargar() {
  cargando.value = true
  try {
    const r = await fetch(`${base}/`, { headers: { Authorization: `Token ${token()}` } })
    const d = await r.json()
    items.value = Array.isArray(d) ? d : (d.results || [])
    const rt = await fetch('/api/usuarios/usuarios-por-rol/?rol=AUXILIAR_SERVICIOS_GENERALES', {
      headers: { Authorization: `Token ${token()}` },
    })
    tecnicos.value = rt.ok ? await rt.json() : []
  } finally {
    cargando.value = false
  }
}

async function postAccion(item, endpoint, body) {
  procesando.value = true
  try {
    const esFormData = body instanceof FormData
    const r = await fetch(`${base}/${item.id}/${endpoint}/`, {
      method: 'POST',
      headers: esFormData
        ? { Authorization: `Token ${token()}` }
        : { Authorization: `Token ${token()}`, 'Content-Type': 'application/json' },
      body: esFormData ? body : JSON.stringify(body || {}),
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible completar la acción.')
    await cargar()
    itemActivo.value = null
    return d
  } finally {
    procesando.value = false
  }
}

function irA(id) {
  vista.value = id
  menuAbierto.value = false
  itemActivo.value = null
}

function abrir(item) {
  itemActivo.value = item
  formClasificar.prioridad = ''
  formClasificar.criterio_prioridad = ''
  formDesignar.tecnico_id = ''
  formCompra.viable = true
  formCompra.motivo_no_viable = ''
  formCompra.poa = null
  formInforme.informe_final = ''
}

function verItem(item) { detalle.value = item }

function fecha(valor) {
  return valor ? new Date(valor).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' }) : 's/d'
}

function salir() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.push('/login')
}

/* Acciones del flujo */
async function validar(item) {
  try { await postAccion(item, 'validar-ticket', { es_valido: true }) } catch (e) { alert(e.message) }
}

async function rechazar(item) {
  const motivo = prompt('Indique el motivo del rechazo:')
  if (!motivo?.trim()) return
  try { await postAccion(item, 'validar-ticket', { es_valido: false, motivo_rechazo: motivo.trim() }) }
  catch (e) { alert(e.message) }
}

const formClasificar = reactive({ prioridad: '', criterio_prioridad: '' })
async function clasificar() {
  try {
    await postAccion(itemActivo.value, 'clasificar-prioridad', {
      prioridad: formClasificar.prioridad,
      criterio_prioridad: formClasificar.criterio_prioridad.trim(),
    })
  } catch (e) { alert(e.message) }
}

const formDesignar = reactive({ tecnico_id: '' })
async function designar() {
  try { await postAccion(itemActivo.value, 'designar-revision', { tecnico_id: Number(formDesignar.tecnico_id) }) }
  catch (e) { alert(e.message) }
}

const formCompra = reactive({ viable: true, motivo_no_viable: '', poa: null })
async function evaluarCompra() {
  try {
    const datos = new FormData()
    datos.append('viable', formCompra.viable)
    datos.append('motivo_no_viable', formCompra.motivo_no_viable.trim())
    if (formCompra.viable && formCompra.poa) {
      datos.append('poa', formCompra.poa)
    }
    const d = await postAccion(itemActivo.value, 'evaluar-viabilidad-compra', datos)
    alert(d?.mensaje || 'Evaluación registrada.')
  } catch (e) { alert(e.message) }
}

function seleccionarPoa(evento) {
  formCompra.poa = evento.target.files?.[0] || null
}

async function verificar(item, resuelto) {
  try {
    const d = await postAccion(item, 'verificar-funcionamiento', { problema_resuelto: resuelto })
    alert(d?.mensaje || 'Verificación registrada.')
  } catch (e) { alert(e.message) }
}

async function conformar(item) {
  try { await postAccion(item, 'informar-conformidad', {}) } catch (e) { alert(e.message) }
}

const formInforme = reactive({ informe_final: '' })
async function elaborarInforme() {
  try {
    await postAccion(itemActivo.value, 'elaborar-informe-final', { informe_final: formInforme.informe_final.trim() })
    alert('Informe final validado y elevado a la Dirección.')
  } catch (e) { alert(e.message) }
}

const periodo = reactive({ anio: new Date().getFullYear(), mes: new Date().getMonth() + 1 })
async function cargarReporte() {
  procesando.value = true
  try {
    const r = await fetch(`${base}/reporte-mensual/?anio=${periodo.anio}&mes=${periodo.mes}`, {
      headers: { Authorization: `Token ${token()}` },
    })
    reporte.value = r.ok ? await r.json() : null
  } finally {
    procesando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.layout{min-height:100vh;background:var(--sigta-fondo);color:var(--sigta-texto);font-family:var(--sigta-fuente)}aside{position:fixed;inset:0 auto 0 0;width:var(--sigta-sidebar);background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand,.profile{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 20px;border-bottom:1px solid rgba(255,255,255,.2)}.brand>b{background:var(--sigta-mostaza);color:var(--sigta-azul);padding:14px 10px;border-radius:9px}.brand strong,.brand small,.profile b,.profile small{display:block}.brand strong{font-size:23px}.brand small,.profile small{color:var(--sigta-azul-texto-claro);margin-top:3px}.profile{padding:22px 10px}.profile>i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}aside>p{font-size:10px;color:var(--sigta-azul-texto-claro);font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{border:0;background:transparent;color:var(--sigta-blanco);border-radius:8px;padding:12px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0;width:100%}aside button .icon-badge{flex-shrink:0;width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center}aside button em{margin-left:auto;background:rgba(255,255,255,.16);padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:rgba(255,255,255,.13)}.bottom{margin-top:auto;border-top:1px solid rgba(255,255,255,.2);padding-top:10px}.bottom button{width:100%}main{margin-left:var(--sigta-sidebar);padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header small{color:var(--sigta-texto-suave)}h1{font-size:var(--sigta-titulo);margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.refresh{border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-azul);padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-azul-medio));color:var(--sigta-blanco);border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small{font-size:10px;font-weight:800;letter-spacing:1.4px;color:var(--sigta-mostaza-clara)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero>span{width:68px;height:68px;border:1px solid var(--sigta-mostaza);border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px;display:flex;gap:13px;cursor:pointer}.stats i,.flow i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:var(--sigta-blanco);font-size:10px;font-weight:900}.blue{background:var(--sigta-azul)}.gold{background:var(--sigta-mostaza);color:var(--sigta-texto)!important}.green{background:var(--sigta-azul-medio)}.navy{background:var(--sigta-azul-medio)}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.panels{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}.panel-head h3{margin:5px 0 14px}.flow{width:100%;border:0;border-top:1px solid var(--sigta-borde-suave);background:var(--sigta-blanco);padding:15px 2px;display:flex;gap:13px;align-items:center;text-align:left;cursor:pointer}.flow div{flex:1}.flow b,.flow small{display:block}.flow small{color:var(--sigta-texto-suave);margin-top:4px}.flow>strong{font-size:20px}.copy{color:var(--sigta-texto-suave);font-size:12px;line-height:1.7}.wide{width:100%;padding:10px;border-radius:7px;border:1px solid var(--sigta-borde);cursor:pointer}.primary{background:var(--sigta-azul)!important;color:var(--sigta-blanco)!important;border-color:var(--sigta-azul)!important}.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;margin-bottom:17px;border-radius:7px}.instruction b,.instruction span{display:block}.instruction span{font-size:12px;color:var(--sigta-alerta);margin-top:4px}.mini-alerta{background:var(--sigta-error-fondo);color:var(--sigta-error);font-size:11px;font-weight:700;padding:7px 9px;border-radius:6px;margin-bottom:10px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:16px}.cards article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px}.cards article.retorno{border-color:var(--sigta-error);box-shadow:inset 3px 0 var(--sigta-error)}.top{display:flex;justify-content:space-between;gap:8px}.top span{font-size:12px;font-weight:800;color:var(--sigta-azul)}.top em{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px;font-style:normal}.cards h3{font-size:17px;margin:15px 0 7px}.cards article>p{font-size:12px;color:var(--sigta-texto-suave);min-height:42px}.datos{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:4px}.datos li{display:flex;justify-content:space-between;gap:10px;font-size:11px;border-bottom:1px dashed var(--sigta-borde-suave);padding-bottom:3px}.datos b{color:var(--sigta-texto-suave)}.datos span{color:var(--sigta-texto-suave);text-align:right}.adjunto{display:inline-block;font-size:11px;color:var(--sigta-azul);margin-bottom:10px;text-decoration:none}.actions{display:flex;gap:7px;border-top:1px solid var(--sigta-borde-suave);padding-top:13px;margin-top:10px;align-items:flex-end}.actions button{flex:1;padding:9px 6px;border-radius:7px;border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-texto);font-weight:700;cursor:pointer}.actions button:disabled{opacity:.55;cursor:not-allowed}.reject{color:var(--sigta-error)!important;border-color:var(--sigta-error)!important}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-borde);padding:65px;border-radius:10px;color:var(--sigta-texto-suave)}.empty>span{font-size:31px;color:var(--sigta-exito)}.campo{display:block;margin:14px 0;font-size:12px;font-weight:700;color:var(--sigta-texto)}.campo input,.campo select,.campo textarea{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-borde);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}.reporte-item{padding:9px 0;border-top:1px solid var(--sigta-borde-suave);font-size:13px}.detalle-modal-backdrop{position:fixed;inset:0;background:rgba(18,58,107,.55);display:grid;place-items:center;padding:20px;z-index:20}.detalle-modal{background:var(--sigta-blanco);border-radius:14px;width:min(700px,100%);max-height:88vh;display:flex;flex-direction:column}.detalle-modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--sigta-borde-suave)}.detalle-modal-header h3{margin:0}.detalle-modal-header small{color:var(--sigta-texto-suave)}.detalle-modal-close{border:0;background:transparent;font-size:20px;cursor:pointer;color:var(--sigta-texto-suave)}.detalle-modal-body{padding:20px 24px;overflow-y:auto;display:grid;gap:14px}.detalle-fila{display:grid;grid-template-columns:1fr 1fr;gap:14px}.detalle-campo b{display:block;font-size:11px;color:var(--sigta-texto-suave);margin-bottom:4px}.detalle-campo span,.detalle-campo p{font-size:13px;color:var(--sigta-texto);margin:0}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:760px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column;gap:12px}.detalle-fila{grid-template-columns:1fr}}
</style>
