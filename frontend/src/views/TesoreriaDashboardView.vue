<template>
  <div class="layout sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><b><img src="/img/emi.jpg" alt="EMI"></b><div><strong>SIGTA</strong><small>Tesorería</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="profile"><i>{{ iniciales }}</i><div><b>{{ nombre }}</b><small>Tesorería</small></div></div>
      <p>CAJA CHICA</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="irA(m.id)"><span>{{ m.icono }}</span>{{ m.nombre }}<em v-if="m.total!==undefined">{{ m.total }}</em></button>
      <div class="bottom"><button @click="salir"><span>↪</span>Cerrar sesión</button></div>
    </aside>

    <main>
      <header>
        <div><small>SIGTA / COMPRAS / {{ titulo }}</small><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <button class="refresh" :disabled="cargando" @click="cargar">↻ Actualizar</button>
      </header>

      <!-- ============================ RESUMEN ============================ -->
      <section v-if="vista==='resumen'">
        <div class="hero">
          <div><small>TESORERÍA</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Expedientes autorizados que esperan la entrega del efectivo.</p></div>
          <span>TS</span>
        </div>

        <div class="stats">
          <article @click="irA('desembolso')"><i class="gold">DE</i><div><small>Por desembolsar</small><b>{{ porDesembolsar.length }}</b><p>autorizados por el Director</p></div></article>
          <article @click="irA('historial')"><i class="blue">DS</i><div><small>Desembolsados</small><b>{{ desembolsados.length }}</b><p>fondos entregados</p></div></article>
          <article><i class="blue">MT</i><div><small>Monto desembolsado</small><b>{{ montoTotal }}</b><p>bolivianos en total</p></div></article>
          <article @click="irA('historial')"><i class="green">TT</i><div><small>Expedientes</small><b>{{ expedientes.length }}</b><p>en el sistema</p></div></article>
        </div>

        <div class="panels">
          <section class="panel">
            <div class="panel-head"><div><h3>Proceso de Compra — Caja Chica</h3></div></div>
            <div class="flow inactivo"><i class="gris">1</i><div><b>Enviar solicitud de compra</b><small>Sección solicitante</small></div></div>
            <div class="flow inactivo"><i class="gris">2</i><div><b>Verificar requisitos y emitir certificación</b><small>DAF</small></div></div>
            <div class="flow inactivo"><i class="gris">3</i><div><b>Autorizar compra</b><small>Director</small></div></div>
            <button class="flow" @click="irA('desembolso')"><i class="gold">4</i><div><b>Desembolsar dinero</b><small>Su tarea: entregar el efectivo y registrar el monto</small></div><strong>›</strong></button>
            <div class="flow inactivo"><i class="gris">5</i><div><b>Realizar compra y movimientos de almacén</b><small>Encargado de Compras y Almacén</small></div></div>
            <div class="flow inactivo"><i class="gris">6</i><div><b>Firmar acta y recibir la solicitud</b><small>Sección solicitante</small></div></div>
          </section>
          <section class="panel">
            <div class="panel-head"><div><small>SU FUNCIÓN</small><h3>Una sola tarea</h3></div></div>
            <p class="copy">En este proceso Tesorería no evalúa el expediente ni lo cierra: entrega el efectivo una vez que el Director autorizó la compra, y registra a quién se entregó.</p>
            <button class="wide primary" @click="irA('desembolso')">Ir a desembolsos →</button>
          </section>
        </div>
      </section>

      <!-- ========================== DESEMBOLSO ========================== -->
      <section v-else-if="vista==='desembolso'">
        <div class="instruction"><b>Desembolsar dinero</b><span>Entregue el efectivo y registre el monto y el responsable que lo recibe.</span></div>

        <div v-if="cargando" class="empty">Consultando expedientes…</div>

        <div v-else-if="!expedienteActivo" class="cards">
          <article v-for="e in porDesembolsar" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>autorizado</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li><b>Solicitante</b><span>{{ e.solicitante_nombre || 's/d' }}</span></li>
              <li><b>Área</b><span>{{ e.area_nombre || 's/d' }}</span></li>
              <li><b>Monto estimado</b><span>{{ e.monto_estimado ? `Bs ${e.monto_estimado}` : 's/d' }}</span></li>
            </ul>
            <p class="situacion">{{ e.situacion }}</p>
            <div class="actions">
              <button @click="verDetalle(e)">Ver expediente</button>
              <button class="primary" @click="abrir(e)">Desembolsar</button>
            </div>
          </article>
          <div v-if="!porDesembolsar.length" class="empty">
            <span>✓</span>
            <h3>Sin desembolsos pendientes</h3>
            <p>Los expedientes llegan aquí cuando el Director autoriza la compra.</p>
          </div>
        </div>

        <div v-else class="panel hoja">
          <div class="hoja-head">
            <div><small>DESEMBOLSO</small><h3>{{ expedienteActivo.codigo }} — {{ expedienteActivo.titulo }}</h3></div>
            <button class="refresh" @click="expedienteActivo=null">Volver</button>
          </div>

          <p class="copy">
            <b>Solicitante:</b> {{ expedienteActivo.solicitante_nombre }}<br>
            <b>Monto estimado:</b> Bs {{ expedienteActivo.monto_estimado || 's/d' }}<br>
            <b>Certificación presupuestaria:</b>
            <a v-if="expedienteActivo.certificacion_presupuestaria" :href="expedienteActivo.certificacion_presupuestaria" target="_blank">ver documento</a>
            <span v-else>no adjunta</span>
          </p>

          <label class="campo">Monto desembolsado (Bs)
            <input v-model="form.monto_desembolsado" type="number" min="0" step="0.01" placeholder="0.00">
          </label>
          <label class="campo">Responsable que recibe el efectivo
            <input v-model="form.responsable_adquisicion" type="text" placeholder="Nombre de quien retira el dinero">
          </label>

          <p v-if="error" class="error-linea">{{ error }}</p>

          <div class="actions">
            <button @click="expedienteActivo=null">Cancelar</button>
            <button class="primary" :disabled="procesando||!form.monto_desembolsado||!form.responsable_adquisicion.trim()" @click="desembolsar">Registrar desembolso</button>
          </div>
        </div>
      </section>

      <!-- =========================== HISTORIAL =========================== -->
      <section v-else-if="vista==='historial'">
        <div class="instruction"><b>Historial</b><span>Expedientes en los que Tesorería ya entregó los fondos.</span></div>
        <div v-if="desembolsados.length" class="cards">
          <article v-for="e in desembolsados" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>{{ etiquetaEstado(e.estado) }}</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li><b>Desembolsado</b><span>Bs {{ e.monto_desembolsado }}</span></li>
              <li><b>Entregado a</b><span>{{ e.responsable_adquisicion || 's/d' }}</span></li>
              <li><b>Retiro confirmado</b><span>{{ e.fondos_recibidos_en ? `${e.fondos_recibidos_por}` : 'pendiente' }}</span></li>
            </ul>

            <p class="situacion" :class="{ aviso: !e.fondos_recibidos_en }">
              {{ e.fondos_recibidos_en
                 ? `Retirado el ${fecha(e.fondos_recibidos_en)} · ${e.situacion}`
                 : 'El Encargado de Compras aún no confirma el retiro del efectivo' }}
            </p>

            <div class="actions"><button @click="verDetalle(e)">Ver expediente</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin registros</h3><p>Todavía no ha realizado desembolsos.</p></div>
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
            <div class="detalle-campo"><b>Estado</b><span>{{ etiquetaEstado(detalle.estado) }}</span></div>
            <div class="detalle-campo"><b>Monto estimado</b><span>Bs {{ detalle.monto_estimado || 's/d' }}</span></div>
          </div>
          <div class="detalle-fila">
            <div class="detalle-campo"><b>Solicitante</b><span>{{ detalle.solicitante_nombre }}</span></div>
            <div class="detalle-campo"><b>Área</b><span>{{ detalle.area_nombre || 's/d' }}</span></div>
          </div>
          <div class="detalle-campo"><b>Descripción</b><p>{{ detalle.descripcion }}</p></div>
          <div class="detalle-campo"><b>Justificación</b><p>{{ detalle.justificacion || 's/d' }}</p></div>
          <div class="detalle-campo"><b>Documentos</b>
            <p class="documentos">
              <a v-if="detalle.informe" :href="detalle.informe" target="_blank">Informe</a>
              <a v-if="detalle.proforma" :href="detalle.proforma" target="_blank">Proforma</a>
              <a v-if="detalle.poa" :href="detalle.poa" target="_blank">POA</a>
              <a v-if="detalle.certificacion_presupuestaria" :href="detalle.certificacion_presupuestaria" target="_blank">Certificación</a>
            </p>
          </div>
          <div class="detalle-campo" v-if="detalle.monto_desembolsado"><b>Desembolso</b><span>Bs {{ detalle.monto_desembolsado }} — recibió {{ detalle.responsable_adquisicion }}</span></div>
          <div class="detalle-campo" v-if="detalle.motivo_rechazo"><b>Motivo del rechazo</b><p>{{ detalle.motivo_rechazo }}</p></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))
