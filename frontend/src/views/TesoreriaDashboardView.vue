<template>
  <div class="layout sigta-role-layout">
    <aside>
      <div class="brand"><b>EMI</b><div><strong>SIGTA</strong><small>Caja Chica</small></div></div>
      <div class="person"><span>{{ iniciales }}</span><div><b>{{ nombre }}</b><small>Tesorería</small></div></div>
      <p>GESTIÓN FINANCIERA</p>
      <button v-for="item in menu" :key="item.id" :class="{active:vista===item.id}" @click="vista=item.id"><i>{{ item.icono }}</i>{{ item.nombre }}<em v-if="item.total !== undefined">{{ item.total }}</em></button>
      <div class="bottom"><button @click="cerrarSesion"><i>↪</i>Cerrar sesión</button></div>
    </aside>

    <main>
      <header><div><span>SIGTA / Tesorería / {{ tituloVista }}</span><h1>{{ tituloVista }}</h1><p>Control contable y custodia de fondos de Caja Chica.</p></div><button class="reload" @click="cargar">↻ Actualizar</button></header>

      <section v-if="vista==='resumen'">
        <div class="welcome"><div><small>CONTROL DE TESORERÍA</small><h2>Buenos días, {{ primerNombre }}</h2><p>Revise los expedientes, desembolsos y descargos pendientes del periodo.</p></div><div class="seal">Bs</div></div>
        <div class="stats">
          <article><span class="blue">▤</span><div><small>Por verificar</small><b>{{ porVerificar.length }}</b><p>expedientes recibidos</p></div></article>
          <article><span class="amber">$</span><div><small>Por desembolsar</small><b>{{ porDesembolsar.length }}</b><p>con visto bueno</p></div></article>
          <article><span class="green">✓</span><div><small>Por cerrar</small><b>{{ porCerrar.length }}</b><p>descargos pendientes</p></div></article>
          <article><span class="navy">Σ</span><div><small>Fondos registrados</small><b>{{ moneda(totalFondos) }}</b><p>en la bandeja actual</p></div></article>
        </div>
        <div class="grid"><section class="panel"><div class="panel-title"><div><small>FLUJO DE CAJA CHICA</small><h3>Acciones pendientes</h3></div></div>
          <button class="task" @click="vista='verificacion'"><span class="blue">1</span><div><b>Verificar integridad del expediente</b><small>POA, Pedido, Proforma y Certificación DAF</small></div><em>{{ porVerificar.length }}</em><strong>›</strong></button>
          <button class="task" @click="vista='desembolsos'"><span class="amber">2</span><div><b>Registrar desembolso</b><small>Monto entregado y responsable de adquisición</small></div><em>{{ porDesembolsar.length }}</em><strong>›</strong></button>
          <button class="task" @click="vista='descargos'"><span class="green">3</span><div><b>Verificar descargo y cerrar</b><small>Factura, conformidad, fotograma y cuadre</small></div><em>{{ porCerrar.length }}</em><strong>›</strong></button>
        </section><section class="panel rules"><div class="panel-title"><div><small>REGLAS DE CONTROL</small><h3>Responsabilidad</h3></div></div><p><b>Filtro preventivo</b><br>Solo los expedientes completos avanzan al Director.</p><p><b>Custodia de efectivo</b><br>Todo desembolso registra monto y responsable.</p><p><b>Cierre inmutable</b><br>El expediente se archiva después del cuadre documental.</p></section></div>
      </section>

      <section v-else>
        <div class="toolbar"><div class="tabs"><button class="active">Pendientes</button><button>Procesados</button></div><label>⌕ <input v-model="busqueda" placeholder="Buscar expediente o solicitante"></label></div>
        <div v-if="cargando" class="empty">Consultando expedientes…</div>
        <div v-else-if="filtrados.length" class="cards">
          <article v-for="exp in filtrados" :key="exp.id" class="card"><div class="card-top"><span>{{ codigo(exp) }}</span><em>{{ estado(exp) }}</em></div><h3>{{ titulo(exp) }}</h3><p>{{ detalle(exp) }}</p><div class="money"><small>Monto solicitado</small><b>{{ moneda(monto(exp)) }}</b></div>
            <div v-if="vista==='verificacion'" class="checklist"><label v-for="doc in documentos" :key="doc"><input type="checkbox"> {{ doc }}</label></div>
            <div class="card-foot"><button class="ghost" @click="verExpediente(exp)">Ver expediente</button><button class="primary" @click="ejecutar(exp)">{{ accion }}</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No existen expedientes pendientes en esta etapa.</p></div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
