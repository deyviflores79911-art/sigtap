<template>
  <div class="shell sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><span><img src="/img/emi.jpg" alt="EMI"></span><div><b>SIGTA</b><small>Dirección institucional</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="user"><i>{{ iniciales }}</i><div><strong>{{ nombre }}</strong><small>Director</small></div></div>
      <p>APROBACIÓN Y RECEPCIÓN</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="vista=m.id; menuAbierto=false"><em>{{ m.icono }}</em>{{ m.nombre }}<b v-if="m.total!==undefined">{{ m.total }}</b></button>
      <div class="logout"><button @click="salir"><em>↪</em>Cerrar sesión</button></div>
    </aside>

    <main>
      <header><div><span>SIGTA / Dirección / {{ titulo }}</span><h1>{{ titulo }}</h1><p>Vistos buenos y recepción de informes institucionales.</p></div><button class="refresh" @click="cargarTodo">↻ Actualizar</button></header>

      <section v-if="vista==='resumen'">
        <div class="hero"><div><small>BANDEJA EJECUTIVA</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Decisiones y documentos que requieren atención de Dirección.</p></div><span>DIR</span></div>
        <div class="stats">
          <article><i class="gold">VB</i><div><small>Vistos buenos</small><b>{{ comprasPendientes.length }}</b><p>Caja Chica</p></div></article>
          <article><i class="blue">AC</i><div><small>Autorizaciones</small><b>{{ soporteCompra.length }}</b><p>Compras técnicas</p></div></article>
          <article><i class="green">RM</i><div><small>Reportes mensuales</small><b>{{ reportesMantenimiento.length }}</b><p>Mantenimiento</p></div></article>
          <article><i class="navy">IF</i><div><small>Informes finales</small><b>{{ informesSoporte.length }}</b><p>Soporte técnico</p></div></article>
        </div>
        <section class="panel"><div class="panel-head"><div><small>RESPONSABILIDADES BPMN</small><h3>Acciones del Director</h3></div><span>{{ totalPendiente }} pendientes</span></div>
          <div class="flows">
            <button @click="vista='caja'"><i class="gold">01</i><div><b>Visto bueno de Caja Chica</b><p>Revisar expediente verificado y derivar a Tesorería para desembolso.</p></div><em>Compras</em><strong>›</strong></button>
            <button @click="vista='compras-ti'"><i class="blue">02</i><div><b>Autorizar compra técnica</b><p>Resolver el informe de viabilidad elevado por el Jefe de UTIC.</p></div><em>Soporte TI</em><strong>›</strong></button>
            <button @click="vista='mantenimiento'"><i class="green">03</i><div><b>Recibir reporte mensual</b><p>Tomar conocimiento del consolidado de mantenimientos finalizados.</p></div><em>Mantenimiento</em><strong>›</strong></button>
            <button @click="vista='informes'"><i class="navy">04</i><div><b>Recibir informe final</b><p>Registrar recepción del informe validado por el Jefe de UTIC.</p></div><em>Soporte TI</em><strong>›</strong></button>
          </div>
        </section>
      </section>

      <section v-else-if="vista==='delegar'">
        <DelegacionesPanel rol-codigo="DIRECTOR" rol-nombre="Director" />
      </section>

      <section v-else>
        <div class="notice"><b>{{ instruccion.titulo }}</b><span>{{ instruccion.texto }}</span></div>
        <div class="toolbar"><div><button class="active">{{ soloLectura?'Consulta':'Pendientes' }}</button></div><label>⌕ <input v-model="busqueda" placeholder="Buscar código o asunto"></label></div>
        <div v-if="cargando" class="empty">Actualizando bandeja…</div>
        <div v-else-if="filtrados.length" class="cards">
          <article v-for="item in filtrados" :key="item.id"><div class="top"><span>{{ codigo(item) }}</span><em>{{ estado(item) }}</em></div><h3>{{ asunto(item) }}</h3><p>{{ detalle(item) }}</p><dl><div><dt>Origen</dt><dd>{{ origen }}</dd></div><div><dt>Fecha</dt><dd>{{ fecha(item) }}</dd></div></dl><div class="actions"><button @click="verExpediente(item)">Ver expediente</button><button v-if="!soloLectura" class="primary" @click="ejecutar(item)">{{ instruccion.accion }}</button></div></article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin asuntos pendientes</h3><p>La bandeja de {{ titulo.toLowerCase() }} está al día.</p></div>
      </section>
    </main>
  </div>