const vista = ref('resumen')
const menuAbierto = ref(false)
const expedientes = ref([])
const cargando = ref(false)
const procesando = ref(false)
const expedienteActivo = ref(null)
const detalle = ref(null)
const error = ref('')

const nombre = computed(() => usuario.value.nombre || usuario.value.nombre_completo || 'Tesorería')
const primerNombre = computed(() => nombre.value.split(' ')[0])
const iniciales = computed(() => nombre.value.split(' ').slice(0, 2).map(x => x[0]).join('').toUpperCase())
const saludo = computed(() => new Date().getHours() < 12 ? 'Buenos días' : new Date().getHours() < 19 ? 'Buenas tardes' : 'Buenas noches')

/* Su única tarea del BPMN: desembolsar tras la autorización del Director. */
const porDesembolsar = computed(() => expedientes.value.filter(e => e.estado === 'APROBADO_PARA_DESEMBOLSO'))
const desembolsados = computed(() => expedientes.value.filter(e => !!e.monto_desembolsado))
const montoTotal = computed(() =>
  desembolsados.value
    .reduce((total, e) => total + Number(e.monto_desembolsado || 0), 0)
    .toLocaleString('es-BO', { minimumFractionDigits: 2 })
)

const menu = computed(() => [
  { id: 'resumen', icono: '⌂', nombre: 'Dashboard' },
  { id: 'desembolso', icono: 'DE', nombre: 'Desembolsar dinero', total: porDesembolsar.value.length },
  { id: 'historial', icono: 'HI', nombre: 'Historial', total: desembolsados.value.length },
])

