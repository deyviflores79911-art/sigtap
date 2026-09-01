<template>
  <div class="shell">
    <aside class="side">
      <div class="brand">SIGTA <small>Jefatura DAF</small></div>
      <button v-for="tab in tabs" :key="tab.id" :class="{ active: activo === tab.id }" @click="activo = tab.id">
        <span>{{ tab.icon }}</span>{{ tab.nombre }}
      </button>
      <router-link class="config" to="/usuario/configuracion">⚙ Configuración</router-link>
      <button class="salir" @click="cerrarSesion">Cerrar sesión</button>
    </aside>

    <main>
      <header>
        <div><p>JEFATURA DAF</p><h1>{{ titulo }}</h1></div>
        <div class="usuario"><span>{{ nombreUsuario }}</span><span class="avatar">{{ iniciales }}</span></div>
      </header>

      <div v-if="mensaje" :class="['mensaje', mensajeError ? 'error' : 'ok']">{{ mensaje }}</div>

      <section v-if="activo === 'resumen'" class="resumen">
        <article><strong>{{ pendientes.length }}</strong><span>Por validar y asignar</span></article>
        <article><strong>{{ asignados.length }}</strong><span>En evaluación del Técnico DAF</span></article>
        <article><strong>{{ certificados.length }}</strong><span>Certificados / procesados</span></article>
        <div class="panel ancho"><h2>Flujo de trabajo</h2><p>Jefe DAF valida y prioriza → Técnico DAF evalúa y certifica → Jefe DAF emite el informe de aprobación.</p></div>
      </section>

      <section v-else-if="activo === 'validar'" class="panel">
        <h2>Expedientes pendientes</h2>
        <p class="sub">Revise la documentación, defina la prioridad y derive el expediente al Técnico DAF.</p>
        <div v-if="!pendientes.length" class="vacio">No existen expedientes pendientes de asignación.</div>
        <article v-for="item in pendientes" :key="item.id" class="expediente">
          <div class="info"><b>{{ item.codigo }} · {{ item.titulo }}</b><span>{{ item.solicitante_nombre }} · {{ item.area_nombre || 'Sin área' }}</span><small>{{ item.descripcion }}</small></div>
          <div class="docs">
            <a v-for="doc in documentos(item)" :key="doc.nombre" :href="doc.url" target="_blank">{{ doc.nombre }}</a>
          </div>
          <button class="primario" @click="abrirAsignacion(item)">Validar y asignar</button>
        </article>
      </section>

      <section v-else-if="activo === 'informes'" class="panel">
        <h2>Informes de los Técnicos DAF</h2>
        <div v-if="!columnasTecnicos.length" class="vacio">Todavía no existen expedientes asignados.</div>
        <div class="columnas">
          <div v-for="grupo in columnasTecnicos" :key="grupo.nombre" class="columna">
            <h3>{{ grupo.nombre }}</h3>
            <article v-for="item in grupo.items" :key="item.id" class="tarjeta">
              <b>{{ item.codigo }}</b><span>{{ item.titulo }}</span><em>{{ item.estado_nombre }}</em>
              <a v-if="item.certificacion_presupuestaria" :href="item.certificacion_presupuestaria" target="_blank">Ver certificación</a>
            </article>
          </div>
        </div>
      </section>

      <section v-else class="panel">
        <h2>Mis informes para el Director</h2>
        <form class="form" @submit.prevent="crearInforme">
          <label>Tipo<select v-model="informe.tipo" required><option value="APROBACION_DAF">Aprobación posterior a certificación</option><option value="ACTIVIDADES">Trabajos y actividades asignadas</option></select></label>
          <label>Título<input v-model.trim="informe.titulo" required></label>
          <label>Periodo<input v-model.trim="informe.periodo" placeholder="Ej. Agosto 2026" required></label>
          <label class="completo">Contenido<textarea v-model.trim="informe.contenido" rows="5" required></textarea></label>
          <label class="check"><input v-model="informe.enviado_director" type="checkbox"> Enviar al Director al registrar</label>
          <button class="primario" :disabled="guardando">{{ guardando ? 'Guardando…' : 'Registrar informe' }}</button>
        </form>
        <div class="lista-informes"><article v-for="item in misInformes" :key="item.id"><b>{{ item.titulo }}</b><span>{{ item.periodo }} · {{ etiquetaTipo(item.tipo) }}</span><em>{{ item.enviado_director ? 'Enviado al Director' : 'Borrador' }}</em></article></div>
      </section>
    </main>

    <div v-if="seleccionado" class="fondo" @click.self="seleccionado = null">
      <form class="modal" @submit.prevent="asignar">
        <button type="button" class="cerrar" @click="seleccionado = null">×</button>
        <p>VALIDACIÓN DAF</p><h2>{{ seleccionado.codigo }}</h2>
        <label>Técnico DAF<select v-model="asignacion.tecnico_daf_id" required><option value="">Seleccione</option><option v-for="t in tecnicos" :key="t.id" :value="t.id">{{ t.nombre_completo }} · {{ t.email }}</option></select></label>
        <label>Prioridad<select v-model="asignacion.prioridad" required><option value="BAJA">Baja</option><option value="MEDIA">Media</option><option value="ALTA">Alta</option><option value="URGENTE">Urgente</option></select></label>
        <label>Criterio de prioridad<textarea v-model.trim="asignacion.criterio_prioridad" rows="4" placeholder="Explique por qué se asigna esta prioridad" required></textarea></label>
        <button class="primario" :disabled="guardando || !asignacion.tecnico_daf_id || !asignacion.prioridad || !asignacion.criterio_prioridad.trim()">Confirmar y pasar al Técnico DAF</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activo = ref('resumen'), compras = ref([]), tecnicos = ref([]), misInformes = ref([])