const router=useRouter(); const usuario=ref(JSON.parse(localStorage.getItem('sigta_usuario')||'{}'))
const vista=ref('resumen'), compras=ref([]), cargando=ref(false), busqueda=ref('')
const nombre=computed(()=>usuario.value.nombre||usuario.value.nombre_completo||'Responsable de Tesorería')
const primerNombre=computed(()=>nombre.value.split(' ')[0]); const iniciales=computed(()=>nombre.value.split(' ').slice(0,2).map(x=>x[0]).join('').toUpperCase())
const estadoTexto=x=>String(x?.estado_nombre||x?.estado?.nombre||x?.estado||'Pendiente')
const porVerificar=computed(()=>compras.value.filter(x=>x.estado==='CERTIFICADO_PENDIENTE_VERIFICACION'))
const porDesembolsar=computed(()=>compras.value.filter(x=>x.estado==='APROBADO_PARA_DESEMBOLSO'))
const porCerrar=computed(()=>compras.value.filter(x=>x.estado==='DESCARGO_PENDIENTE_LIQUIDACION'))
const totalFondos=computed(()=>compras.value.reduce((s,x)=>s+Number(x.monto||x.monto_total||x.presupuesto||0),0))
const menu=computed(()=>[{id:'resumen',icono:'⌂',nombre:'Resumen'},{id:'verificacion',icono:'✓',nombre:'Verificar expedientes',total:porVerificar.value.length},{id:'desembolsos',icono:'Bs',nombre:'Desembolsos',total:porDesembolsar.value.length},{id:'descargos',icono:'▣',nombre:'Descargos y cierre',total:porCerrar.value.length}])
const tituloVista=computed(()=>({resumen:'Panel de Tesorería',verificacion:'Verificación preventiva',desembolsos:'Registro de desembolsos',descargos:'Descargos y cierre'})[vista.value])
const lista=computed(()=>vista.value==='verificacion'?porVerificar.value:vista.value==='desembolsos'?porDesembolsar.value:porCerrar.value)
const filtrados=computed(()=>lista.value.filter(x=>JSON.stringify(x).toLowerCase().includes(busqueda.value.toLowerCase())))
const accion=computed(()=>vista.value==='verificacion'?'Habilitar para Director':vista.value==='desembolsos'?'Registrar desembolso':'Cerrar Caja Chica')
const documentos=['POA','Pedido institucional','Proforma','Certificación DAF']
const codigo=x=>x.codigo||x.numero_solicitud||`CP-${String(x.id).padStart(4,'0')}`
const titulo=x=>x.titulo||x.objeto||x.descripcion_corta||'Adquisición por Caja Chica'
const detalle=x=>String(x.descripcion||x.justificacion||'Expediente de adquisición institucional.').slice(0,120)
const estado=x=>estadoTexto(x); const monto=x=>x.monto||x.monto_total||x.presupuesto||0
const moneda=n=>new Intl.NumberFormat('es-BO',{style:'currency',currency:'BOB',maximumFractionDigits:2}).format(Number(n)||0)
async function cargar(){cargando.value=true;try{const r=await fetch('/api/compras/solicitudes/',{headers:{Authorization:`Token ${localStorage.getItem('sigta_token')}`}});if(!r.ok)throw 0;const d=await r.json();compras.value=Array.isArray(d)?d:(d.results||[])}catch{compras.value=[]}finally{cargando.value=false}}
async function postAccion(exp,endpoint,body={}){const r=await fetch(`/api/compras/solicitudes/${exp.id}/${endpoint}/`,{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Token ${localStorage.getItem('sigta_token')}`},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw new Error(d.detalle||'No fue posible completar la acción.');await cargar();return d}
async function ejecutar(exp){try{if(vista.value==='verificacion'){if(!confirm('¿Confirma que Informe, POA, Pedido, Proforma y Certificación están completos?'))return;await postAccion(exp,'verificar-tesoreria')}else if(vista.value==='desembolsos'){const monto=prompt('Monto efectivo desembolsado (Bs):',exp.monto_estimado||'');if(!monto)return;const responsable=prompt('Nombre del responsable que recibe el efectivo:','Encargado de Compras y Almacén');if(!responsable?.trim())return;await postAccion(exp,'desembolsar',{monto_desembolsado:monto,responsable_adquisicion:responsable.trim()})}else{if(!confirm('Esta acción cerrará y archivará el expediente de forma inmutable. ¿Continuar?'))return;await postAccion(exp,'cerrar-archivar')}alert('Acción registrada correctamente.')}catch(e){alert(e.message)}}
function verExpediente(exp){const archivo=exp.certificacion_presupuestaria||exp.informe||exp.factura||exp.acta_conformidad||exp.fotograma;if(archivo)window.open(archivo,'_blank');else alert('No existe un documento disponible para abrir.')}
function cerrarSesion(){localStorage.removeItem('sigta_token');localStorage.removeItem('sigta_usuario');router.push('/login')}
onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.layout{min-height:100vh;background:#f4f7fa;color:#193047;font-family:Inter,Segoe UI,sans-serif}aside{position:fixed;inset:0 auto 0 0;width:272px;background:#0d385e;color:white;padding:22px 16px;display:flex;flex-direction:column}.brand,.person{display:flex;align-items:center;gap:12px}.brand{padding:0 9px 20px;border-bottom:1px solid #ffffff22}.brand>b{background:#f6c719;color:#113c61;padding:14px 10px;border-radius:9px}.brand strong,.brand small,.person b,.person small{display:block}.brand strong{font-size:23px}.brand small,.person small{color:#b7cee0;margin-top:3px}.person{padding:22px 9px}.person>span{width:42px;height:42px;border-radius:50%;background:#f6c719;color:#153d5e;display:grid;place-items:center;font-weight:900}aside>p{color:#80a7c5;font-size:10px;font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{background:transparent;border:0;color:#d9e9f6;padding:12px;border-radius:8px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0}aside button i{font-style:normal;font-size:11px;font-weight:900;width:27px}aside button em{margin-left:auto;background:#ffffff20;padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:#ffffff18;box-shadow:inset 3px 0 #f6c719}.bottom{margin-top:auto;border-top:1px solid #ffffff20;padding-top:10px}.bottom button{width:100%}main{margin-left:272px;padding:30px 38px 60px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header span{font-size:11px;color:#73869a}h1{margin:6px 0;font-size:29px}header p{margin:0;color:#708295}.reload{background:white;border:1px solid #d5e0e8;padding:10px 14px;border-radius:8px;color:#1c4e76;cursor:pointer}.welcome{background:linear-gradient(120deg,#0f3b62,#1b6582);padding:27px 30px;border-radius:13px;color:white;display:flex;justify-content:space-between;align-items:center}.welcome small,.panel-title small{font-size:10px;font-weight:800;letter-spacing:1.5px;color:#f6c719}.welcome h2{font-size:24px;margin:7px 0}.welcome p{margin:0;color:#d4e5ed}.seal{height:65px;width:65px;border-radius:50%;border:2px solid #f6c719;display:grid;place-items:center;font-size:20px;font-weight:800}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:white;border:1px solid #e0e8ee;border-radius:10px;padding:19px;display:flex;gap:13px}.stats article>span,.task>span{width:36px;height:36px;border-radius:8px;display:grid;place-items:center;color:white;font-weight:800}.blue{background:#2582bd}.amber{background:#e3a42a}.green{background:#25a477}.navy{background:#164767}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:#8494a4;margin:0}.grid{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:white;border:1px solid #e0e8ee;border-radius:11px;padding:22px}.panel-title h3{margin:5px 0 15px}.task{width:100%;border:0;border-top:1px solid #ebf0f4;background:white;padding:15px 3px;display:flex;align-items:center;gap:13px;text-align:left;cursor:pointer}.task div b,.task div small{display:block}.task div small{color:#8291a0;margin-top:4px}.task em{margin-left:auto;background:#edf3f6;border-radius:12px;padding:4px 9px;font-style:normal}.task>strong{font-size:22px;color:#668097}.rules p{padding:12px 0;margin:0;border-top:1px solid #ebf0f4;color:#748595;font-size:12px;line-height:1.6}.rules b{color:#29465f}.toolbar{display:flex;justify-content:space-between;margin-bottom:17px}.tabs{background:#e7edf2;padding:4px;border-radius:8px}.tabs button{border:0;background:transparent;padding:9px 14px;border-radius:6px}.tabs .active{background:white;box-shadow:0 2px 6px #19304720}.toolbar label{background:white;border:1px solid #d8e2e9;border-radius:8px;padding:9px 12px;width:330px}.toolbar input{border:0;outline:0;margin-left:7px;width:88%}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{background:white;border:1px solid #dde6ed;border-radius:11px;padding:19px}.card-top{display:flex;justify-content:space-between}.card-top span{color:#176a9b;font-weight:800;font-size:12px}.card-top em{font-size:10px;background:#edf3f6;padding:4px 8px;border-radius:10px;font-style:normal}.card h3{font-size:17px;margin:15px 0 7px}.card>p{color:#738598;font-size:12px;min-height:42px}.money{background:#f4f7f9;padding:10px;border-radius:7px;margin:13px 0}.money small,.money b{display:block}.money small{color:#7b8d9e;font-size:10px}.money b{font-size:18px;margin-top:3px}.checklist{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0;font-size:11px;color:#526a7f}.card-foot{display:flex;gap:8px;border-top:1px solid #e9eef2;padding-top:14px}.card-foot button{flex:1;padding:9px 6px;border-radius:7px;font-weight:700;cursor:pointer}.ghost{background:white;border:1px solid #cbd8e1;color:#3b5b74}.primary{background:#12547c;border:1px solid #12547c;color:white}.empty{text-align:center;background:white;border:1px dashed #cbd8df;border-radius:11px;padding:70px;color:#748797}.empty>span{font-size:32px;color:#25a477}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:720px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}.toolbar,header{align-items:flex-start;flex-direction:column;gap:12px}.toolbar label{width:100%}}
</style>