const titulo = computed(() => ({
  resumen: 'Dashboard de Tesorería',
  desembolso: 'Desembolsar dinero',
  historial: 'Historial de desembolsos',
}[vista.value]))

const subtitulo = computed(() => ({
  resumen: 'Entrega de fondos de Caja Chica para las compras autorizadas.',
  desembolso: 'Expedientes autorizados por el Director que esperan el efectivo.',
  historial: 'Desembolsos ya realizados.',
}[vista.value]))

const ETIQUETAS = {
  CREADO_PENDIENTE_DAF: 'Esperando revisión de la DAF',
  EVALUADO_PENDIENTE_CERTIFICACION: 'Esperando certificación de la DAF',
  VERIFICADO_PENDIENTE_AUTORIZACION: 'Esperando autorización del Director',
  APROBADO_PARA_DESEMBOLSO: 'Autorizado — pendiente de desembolso',
  FONDOS_DESEMBOLSADOS: 'Fondos entregados',
  COMPRA_REGISTRADA: 'Compra realizada',
  COMPRADO_Y_ENTREGADO: 'Entregado al solicitante',
  DESCARGO_PENDIENTE_LIQUIDACION: 'Acta firmada',
  CERRADO_ARCHIVADO: 'Cerrado y archivado',
  RECHAZADO: 'Rechazado',
  ANULADO: 'Anulado',
}