const seleccionado = ref(null), mensaje = ref(''), mensajeError = ref(false), guardando = ref(false)
const tabs = [{id:'resumen',nombre:'Dashboard',icon:'▦'},{id:'validar',nombre:'Validar y asignar',icon:'✓'},{id:'informes',nombre:'Informes de trabajo',icon:'▤'},{id:'mios',nombre:'Mis informes',icon:'✎'}]
const usuario = computed(() => { try { return JSON.parse(localStorage.getItem('sigta_usuario') || '{}') } catch { return {} } })
const nombreUsuario = computed(() => usuario.value.nombre_completo || usuario.value.email || 'Jefe DAF')
const iniciales = computed(() => nombreUsuario.value.split(' ').slice(0,2).map(x=>x[0]).join('').toUpperCase())
const titulo = computed(() => tabs.find(x=>x.id===activo.value)?.nombre || 'Dashboard')
const pendientes = computed(() => compras.value.filter(x=>x.estado==='CREADO_PENDIENTE_DAF' && !x.tecnico_daf))
const asignados = computed(() => compras.value.filter(x=>x.tecnico_daf && ['CREADO_PENDIENTE_DAF','EVALUADO_PENDIENTE_CERTIFICACION'].includes(x.estado)))
const certificados = computed(() => compras.value.filter(x=>!['CREADO_PENDIENTE_DAF','EVALUADO_PENDIENTE_CERTIFICACION'].includes(x.estado)))
const columnasTecnicos = computed(() => Object.entries(compras.value.filter(x=>x.tecnico_daf).reduce((a,x)=>{ const n=x.tecnico_daf_nombre||'Técnico DAF'; (a[n] ||= []).push(x); return a },{})).map(([nombre,items])=>({nombre,items})))
const asignacion = reactive({tecnico_daf_id:'',prioridad:'MEDIA',criterio_prioridad:''})
const informe = reactive({tipo:'APROBACION_DAF',titulo:'',periodo:'',contenido:'',enviado_director:false})
const auth = () => ({Authorization:`Token ${localStorage.getItem('sigta_token')}`,Accept:'application/json','Content-Type':'application/json'})
const lista = data => Array.isArray(data) ? data : (data.results || [])
async function api(url, options={}) { const r=await fetch(url,{...options,headers:{...auth(),...(options.headers||{})}}); const data=await r.json().catch(()=>({})); if(!r.ok) throw new Error(data.detalle || Object.values(data).flat().join(' ') || 'No se pudo completar la operación.'); return data }
async function cargar(){ try { const [c,t,i]=await Promise.all([api('/api/compras/solicitudes/'),api('/api/usuarios/usuarios-por-rol/?rol=DAF'),api('/api/usuarios/informes-jefatura/')]); compras.value=lista(c); tecnicos.value=lista(t); misInformes.value=lista(i) } catch(e){ avisar(e.message,true) } }
function documentos(x){ return [{nombre:'Informe',url:x.informe},{nombre:'POA',url:x.poa},{nombre:'Pedido',url:x.pedido},{nombre:'Proforma',url:x.proforma}].filter(x=>x.url) }
function abrirAsignacion(x){ seleccionado.value=x; asignacion.tecnico_daf_id=''; asignacion.prioridad='MEDIA'; asignacion.criterio_prioridad='' }
async function asignar(){ guardando.value=true; try { await api(`/api/compras/solicitudes/${seleccionado.value.id}/validar-asignar-daf/`,{method:'POST',body:JSON.stringify({...asignacion,tecnico_daf_id:Number(asignacion.tecnico_daf_id)})}); seleccionado.value=null; avisar('Expediente validado y enviado al Técnico DAF.'); await cargar() } catch(e){ avisar(e.message,true) } finally { guardando.value=false } }
async function crearInforme(){ guardando.value=true; try { await api('/api/usuarios/informes-jefatura/',{method:'POST',body:JSON.stringify(informe)}); Object.assign(informe,{tipo:'APROBACION_DAF',titulo:'',periodo:'',contenido:'',enviado_director:false}); avisar('Informe registrado correctamente.'); await cargar() } catch(e){ avisar(e.message,true) } finally { guardando.value=false } }
function etiquetaTipo(x){ return x==='APROBACION_DAF'?'Aprobación DAF':'Actividades' }
function avisar(texto,error=false){ mensaje.value=texto; mensajeError.value=error; setTimeout(()=>{mensaje.value=''},4500) }
function cerrarSesion(){ localStorage.removeItem('sigta_token'); localStorage.removeItem('sigta_usuario'); router.push('/login') }
onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.shell{min-height:100vh;background:#f3f6fb;color:#17223b;font-family:Inter,Arial,sans-serif;display:flex}.side{width:250px;background:#172a52;color:white;padding:28px 16px;display:flex;flex-direction:column;gap:8px}.brand{font-size:26px;font-weight:800;margin:0 12px 34px}.brand small{display:block;font-size:12px;color:#b9c7df;margin-top:5px}.side button,.config{border:0;background:transparent;color:#dce5f5;text-align:left;padding:13px 15px;border-radius:9px;font-size:14px;text-decoration:none;cursor:pointer}.side button span{display:inline-block;width:28px}.side button.active,.side button:hover,.config:hover{background:#294577;color:white}.side .config{margin-top:auto}.side .salir{color:#ffcaca}main{flex:1;padding:30px 38px;min-width:0}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}header p,.modal>p{color:#6b7c96;font-size:12px;font-weight:800;letter-spacing:.1em;margin:0}h1{margin:4px 0;font-size:28px}.usuario{display:flex;gap:12px;align-items:center}.avatar{background:#e5ad24;color:#172a52;width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font-weight:800}.resumen{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.resumen>article,.panel{background:white;border:1px solid #e2e8f1;border-radius:14px;padding:24px;box-shadow:0 5px 20px #1c33500c}.resumen article strong{display:block;font-size:34px;color:#244c83}.resumen article span,.sub,.info span,.info small{display:block;color:#718096;margin-top:6px}.ancho{grid-column:1/-1}.panel h2{margin-top:0}.expediente{display:grid;grid-template-columns:1fr auto auto;gap:20px;align-items:center;border-top:1px solid #e8edf4;padding:18px 0}.info{min-width:0}.docs{display:flex;gap:8px;flex-wrap:wrap}.docs a,.tarjeta a{color:#205aa3;font-size:13px}.primario{background:#1d5a9b;color:white;border:0;border-radius:8px;padding:11px 16px;font-weight:700;cursor:pointer}.columnas{display:flex;gap:16px;overflow:auto}.columna{background:#f3f6fa;border-radius:12px;padding:14px;min-width:280px}.tarjeta,.lista-informes article{background:white;border:1px solid #e2e8f1;padding:14px;border-radius:9px;margin:9px 0;display:flex;flex-direction:column;gap:6px}.tarjeta span,.lista-informes span{font-size:13px;color:#68768b}.tarjeta em,.lista-informes em{font-size:12px;color:#245b8d;font-style:normal}.form{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-bottom:25px}label{font-size:13px;font-weight:700;display:flex;flex-direction:column;gap:6px}input,select,textarea{width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:7px;font:inherit}.completo{grid-column:1/-1}.check{flex-direction:row;align-items:center}.check input{width:auto}.fondo{position:fixed;inset:0;background:#0d1a31aa;display:grid;place-items:center;padding:20px}.modal{position:relative;background:white;border-radius:15px;padding:28px;width:min(520px,100%);display:flex;flex-direction:column;gap:15px}.cerrar{position:absolute;right:16px;top:12px;background:none;border:0;font-size:25px}.mensaje{position:fixed;right:25px;top:20px;z-index:10;padding:14px 18px;border-radius:9px;color:white}.mensaje.ok{background:#16734a}.mensaje.error{background:#b42318}.vacio{padding:35px;text-align:center;color:#718096}@media(max-width:850px){.shell{display:block}.side{width:100%;height:auto}.brand{margin-bottom:10px}.side .config{margin-top:8px}main{padding:22px 15px}.resumen{grid-template-columns:1fr}.expediente{grid-template-columns:1fr}.form{grid-template-columns:1fr}.completo{grid-column:auto}}
</style>
