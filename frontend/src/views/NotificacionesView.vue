<template>
  <div class="notification-layout">
    <SolicitanteMenu v-if="!esTecnico" />
    <aside v-else class="technician-nav">
      <div class="tech-brand"><img src="/img/emi.jpg" alt="EMI"><div><b>SIGTA</b><small>Soporte Técnico</small></div></div>
      <div class="tech-profile"><i>{{iniciales}}</i><div><b>{{nombre}}</b><small>Especialista</small></div></div>
      <p>MI TRABAJO</p>
      <button @click="irSeccion('resumen')"><span>⌂</span>Dashboard</button>
      <button @click="irSeccion('misordenes')"><span>OT</span>Mis órdenes</button>
      <button @click="irSeccion('curso')"><span>TC</span>Trabajos en curso</button>
      <button @click="irSeccion('cotizaciones')"><span>CO</span>Cotizaciones y requerimientos</button>
      <button @click="irSeccion('trabajo')"><span>RP</span>Trabajos y anotaciones</button>
      <button @click="irSeccion('informes')"><span>IF</span>Pruebas e informes</button>
      <button @click="irSeccion('compras')"><span>CP</span>Seguimiento de compras</button>
      <button class="active"><span>●</span>Notificaciones <em v-if="pendientes">{{pendientes}}</em></button>
      <button @click="irSeccion('historial')"><span>HI</span>Historial</button>
      <button class="tech-logout" @click="salir">↪　Cerrar sesión</button>
    </aside>
    <main class="page">
    <header>
      <button class="back" @click="router.push(rutaVolver)" aria-label="Volver al panel"><span>←</span> Volver al panel</button>
      <div><small>CENTRO DE AVISOS</small><h1>Notificaciones</h1><p>Decisiones y novedades relacionadas con sus tickets.</p></div>
      <button v-if="pendientes" class="read-all" @click="marcarTodas">Marcar todas como leídas</button>
    </header>
    <section class="summary">
      <div><b>{{pendientes}}</b><span>Sin leer</span></div>
      <div class="summary-approved"><b>{{aprobadas}}</b><span>Aprobadas</span></div>
      <div class="summary-rejected"><b>{{rechazadas}}</b><span>Rechazadas</span></div>
      <div class="summary-total"><b>{{notificaciones.length}}</b><span>Total</span></div>
    </section>
    <section class="list">
      <article v-for="n in notificaciones" :key="n.id" :class="[n.tipo.toLowerCase(),{unread:!n.leida}]">
        <i>{{n.tipo==='EXITO'?'✓':n.tipo==='RECHAZO'?'!':'i'}}</i>
        <div><div class="title"><strong>{{n.titulo}}</strong><em v-if="!n.leida">Nueva</em></div><p>{{n.mensaje}}</p><small>{{fecha(n.creada_en)}} · {{n.ticket_titulo}}</small></div>
        <div class="actions"><button @click="verDetalle(n)">Ver detalles</button><button v-if="!n.leida" class="secondary" @click="marcarLeida(n)">Marcar leída</button></div>
      </article>
      <div v-if="!cargando&&!notificaciones.length" class="empty"><span>✓</span><h3>Está al día</h3><p>No tiene notificaciones registradas.</p></div>
      <div v-if="cargando" class="empty">Consultando notificaciones…</div>
    </section>
    </main>
  </div>
</template>