</template>

<script setup>
import {computed,onMounted,ref} from 'vue'; import {useRouter} from 'vue-router'
import DelegacionesPanel from '../components/DelegacionesPanel.vue'
const router=useRouter(), usuario=ref(JSON.parse(localStorage.getItem('sigta_usuario')||'{}'))
const vista=ref('resumen'),menuAbierto=ref(false),compras=ref([]),soporte=ref([]),mantenimiento=ref([]),cargando=ref(false),busqueda=ref('')
const nombre=computed(()=>usuario.value.nombre||usuario.value.nombre_completo||'Director');const primerNombre=computed(()=>nombre.value.split(' ')[0]);const iniciales=computed(()=>nombre.value.split(' ').slice(0,2).map(x=>x[0]).join('').toUpperCase())
const saludo=computed(()=>new Date().getHours()<12?'Buenos días':new Date().getHours()<19?'Buenas tardes':'Buenas noches')
const textEstado=x=>String(x.estado_nombre||x.estado?.nombre||x.estado||'Pendiente')
// Un mismo expediente (SolicitudCompra) puede venir de una solicitud
// directa, de Mantenimiento o de Soporte (origen_modulo). "Caja" agrupa
// las dos primeras; "compras-ti" muestra solo las derivadas de Soporte.
const comprasPendientes=computed(()=>compras.value.filter(x=>x.estado==='VERIFICADO_PENDIENTE_AUTORIZACION'&&x.origen_modulo!=='SOPORTE'))
const soporteCompra=computed(()=>compras.value.filter(x=>x.estado==='VERIFICADO_PENDIENTE_AUTORIZACION'&&x.origen_modulo==='SOPORTE'))
const reportesMantenimiento=computed(()=>mantenimiento.value.filter(x=>x.estado_codigo==='FINALIZADO'))
const informesSoporte=computed(()=>soporte.value.filter(x=>x.estado_codigo==='CERRADO'&&!!x.informe_final))
const totalPendiente=computed(()=>comprasPendientes.value.length+soporteCompra.value.length)
const soloLectura=computed(()=>vista.value==='mantenimiento'||vista.value==='informes')
const menu=computed(()=>[{id:'resumen',icono:'⌂',nombre:'Resumen'},{id:'caja',icono:'VB',nombre:'Vistos buenos',total:comprasPendientes.value.length},{id:'compras-ti',icono:'AC',nombre:'Compras técnicas',total:soporteCompra.value.length},{id:'mantenimiento',icono:'RM',nombre:'Reportes mensuales',total:reportesMantenimiento.value.length},{id:'informes',icono:'IF',nombre:'Informes de soporte',total:informesSoporte.value.length},{id:'delegar',icono:'DL',nombre:'Delegar aprobación'}])
const titulo=computed(()=>({resumen:'Panel del Director',caja:'Visto bueno de Caja Chica','compras-ti':'Autorización de compra técnica',mantenimiento:'Reportes mensuales de mantenimiento',informes:'Informes finales de soporte'})[vista.value])
const instruccion=computed(()=>({caja:{titulo:'Decisión requerida',texto:'Confirme el visto bueno para devolver el expediente a Tesorería y habilitar el desembolso.',accion:'Dar visto bueno'},'compras-ti':{titulo:'Autorización técnica-financiera',texto:'Revise el expediente derivado desde un ticket de Soporte antes de continuar la gestión de compra.',accion:'Dar visto bueno'},mantenimiento:{titulo:'Recepción institucional (solo lectura)',texto:'Consolidado de mantenimientos finalizados. Servicios Generales ya archivó estos expedientes.',accion:''},informes:{titulo:'Cierre informativo (solo lectura)',texto:'Informes finales ya elaborados y validados por el Jefe de UTIC.',accion:''}})[vista.value]||{})
const lista=computed(()=>vista.value==='caja'?comprasPendientes.value:vista.value==='compras-ti'?soporteCompra.value:vista.value==='mantenimiento'?reportesMantenimiento.value:informesSoporte.value)
const filtrados=computed(()=>lista.value.filter(x=>JSON.stringify(x).toLowerCase().includes(busqueda.value.toLowerCase())))
const origen=computed(()=>(vista.value==='caja'||vista.value==='compras-ti')?'Tesorería':vista.value==='mantenimiento'?'Servicios Generales':'Jefe de UTIC')
const codigo=x=>x.codigo||x.numero_ticket||x.numero_solicitud||`#${x.id}`;const asunto=x=>x.asunto||x.titulo||x.descripcion_corta||'Expediente institucional';const detalle=x=>String(x.descripcion||x.justificacion||'Documento remitido para conocimiento y decisión de Dirección.').slice(0,135);const estado=x=>textEstado(x);const fecha=x=>{const v=x.created_at||x.fecha_solicitud||x.fecha_creacion||x.finalizado_en||x.cerrado_en;if(!v)return 'Sin fecha';return new Intl.DateTimeFormat('es-BO').format(new Date(v))}
async function obtener(url,destino){const r=await fetch(url,{headers:{Authorization:`Token ${localStorage.getItem('sigta_token')}`}});if(!r.ok)throw 0;const d=await r.json();destino.value=Array.isArray(d)?d:(d.results||[])}
async function cargarTodo(){cargando.value=true;await Promise.allSettled([obtener('/api/compras/solicitudes/',compras),obtener('/api/soporte/tickets/',soporte),obtener('/api/mantenimiento/requerimientos/',mantenimiento)]);cargando.value=false}
async function ejecutar(item){if(vista.value!=='caja'&&vista.value!=='compras-ti')return;if(!confirm(`¿Dar visto bueno a ${item.codigo} y devolverlo a Tesorería?`))return;try{const r=await fetch(`/api/compras/solicitudes/${item.id}/visto-bueno-director/`,{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Token ${localStorage.getItem('sigta_token')}`},body:'{}'});const d=await r.json();if(!r.ok)throw new Error(d.detalle||'No fue posible autorizar.');await cargarTodo();alert('Visto bueno registrado. El expediente fue enviado a Tesorería.')}catch(e){alert(e.message)}}
function verExpediente(item){const archivo=item.certificacion_presupuestaria||item.informe||item.poa||item.pedido||item.proforma;if(archivo)window.open(archivo,'_blank');else alert('No existe un documento disponible para abrir.')}
function salir(){localStorage.removeItem('sigta_token');localStorage.removeItem('sigta_usuario');router.push('/login')} onMounted(cargarTodo)
</script>

<style scoped>
*{box-sizing:border-box}.shell{min-height:100vh;background:#f5f7fa;color:#172f46;font-family:Inter,Segoe UI,sans-serif}aside{position:fixed;inset:0 auto 0 0;width:274px;background:#142f4b;color:white;padding:22px 16px;display:flex;flex-direction:column}.brand,.user{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 21px;border-bottom:1px solid #ffffff20}.brand>span{background:#ddb546;color:#162f49;padding:14px 10px;border-radius:8px;font-weight:900}.brand b,.brand small,.user strong,.user small{display:block}.brand b{font-size:23px}.brand small,.user small{color:#b7c9d9;margin-top:3px}.user{padding:22px 10px}.user>i{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:#ddb546;color:#17314a;font-style:normal;font-weight:900}aside>p{font-size:10px;letter-spacing:1.3px;color:#89a7c0;font-weight:800;margin:14px 11px 8px}aside button{border:0;background:transparent;color:#d8e5ef;border-radius:8px;padding:12px;display:flex;align-items:center;gap:11px;text-align:left;cursor:pointer;margin:2px 0}aside button em{font-style:normal;font-size:10px;font-weight:900;width:27px}aside button>b{margin-left:auto;background:#ffffff1c;padding:2px 8px;border-radius:10px}aside button:hover,aside button.active{background:#ffffff14;box-shadow:inset 3px 0 #ddb546}.logout{margin-top:auto;border-top:1px solid #ffffff1f;padding-top:10px}.logout button{width:100%}main{margin-left:274px;padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header>div>span{font-size:11px;color:#718497}h1{font-size:29px;margin:6px 0}header p{margin:0;color:#738496}.refresh{border:1px solid #d8e0e7;background:white;color:#254a69;padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,#173450,#245778);color:white;border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small{color:#e1bd55;font-size:10px;font-weight:800;letter-spacing:1.4px}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:#d3e0e9}.hero>span{width:67px;height:67px;border:1px solid #e1bd5588;border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:white;border:1px solid #e0e6eb;border-radius:10px;padding:19px;display:flex;gap:13px}.stats i,.flows i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:white;font-size:10px;font-weight:900}.gold{background:#c89b2e}.blue{background:#287bab}.green{background:#35966f}.navy{background:#234866}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:#8392a0;margin:0}.panel{background:white;border:1px solid #e0e6eb;border-radius:11px;padding:22px}.panel-head{display:flex;justify-content:space-between;align-items:center}.panel-head h3{margin:5px 0 14px}.panel-head>span{font-size:11px;background:#f3ead2;color:#80611e;padding:6px 10px;border-radius:12px}.flows{display:grid;grid-template-columns:1fr 1fr;gap:12px}.flows button{border:1px solid #e2e8ed;background:white;border-radius:9px;padding:16px;display:flex;align-items:center;gap:13px;text-align:left;cursor:pointer}.flows button div{flex:1}.flows button b,.flows button p{display:block}.flows button p{margin:4px 0 0;color:#768797;font-size:11px}.flows button em{font-style:normal;background:#eff3f6;padding:4px 8px;border-radius:10px;font-size:10px}.flows button>strong{font-size:20px}.notice{background:#fff9e8;border-left:4px solid #d5a836;padding:14px 17px;border-radius:7px;margin-bottom:17px}.notice b,.notice span{display:block}.notice span{font-size:12px;color:#756844;margin-top:4px}.toolbar{display:flex;justify-content:space-between;margin-bottom:17px}.toolbar>div{background:#e7edf1;padding:4px;border-radius:8px}.toolbar button{border:0;background:transparent;padding:9px 14px}.toolbar .active{background:white;border-radius:6px;box-shadow:0 2px 6px #1b344b20}.toolbar label{width:330px;background:white;border:1px solid #d7e0e7;border-radius:8px;padding:9px 12px}.toolbar input{border:0;outline:0;margin-left:7px;width:88%}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.cards article{background:white;border:1px solid #dfe6ec;border-radius:10px;padding:19px}.top{display:flex;justify-content:space-between}.top span{font-size:12px;font-weight:800;color:#246b96}.top em{font-size:10px;font-style:normal;background:#eef2f5;padding:4px 8px;border-radius:10px}.cards h3{font-size:17px;margin:15px 0 7px}.cards article>p{font-size:12px;color:#758697;min-height:42px}.cards dl{display:grid;grid-template-columns:1fr 1fr;border-block:1px solid #ebeff2;padding:12px 0}.cards dl div{display:block}.cards dt{font-size:9px;color:#8b99a6}.cards dd{font-size:11px;font-weight:700;margin:3px 0 0}.actions{display:flex;gap:8px;margin-top:14px}.actions button{flex:1;padding:9px;border-radius:7px;border:1px solid #cbd7df;background:white;color:#38576f;font-weight:700;cursor:pointer}.actions .primary{background:#183f5e;color:white;border-color:#183f5e}.empty{text-align:center;background:white;border:1px dashed #cad5dd;border-radius:11px;padding:70px;color:#768897}.empty>span{font-size:32px;color:#399970}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:720px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards,.flows{grid-template-columns:1fr}.toolbar,header{align-items:flex-start;flex-direction:column;gap:12px}.toolbar label{width:100%}}
</style>