function etiquetaEstado(estado) {
  return ETIQUETAS[estado] || estado
}

function fecha(valor) {
  return valor
    ? new Date(valor).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' })
    : 's/d'
}

const token = () => localStorage.getItem('sigta_token')

async function cargar() {
  cargando.value = true
  try {
    const r = await fetch('/api/compras/solicitudes/', { headers: { Authorization: `Token ${token()}` } })
    const d = await r.json()
    expedientes.value = Array.isArray(d) ? d : (d.results || [])
  } finally {
    cargando.value = false
  }
}

function irA(id) {
  vista.value = id
  menuAbierto.value = false
  expedienteActivo.value = null
  error.value = ''
}

function abrir(e) {
  expedienteActivo.value = e
  form.monto_desembolsado = e.monto_estimado || ''
  form.responsable_adquisicion = ''
  error.value = ''
}

function verDetalle(e) { detalle.value = e }

function salir() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.push('/login')
}

const form = reactive({ monto_desembolsado: '', responsable_adquisicion: '' })

async function desembolsar() {
  error.value = ''
  procesando.value = true
  try {
    const r = await fetch(`/api/compras/solicitudes/${expedienteActivo.value.id}/desembolsar/`, {
      method: 'POST',
      headers: { Authorization: `Token ${token()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        monto_desembolsado: form.monto_desembolsado,
        responsable_adquisicion: form.responsable_adquisicion.trim(),
      }),
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible registrar el desembolso.')
    await cargar()
    expedienteActivo.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    procesando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.layout{min-height:100vh;background:var(--sigta-fondo);color:var(--sigta-texto);font-family:var(--sigta-fuente)}aside{position:fixed;inset:0 auto 0 0;width:var(--sigta-sidebar);background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand,.profile{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 20px;border-bottom:1px solid rgba(255,255,255,.2)}.brand>b{background:var(--sigta-mostaza);color:var(--sigta-azul);padding:14px 10px;border-radius:9px}.brand strong,.brand small,.profile b,.profile small{display:block}.brand strong{font-size:23px}.brand small,.profile small{color:var(--sigta-azul-texto-claro);margin-top:3px}.profile{padding:22px 10px}.profile>i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}aside>p{font-size:10px;color:var(--sigta-azul-texto-claro);font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{border:0;background:transparent;color:var(--sigta-blanco);border-radius:8px;padding:12px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0;width:100%}aside button>span{font-size:10px;font-weight:900;width:28px}aside button em{margin-left:auto;background:rgba(255,255,255,.16);padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:rgba(255,255,255,.13)}.bottom{margin-top:auto;border-top:1px solid rgba(255,255,255,.2);padding-top:10px}.bottom button{width:100%}main{margin-left:var(--sigta-sidebar);padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header small{color:var(--sigta-texto-suave)}h1{font-size:var(--sigta-titulo);margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.refresh{border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-azul);padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-azul-medio));color:var(--sigta-blanco);border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small,.hoja-head small{font-size:10px;font-weight:800;letter-spacing:1.4px;color:var(--sigta-mostaza-clara)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero>span{width:68px;height:68px;border:1px solid var(--sigta-mostaza);border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px;display:flex;gap:13px;cursor:pointer}.stats i,.flow i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:var(--sigta-blanco);font-size:10px;font-weight:900;flex-shrink:0}.blue{background:var(--sigta-azul)}.gold{background:var(--sigta-mostaza);color:var(--sigta-texto)!important}.green{background:var(--sigta-azul-medio)}.gris{background:var(--sigta-borde);color:var(--sigta-texto-suave)!important}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.panels{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}.panel-head h3{margin:5px 0 14px}.flow{width:100%;border:0;border-top:1px solid var(--sigta-borde-suave);background:var(--sigta-blanco);padding:15px 2px;display:flex;gap:13px;align-items:center;text-align:left;cursor:pointer}.flow.inactivo{cursor:default;opacity:.6}.flow div{flex:1}.flow b,.flow small{display:block}.flow small{color:var(--sigta-texto-suave);margin-top:4px}.flow>strong{font-size:20px}.copy{color:var(--sigta-texto-suave);font-size:12px;line-height:1.8}.copy a{color:var(--sigta-azul)}.wide{width:100%;padding:10px;border-radius:7px;border:1px solid var(--sigta-borde);cursor:pointer}.primary{background:var(--sigta-azul)!important;color:var(--sigta-blanco)!important;border-color:var(--sigta-azul)!important}.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;margin-bottom:17px;border-radius:7px}.instruction b,.instruction span{display:block}.instruction span{font-size:12px;color:var(--sigta-alerta);margin-top:4px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.cards article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px}.top{display:flex;justify-content:space-between;gap:8px}.top span{font-size:12px;font-weight:800;color:var(--sigta-azul)}.top em{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px;font-style:normal;white-space:nowrap}.cards h3{font-size:17px;margin:15px 0 7px}.cards article>p{font-size:12px;color:var(--sigta-texto-suave);min-height:36px}.datos{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:4px}.datos li{display:flex;justify-content:space-between;gap:10px;font-size:11px;border-bottom:1px dashed var(--sigta-borde-suave);padding-bottom:3px}.datos b{color:var(--sigta-texto-suave)}.datos span{color:var(--sigta-texto-suave);text-align:right}.actions{display:flex;gap:7px;border-top:1px solid var(--sigta-borde-suave);padding-top:13px;margin-top:10px}.actions button{flex:1;padding:9px 6px;border-radius:7px;border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-texto);font-weight:700;cursor:pointer}.actions button:disabled{opacity:.55;cursor:not-allowed}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-borde);padding:65px;border-radius:10px;color:var(--sigta-texto-suave)}.empty>span{font-size:31px;color:var(--sigta-exito)}.empty h3{margin:10px 0 6px}.campo{display:block;margin:14px 0;font-size:12px;font-weight:700;color:var(--sigta-texto)}.campo input{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-borde);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}.situacion{font-size:11px;color:var(--sigta-texto-suave);background:var(--sigta-azul-tenue);border-radius:6px;padding:8px 10px;margin:0 0 10px}.situacion.aviso{background:var(--sigta-mostaza-suave);color:var(--sigta-alerta);font-weight:700}.error-linea{background:var(--sigta-error-fondo);color:var(--sigta-error);padding:10px 13px;border-radius:7px;font-size:12px;font-weight:700}.hoja{max-width:760px}.hoja-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:16px}.hoja-head h3{margin:5px 0 0}.documentos{display:flex;gap:12px;flex-wrap:wrap}.documentos a{color:var(--sigta-azul);font-size:12px}.detalle-modal-backdrop{position:fixed;inset:0;background:rgba(18,58,107,.55);display:grid;place-items:center;padding:20px;z-index:20}.detalle-modal{background:var(--sigta-blanco);border-radius:14px;width:min(700px,100%);max-height:88vh;display:flex;flex-direction:column}.detalle-modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--sigta-borde-suave)}.detalle-modal-header h3{margin:0}.detalle-modal-header small{color:var(--sigta-texto-suave)}.detalle-modal-close{border:0;background:transparent;font-size:20px;cursor:pointer;color:var(--sigta-texto-suave)}.detalle-modal-body{padding:20px 24px;overflow-y:auto;display:grid;gap:14px}.detalle-fila{display:grid;grid-template-columns:1fr 1fr;gap:14px}.detalle-campo b{display:block;font-size:11px;color:var(--sigta-texto-suave);margin-bottom:4px}.detalle-campo span,.detalle-campo p{font-size:13px;color:var(--sigta-texto);margin:0}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:760px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column;gap:12px}.detalle-fila{grid-template-columns:1fr}}
</style>