<script setup>
import {computed,onMounted,ref} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import SolicitanteMenu from '../components/SolicitanteMenu.vue'
const router=useRouter(),route=useRoute(),notificaciones=ref([]),cargando=ref(true)
const usuario=JSON.parse(localStorage.getItem('sigta_usuario')||'{}'),roles=(usuario.roles||[]).map(r=>String(r?.codigo||r).toUpperCase())
const esTecnico=route.path.startsWith('/especialista/')||roles.includes('ESPECIALISTA')||roles.includes('AGENTE'),rutaVolver=esTecnico?'/especialista/dashboard':'/usuario/dashboard'
const nombre=usuario.nombre||usuario.nombre_completo||'Técnico',iniciales=nombre.split(' ').slice(0,2).map(x=>x[0]).join('').toUpperCase()
const pendientes=computed(()=>notificaciones.value.filter(n=>!n.leida).length)
const aprobadas=computed(()=>notificaciones.value.filter(n=>n.tipo==='EXITO').length)
const rechazadas=computed(()=>notificaciones.value.filter(n=>n.tipo==='RECHAZO').length)
const headers=()=>({Authorization:`Token ${localStorage.getItem('sigta_token')}`,Accept:'application/json'})
async function cargar(){cargando.value=true;try{const r=await fetch('/api/soporte/notificaciones/',{headers:headers()}),d=await r.json();notificaciones.value=Array.isArray(d)?d:d.results||[]}finally{cargando.value=false}}
async function marcarLeida(n){await fetch(`/api/soporte/notificaciones/${n.id}/marcar-leida/`,{method:'POST',headers:headers()});n.leida=true}
async function marcarTodas(){await fetch('/api/soporte/notificaciones/marcar-todas-leidas/',{method:'POST',headers:headers()});notificaciones.value.forEach(n=>n.leida=true)}
async function verDetalle(n){if(!n.leida)await marcarLeida(n);router.push(esTecnico?{path:'/especialista/dashboard',query:{ticket:n.ticket}}:{path:'/usuario/mis-solicitudes',query:{proceso:'SOPORTE',id:n.ticket,origen:'notificaciones'}})}
function fecha(v){return new Date(v).toLocaleString('es-BO',{dateStyle:'medium',timeStyle:'short'})}
function irSeccion(vista){router.push({path:'/especialista/dashboard',query:{vista}})}
function salir(){localStorage.removeItem('sigta_token');localStorage.removeItem('sigta_usuario');router.push('/login')}
onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.page{min-height:100vh;padding:30px;background:var(--sigta-azul-tenue);color:var(--sigta-texto);font-family:var(--sigta-fuente)}header{max-width:1050px;margin:auto auto 18px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:20px;background:linear-gradient(120deg,var(--sigta-azul),#315f8b);color:#fff;border-radius:15px;padding:22px 25px}header small{color:var(--sigta-mostaza-clara);font-weight:900;letter-spacing:1px}h1{margin:3px 0;font-size:26px}header p{margin:0;color:#d2e1ef}.back,.read-all{border:1px solid #ffffff55;background:#ffffff12;color:#fff;border-radius:8px;padding:10px 13px;font-weight:800;cursor:pointer}.read-all{background:var(--sigta-mostaza);border-color:var(--sigta-mostaza);color:var(--sigta-azul)}.summary{max-width:1050px;margin:auto auto 14px;display:flex;gap:10px}.summary div{background:#fff;border:1px solid var(--sigta-borde);border-radius:9px;padding:10px 18px}.summary b,.summary span{display:block}.summary b{font-size:20px;color:var(--sigta-azul)}.summary span{font-size:10px;color:var(--sigta-texto-suave)}.list{max-width:1050px;margin:auto;display:grid;gap:10px}.list article{display:grid;grid-template-columns:44px 1fr auto;align-items:center;gap:14px;background:#fff;border:1px solid var(--sigta-borde);border-radius:11px;padding:16px}.list article.unread{box-shadow:inset 4px 0 var(--sigta-mostaza)}.list article.rechazo{border-color:#efc7c7}.list article>i{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:var(--sigta-azul-tenue);color:var(--sigta-azul);font-style:normal;font-weight:900}.list article.rechazo>i{background:var(--sigta-error-fondo);color:var(--sigta-error)}.title{display:flex;gap:9px;align-items:center}.title em{font-size:9px;font-style:normal;background:var(--sigta-mostaza-suave);color:var(--sigta-mostaza-oscuro);border-radius:9px;padding:3px 7px}.list p{margin:5px 0;color:var(--sigta-texto-suave)}.list small{color:var(--sigta-texto-suave)}.actions{display:flex;gap:7px;flex-direction:column}.actions button{border:0;background:var(--sigta-azul);color:#fff;border-radius:7px;padding:8px 11px;font-weight:800;cursor:pointer}.actions .secondary{background:#fff;color:var(--sigta-azul);border:1px solid var(--sigta-borde)}.empty{text-align:center;background:#fff;border:1px dashed var(--sigta-borde);border-radius:11px;padding:50px;color:var(--sigta-texto-suave)}.empty span{font-size:28px;color:var(--sigta-exito)}@media(max-width:700px){.page{padding:12px}header{grid-template-columns:1fr}.read-all,.back{width:100%}.list article{grid-template-columns:38px 1fr}.actions{grid-column:1/-1;flex-direction:row}.actions button{flex:1}}
</style>
<style scoped>
.notification-layout .technician-nav > button{gap:11px;padding:10px 12px;line-height:1.2}
.technician-nav > button span{flex:0 0 28px;width:28px;text-align:center;font-size:11px;font-weight:900}
.notification-layout .page > header{display:flex;min-height:124px;padding:24px 28px;background:var(--sigta-azul);box-shadow:0 8px 22px #0c2a4f14}
.notification-layout .page > header > div{order:2;flex:1}
.notification-layout .page > header .back{order:1;align-self:center;display:inline-flex;align-items:center;gap:8px;flex:0 0 auto;background:#fff;color:var(--sigta-azul);border-color:#fff;padding:10px 14px;box-shadow:0 3px 10px #001b3728}
.page > header .back span{font-size:18px}
.page > header .back:hover{background:var(--sigta-mostaza);border-color:var(--sigta-mostaza)}
.notification-layout .page > header .read-all{order:3;flex:0 0 auto}
@media(max-width:900px){.page > header{display:flex;flex-wrap:wrap}.page > header > div{order:1;flex-basis:100%}.page > header .back{order:2}.page > header .read-all{order:3;margin-left:auto}}
@media(max-width:700px){.page > header{display:grid}.page > header > div{order:1}.page > header .back{order:2;width:auto;justify-self:start}.page > header .read-all{order:3;width:100%;margin:0}}
</style>
<style scoped>
.page > .summary{grid-template-columns:repeat(4,minmax(130px,1fr))}
.page > .summary::after{display:none;content:none}
.summary div{border-top:3px solid var(--sigta-azul)}
.summary .summary-approved{border-top-color:var(--sigta-exito)}
.summary .summary-rejected{border-top-color:var(--sigta-error)}
.summary .summary-total{border-top-color:var(--sigta-mostaza)}
@media(max-width:900px){.page > .summary{grid-template-columns:repeat(2,1fr)}}
</style>
<style scoped>
.notification-layout{display:flex;min-height:100vh;background:var(--sigta-azul-tenue)}.notification-layout>.page{flex:1;min-width:0}.technician-nav{position:sticky;top:0;width:var(--sigta-sidebar);min-width:var(--sigta-sidebar);height:100vh;padding:22px 14px;background:var(--sigta-azul);color:#fff;display:flex;flex-direction:column}.tech-brand,.tech-profile{display:flex;align-items:center;gap:11px}.tech-brand{padding:0 8px 18px;border-bottom:1px solid #ffffff22}.tech-brand img{width:48px;height:48px;border-radius:10px}.tech-brand b,.tech-brand small,.tech-profile b,.tech-profile small{display:block}.tech-brand b{font-size:22px}.tech-brand small,.tech-profile small{color:#c7d8ea;font-size:11px}.tech-profile{padding:22px 8px}.tech-profile i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}.technician-nav>p{font-size:10px;color:#9db3cc;font-weight:900;letter-spacing:1px;margin:8px}.technician-nav>button{display:flex;align-items:center;width:100%;border:0;background:transparent;color:#d7e4f2;border-radius:8px;padding:12px;cursor:pointer;text-align:left;font-weight:700}.technician-nav>button em{margin-left:auto;background:#ffffff20;border-radius:12px;padding:2px 7px;font-style:normal}.technician-nav>button.active{background:#ffffff16;box-shadow:inset 3px 0 var(--sigta-mostaza);color:var(--sigta-mostaza)}.technician-nav>.tech-logout{margin-top:auto;justify-content:center;background:var(--sigta-mostaza);color:var(--sigta-azul)}@media(max-width:700px){.notification-layout{display:block}.technician-nav{position:static;width:100%;min-width:0;height:auto}.technician-nav .tech-profile,.technician-nav>p,.technician-nav>button:not(.active){display:none}.technician-nav>button.active{margin-top:10px}}
</style>
<style scoped>
.notification-layout>.page{padding:32px 38px}.page>header,.page>.summary,.page>.list{max-width:none;width:100%}.page>header{min-height:138px;padding:25px 30px;background:linear-gradient(120deg,var(--sigta-azul) 0%,#285786 72%,#356895 100%);box-shadow:0 12px 28px #0c2a4f18}.page>header h1{font-size:30px}.page>header .back{order:2;align-self:start;background:#ffffff12}.page>header>div{order:1}.page>header .read-all{order:3}.summary{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:12px;margin:0 0 18px}.summary:after{display:none;content:none}.summary div{padding:14px 18px;border-radius:11px;box-shadow:0 5px 15px #17324a0a}.list article{min-height:116px;padding:18px 20px;border-color:#d6e1ed;box-shadow:0 5px 16px #17324a0a;transition:transform .18s,box-shadow .18s}.list article:hover{transform:translateY(-2px);box-shadow:0 10px 24px #17324a14}.list article.unread{border-left:5px solid var(--sigta-mostaza);box-shadow:0 8px 22px #17324a12}.list article.rechazo{background:linear-gradient(90deg,#fff9f9,#fff 28%)}.list article.exito{background:linear-gradient(90deg,#f5fcf8,#fff 28%);border-color:#bfe3d0}.list article.exito>i{background:var(--sigta-exito-fondo);color:var(--sigta-exito)}.title strong{font-size:15px}.list p{font-size:13px;line-height:1.5}.actions button{min-width:128px;padding:10px 14px}.actions .secondary{font-size:11px}@media(max-width:900px){.notification-layout>.page{padding:20px}.page>header{grid-template-columns:1fr auto}.page>header>div{grid-column:1/-1}.page>header .back{order:initial}.summary{grid-template-columns:repeat(2,1fr)}}@media(max-width:700px){.notification-layout>.page{padding:12px}.page>header{grid-template-columns:1fr;padding:20px}.page>header .read-all,.page>header .back{order:initial}.summary{grid-template-columns:1fr 1fr}.list article{min-height:0}}
</style>
