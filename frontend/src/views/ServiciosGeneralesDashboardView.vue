<template>
  <div class="layout sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><b><img src="/img/emi.jpg" alt="EMI"></b><div><strong>SIGTA</strong><small>Mantenimiento</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="profile"><i>{{ iniciales }}</i><div><b>{{ nombre }}</b><small>Jefe de Mantenimiento</small></div></div>
      <p>GESTIÓN DE MANTENIMIENTO</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="irA(m.id)"><span>{{ m.icono }}</span>{{ m.nombre }}<em v-if="m.total!==undefined">{{ m.total }}</em></button>
      <div class="bottom"><button @click="salir"><span>↪</span>Cerrar sesión</button></div>
    </aside>

    <main>
      <header>
        <div><small>SIGTA / MANTENIMIENTO / {{ titulo }}</small><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <button class="refresh" :disabled="cargando" @click="cargar">↻ Actualizar</button>
      </header>

      <!-- ============================ RESUMEN ============================ -->
      <section v-if="vista==='resumen'">
        <div class="hero">
          <div><small>JEFATURA DE MANTENIMIENTO</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Requerimientos que requieren su gestión hoy.</p></div>
          <span>MT</span>
        </div>
        <div class="stats">
          <article @click="irA('gestion')"><i class="blue">GT</i><div><small>Gestión</small><b>{{ ticketsGestion.length }}</b><p>tickets pendientes</p></div></article>
          <article @click="irA('compra')"><i class="navy">CO</i><div><small>Compras</small><b>{{ porEvaluarCompra.length }}</b><p>por evaluar</p></div></article>
          <article @click="irA('verificar')"><i class="green">VF</i><div><small>Por verificar</small><b>{{ porVerificar.length }}</b><p>funcionamiento</p></div></article>
          <article @click="irA('informe')"><i class="gold">IF</i><div><small>Por informar</small><b>{{ porConformar.length + porInformar.length }}</b><p>conformidad</p></div></article>
        </div>
        <div class="panels">
          <section class="panel">
            <div class="panel-head"><div><h3>Proceso de mantenimiento</h3></div></div>
            <button class="flow" @click="irA('gestion')"><i class="blue">1</i><div><b>Gestión integral de tickets</b><small>Validar, clasificar prioridad y designar técnico</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('compra')"><i class="gold">2</i><div><b>Recibir requerimiento y cotización</b><small>Evaluar la viabilidad de la compra</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('verificar')"><i class="green">3</i><div><b>Verificar funcionamiento</b><small>Confirmar si el problema quedó resuelto</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('informe')"><i class="gold">4</i><div><b>Conformidad e informe final</b><small>Cerrar el caso y elevarlo a la Dirección</small></div><strong>›</strong></button>
          </section>
          <section class="panel">
            <div class="panel-head"><div><small>SEGUIMIENTO</small><h3>Reporte mensual</h3></div></div>
            <p class="copy">Consolidado de los mantenimientos finalizados en el periodo.</p>
            <button class="wide primary" @click="irA('reporte')">Ver reporte mensual →</button>
          </section>
        </div>
      </section>

      <!-- ========================= GESTIÓN DE TICKETS ========================= -->
      <section v-else-if="vista==='gestion'" class="gestion-tickets-layout">
        <div class="gestion-left">
          <div class="gestion-left-header">
            <h3>Tickets Pendientes</h3>
            <span class="badge">{{ ticketsGestion.length }} Requiere Acción</span>
          </div>
          <div class="gestion-lista">
            <article v-for="r in ticketsGestion" :key="r.id" :class="['ticket-item', itemActivo?.id === r.id ? 'activo' : '', r.estado_codigo === 'RECIBIDO' ? 't-validar' : (!r.prioridad_jefatura ? 't-clasificar' : 't-designar')]" @click="abrir(r)">
              <div class="top">
                <span>{{ r.codigo }}</span>
                <em v-if="r.estado_codigo === 'RECIBIDO'" class="e-validar">Paso 1: Por Validar</em>
                <em v-else-if="!r.prioridad_jefatura" class="e-clasificar">Paso 2: Por Priorizar</em>
                <em v-else class="e-designar">Paso 3: Por Designar</em>
              </div>
              <h4>{{ r.titulo }}</h4>
              <p>📍 {{ r.ubicacion || 's/d' }} • 🧑 {{ r.solicitante_nombre || 's/d' }}</p>
            </article>
            <div v-if="!ticketsGestion.length" class="empty-list">Bandeja al día. No hay tickets pendientes.</div>
          </div>
        </div>

        <div class="gestion-right">
          <div v-if="!itemActivo" class="empty">
            <span>←</span>
            <h3>Seleccione un ticket</h3>
            <p>Seleccione un ticket de la lista para gestionar su flujo operativo.</p>
          </div>
          <div v-else class="gestion-detalle-wrapper">
              
              <!-- Encabezado del Ticket -->
              <div class="ticket-header-card">
                <div class="t-head">
                  <h2>{{ itemActivo.titulo }}</h2>
                  <span class="codigo-badge">{{ itemActivo.codigo }}</span>
                </div>
                <p class="t-meta">
                  <span>👤 <b>Solicitante:</b> {{ itemActivo.solicitante_nombre }}</span>
                  <span>📍 <b>Ubicación:</b> {{ itemActivo.ubicacion }}</span>
                </p>
                
                <div class="t-content">
                  <div class="desc-box">
                    <strong>Descripción del problema</strong>
                    <p>{{ itemActivo.descripcion }}</p>
                  </div>
                  
                  <div class="evidence-box" v-if="itemActivo.evidencia_archivo_url">
                    <div class="evidence-info">
                      <strong>Evidencia fotográfica</strong>
                      <span>Archivo adjunto por el solicitante</span>
                    </div>
                    <a class="evidence-btn" :href="itemActivo.evidencia_archivo_url" target="_blank">
                      Ver Evidencia ↗
                    </a>
                  </div>
                </div>
              </div>

            <!-- Flujo Operativo -->
            <div class="workflow-card">
              <div class="wf-header">Consola de Gestión (Flujo)</div>
              <div class="wf-body">
                
                <!-- PASO 1: VALIDACIÓN -->
                <div :class="['wf-step', itemActivo.estado_codigo !== 'RECIBIDO' ? 'completed' : 'active']">
                  <div class="step-num">1</div>
                  <div class="step-content">
                    <h4>Validación del Ticket <span v-if="itemActivo.estado_codigo !== 'RECIBIDO'" class="step-badge">✓ Completado</span></h4>
                    <p v-if="itemActivo.estado_codigo === 'RECIBIDO'">Revisa la descripción y aprueba o rechaza esta solicitud.</p>
                    <div v-if="itemActivo.estado_codigo === 'RECIBIDO'" class="step-actions">
                      <button class="primary flex-btn" :disabled="procesando" @click="validar(itemActivo)">Aprobar</button>
                      <button class="reject" :disabled="procesando" @click="rechazar(itemActivo)">Rechazar</button>
                    </div>
                  </div>
                </div>

                <!-- PASO 2: CLASIFICAR PRIORIDAD -->
                <div :class="['wf-step', itemActivo.estado_codigo === 'RECIBIDO' ? 'locked' : (itemActivo.prioridad_jefatura ? 'completed' : 'active')]">
                  <div class="step-num">2</div>
                  <div class="step-content">
                    <h4>Clasificar Prioridad <span v-if="itemActivo.prioridad_jefatura" class="step-badge">✓ {{ itemActivo.prioridad_jefatura }}</span></h4>
                    <p v-if="!itemActivo.prioridad_jefatura">Determina la urgencia y justifícala.</p>
                    <div v-if="itemActivo.estado_codigo !== 'RECIBIDO' && !itemActivo.prioridad_jefatura">
                      <div class="p-options">
                        <label><input type="radio" v-model="formClasificar.prioridad" value="BAJA"> Baja</label>
                        <label><input type="radio" v-model="formClasificar.prioridad" value="MEDIA"> Media</label>
                        <label><input type="radio" v-model="formClasificar.prioridad" value="ALTA"> Alta</label>
                        <label><input type="radio" v-model="formClasificar.prioridad" value="URGENTE"> Urgente</label>
                      </div>
                      <textarea v-model="formClasificar.criterio_prioridad" placeholder="Justifique la prioridad asignada..." rows="2"></textarea>
                      <button class="primary step-btn" :disabled="procesando || !formClasificar.prioridad || !formClasificar.criterio_prioridad.trim()" @click="clasificar">Guardar prioridad</button>
                    </div>
                  </div>
                </div>

                <!-- PASO 3: DESIGNAR TÉCNICO -->
                <div :class="['wf-step', !itemActivo.prioridad_jefatura ? 'locked' : 'active']">
                  <div class="step-num">3</div>
                  <div class="step-content">
                    <h4>Designar Técnico</h4>
                    <p v-if="!itemActivo.tecnico_id">Asigna a la persona responsable de la reparación.</p>
                    <div v-if="itemActivo.prioridad_jefatura">
                      <select v-model="formDesignar.tecnico_id" class="full-select">
                        <option value="">Seleccione un técnico...</option>
                        <option v-for="t in tecnicos" :key="t.id" :value="t.id">{{ t.nombre_completo || t.email }}</option>
                      </select>
                      <small v-if="!tecnicos.length" style="display:block;margin-top:5px;color:red;">No hay técnicos activos disponibles.</small>
                      <button class="primary step-btn" :disabled="procesando || !formDesignar.tecnico_id" @click="designar">Confirmar Asignación</button>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===================== 4. VIABILIDAD COMPRA (NUEVO MAESTRO-DETALLE) ===================== -->
      <div v-else-if="vista==='compra'" class="gestion-tickets-layout">
        
        <!-- Panel Izquierdo: Lista -->
        <div class="gestion-left">
          <div class="gestion-left-header">
            <h3>Compras Pendientes</h3>
            <span class="badge">{{ porEvaluarCompra.length }} por evaluar</span>
          </div>
          <div class="gestion-lista">
            <article v-for="r in porEvaluarCompra" :key="r.id" :class="['ticket-item', itemActivo?.id === r.id ? 'activo' : '', 't-validar']" @click="abrir(r)">
              <div class="top"><span>{{ r.codigo }}</span><em class="e-validar">Por Evaluar</em></div>
              <h4>{{ r.titulo }}</h4>
              <p>📍 {{ r.ubicacion || 's/d' }} • 📦 {{ r.producto_requerido || 's/d' }}</p>
            </article>
            <div v-if="!porEvaluarCompra.length" class="empty-list">Bandeja al día. No hay requerimientos por evaluar.</div>
          </div>
        </div>

        <!-- Panel Derecho: Flujo y Expediente -->
        <div class="gestion-right">
          <div v-if="!itemActivo" class="empty">
            <span style="font-size:30px">📦</span>
            <h3>Seleccione un requerimiento</h3>
            <p>Seleccione un requerimiento de compra de la lista para gestionar su expediente y enviarlo a la DAF.</p>
          </div>
          <div v-else class="gestion-detalle-wrapper">
            
            <!-- Encabezado del Requerimiento -->
            <div class="ticket-header-card">
              <div class="t-head">
                <h2>{{ itemActivo.titulo }}</h2>
                <span class="codigo-badge">{{ itemActivo.codigo }}</span>
              </div>
              <p class="t-meta">
                <span>👤 <b>Técnico asignado:</b> {{ itemActivo.tecnico_asignado_nombre || 's/d' }}</span>
              </p>
              
              <div class="t-content">
                <div class="desc-box">
                  <strong>Detalles del componente solicitado</strong>
                  <p><b>Componente:</b> {{ itemActivo.producto_requerido }}</p>
                  <p v-if="itemActivo.especificacion_producto"><b>Especificación:</b> {{ itemActivo.especificacion_producto }}</p>
                  <p><b>Cantidad requerida:</b> {{ itemActivo.cantidad_requerida || 1 }}</p>
                  <p><b>Costo estimado:</b> Bs. {{ itemActivo.costo_estimado || 's/d' }}</p>
                </div>
                
                <div class="evidence-box" v-if="itemActivo.cotizacion_archivo_url || itemActivo.cotizacion_archivo">
                  <div class="evidence-info">
                    <strong>Cotización de referencia</strong>
                    <span>Archivo adjunto por el técnico</span>
                  </div>
                  <a class="evidence-btn" :href="itemActivo.cotizacion_archivo_url || itemActivo.cotizacion_archivo" target="_blank">
                    Ver Cotización ↗
                  </a>
                </div>
              </div>
            </div>

            <!-- Flujo Operativo -->
            <div class="workflow-card">
              <div class="wf-header">Armado de Expediente para la DAF</div>
              <div class="wf-body">
                
                <div v-if="!formCompra.viable" class="wf-step active">
                  <div class="step-num">!</div>
                  <div class="step-content" style="border-color: var(--sigta-error)">
                    <h4 style="color: var(--sigta-error)">Rechazar Compra</h4>
                    <p>Indique el motivo por el cual la compra no procede. El ticket se cerrará sin compra.</p>
                    <textarea v-model="formCompra.motivo_no_viable" placeholder="Ej: No hay presupuesto, repuesto equivocado..." rows="3" style="width: 100%; padding: 10px; margin-bottom:10px; border: 1px solid var(--sigta-borde); border-radius: 6px; font-family: inherit"></textarea>
                    <div class="step-actions" style="display:flex; gap: 8px">
                      <button class="primary step-btn" style="background: var(--sigta-error); border-color: var(--sigta-error)" :disabled="procesando || !formCompra.motivo_no_viable.trim()" @click="evaluarCompraUpload">Confirmar Rechazo</button>
                      <button class="step-btn" style="background: #f1f5f9; color: var(--sigta-texto)" :disabled="procesando" @click="formCompra.viable = true">Retroceder</button>
                    </div>
                  </div>
                </div>

                <template v-else>
                  <!-- PASO 1: INFORME -->
                  <div :class="['wf-step', formCompra.informe ? 'completed' : 'active']">
                    <div class="step-num">1</div>
                    <div class="step-content">
                      <h4>Subir Informe <span v-if="formCompra.informe" class="step-badge">✓ Cargado</span></h4>
                      <p>Adjunte el documento del informe justificativo (PDF o Word).</p>
                      <div class="step-actions" style="margin-top: 10px;">
                        <input type="file" accept=".pdf,.doc,.docx" @change="e => formCompra.informe = e.target.files[0]">
                      </div>
                    </div>
                  </div>

                  <!-- PASO 2: PROFORMA -->
                  <div :class="['wf-step', !formCompra.informe ? 'locked' : (formCompra.proforma ? 'completed' : 'active')]">
                    <div class="step-num">2</div>
                    <div class="step-content">
                      <h4>Subir Proforma <span v-if="formCompra.proforma" class="step-badge">✓ Cargada</span></h4>
                      <p>Adjunte la imagen de la cotización o proforma (.png, .jpg).</p>
                      <div v-if="formCompra.informe" class="step-actions" style="margin-top: 10px;">
                        <input type="file" accept=".png,.jpg,.jpeg" @change="e => formCompra.proforma = e.target.files[0]">
                      </div>
                    </div>
                  </div>

                  <!-- PASO 3: POA -->
                  <div :class="['wf-step', !formCompra.proforma ? 'locked' : (formCompra.poa ? 'completed' : 'active')]">
                    <div class="step-num">3</div>
                    <div class="step-content">
                      <h4>Subir POA <span v-if="formCompra.poa" class="step-badge">✓ Cargado</span></h4>
                      <p>Adjunte el documento del POA (PDF o Word).</p>
                      <div v-if="formCompra.proforma" class="step-actions" style="margin-top: 10px;">
                        <input type="file" accept=".pdf,.doc,.docx" @change="e => formCompra.poa = e.target.files[0]">
                      </div>
                    </div>
                  </div>

                  <!-- PASO 4: ENVIAR A DAF -->
                  <div :class="['wf-step', !formCompra.poa ? 'locked' : 'active']">
                    <div class="step-num">4</div>
                    <div class="step-content">
                      <h4>Confirmar y Enviar a DAF</h4>
                      <p>El expediente está completo. Elija una opción para finalizar.</p>
                      <div v-if="formCompra.poa" class="step-actions" style="margin-top: 10px; display:flex; gap: 8px">
                        <button class="primary step-btn" style="background: #15803d; border-color: #15803d" :disabled="procesando" @click="evaluarCompraUpload">Aprobar y Enviar a DAF</button>
                      </div>
                      <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed var(--sigta-borde-suave)">
                        <button class="step-btn" style="color: var(--sigta-error); background: transparent; padding: 0" :disabled="procesando" @click="formCompra.viable = false">Rechazar compra en su lugar</button>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

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
const ticketsGestion = computed(() => [...porValidar.value, ...porClasificar.value, ...porDesignar.value])

const porEvaluarCompra = computed(() => items.value.filter(r => r.estado_compra_componente === 'SOLICITADA'))
const porVerificar = computed(() => items.value.filter(r => r.estado_codigo === 'INFORME_REGISTRADO' && !r.verificado_en))
const porConformar = computed(() => items.value.filter(r => r.estado_codigo === 'INFORME_REGISTRADO' && !!r.verificado_en))
const porInformar = computed(() => items.value.filter(r => r.estado_codigo === 'CONFORMIDAD_INFORMADA'))

const menu = computed(() => [
  { id: 'resumen', icono: '⌂', nombre: 'Dashboard' },
  { id: 'gestion', icono: 'GT', nombre: 'Gestión de tickets', total: ticketsGestion.value.length },
  { id: 'compra', icono: 'CO', nombre: 'Solicitar compra', total: porEvaluarCompra.value.length },
  { id: 'verificar', icono: 'VF', nombre: 'Verificar funcionamiento', total: porVerificar.value.length },
  { id: 'informe', icono: 'IF', nombre: 'Conformidad e informe', total: porConformar.value.length + porInformar.value.length },
  { id: 'reporte', icono: 'RM', nombre: 'Reporte mensual' },
])

const titulo = computed(() => ({
  resumen: 'Dashboard del Jefe de Mantenimiento',
  gestion: 'Gestión de Tickets',
  compra: 'Recibir requerimiento y cotización',
  verificar: 'Verificar funcionamiento',
  informe: 'Conformidad e informe final',
  reporte: 'Reporte mensual',
}[vista.value]))

const subtitulo = computed(() => ({
  resumen: 'Validación, clasificación y seguimiento de los requerimientos de mantenimiento.',
  gestion: 'Validación, priorización y asignación de tickets en un solo flujo.',
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
    const r = await fetch(`${base}/${item.id}/${endpoint}/`, {
      method: 'POST',
      headers: { Authorization: `Token ${token()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible completar la acción.')
    await cargar()
    
    if (vista.value === 'gestion' && itemActivo.value) {
      const found = items.value.find(i => i.id === itemActivo.value.id);
      if (found && (found.estado_codigo === 'RECIBIDO' || found.estado_codigo === 'VALIDADO')) {
        itemActivo.value = found;
      } else {
        itemActivo.value = null;
      }
    } else {
      itemActivo.value = null;
    }
    
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
  formCompra.informe = null
  formCompra.proforma = null
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
  const motivo = await window.sigtaPrompt('Indique el motivo del rechazo:')
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

const formCompra = reactive({ viable: true, motivo_no_viable: '', informe: null, proforma: null, poa: null })

async function evaluarCompraUpload() {
  procesando.value = true
  try {
    if (formCompra.viable && (!formCompra.informe || !formCompra.poa || !formCompra.proforma)) {
      throw new Error("Debe subir todos los documentos requeridos para aprobar.")
    }

    const fd = new FormData()
    fd.append("viable", formCompra.viable ? "true" : "false")
    if (!formCompra.viable) fd.append("motivo_no_viable", formCompra.motivo_no_viable.trim())
    
    if (formCompra.viable) {
      fd.append("informe", formCompra.informe)
      fd.append("proforma", formCompra.proforma)
      fd.append("poa", formCompra.poa)
    }

    const r = await fetch(`${base}/${itemActivo.value.id}/evaluar-viabilidad-compra/`, {
      method: 'POST',
      headers: { Authorization: `Token ${token()}` },
      body: fd,
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible completar la acción.')
    alert(d?.mensaje || 'Evaluación de compra registrada.')
    
    await cargar()
    itemActivo.value = null
  } catch (e) { alert(e.message) }
  finally { procesando.value = false }
}

async function evaluarCompra() {
  try {
    const d = await postAccion(itemActivo.value, 'evaluar-viabilidad-compra', {
      viable: formCompra.viable,
      motivo_no_viable: formCompra.motivo_no_viable.trim(),
    })
    alert(d?.mensaje || 'Evaluación registrada.')
  } catch (e) { alert(e.message) }
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
*{box-sizing:border-box}.layout{min-height:100vh;background:var(--sigta-fondo);color:var(--sigta-texto);font-family:var(--sigta-fuente)}aside{position:fixed;inset:0 auto 0 0;width:var(--sigta-sidebar);background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand,.profile{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 20px;border-bottom:1px solid rgba(255,255,255,.2)}.brand>b{background:var(--sigta-mostaza);color:var(--sigta-azul);padding:14px 10px;border-radius:9px}.brand strong,.brand small,.profile b,.profile small{display:block}.brand strong{font-size:23px}.brand small,.profile small{color:var(--sigta-azul-texto-claro);margin-top:3px}.profile{padding:22px 10px}.profile>i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}aside>p{font-size:10px;color:var(--sigta-azul-texto-claro);font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{border:0;background:transparent;color:var(--sigta-blanco);border-radius:8px;padding:12px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0;width:100%}aside button>span{font-size:10px;font-weight:900;width:28px}aside button em{margin-left:auto;background:rgba(255,255,255,.16);padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:rgba(255,255,255,.13)}.bottom{margin-top:auto;border-top:1px solid rgba(255,255,255,.2);padding-top:10px}.bottom button{width:100%}main{margin-left:var(--sigta-sidebar);padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header small{color:var(--sigta-texto-suave)}h1{font-size:var(--sigta-titulo);margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.refresh{border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-azul);padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-azul-medio));color:var(--sigta-blanco);border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small{font-size:10px;font-weight:800;letter-spacing:1.4px;color:var(--sigta-mostaza-clara)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero>span{width:68px;height:68px;border:1px solid var(--sigta-mostaza);border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px;display:flex;gap:13px;cursor:pointer}.stats i,.flow i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:var(--sigta-blanco);font-size:10px;font-weight:900}.blue{background:var(--sigta-azul)}.gold{background:var(--sigta-mostaza);color:var(--sigta-texto)!important}.green{background:var(--sigta-azul-medio)}.navy{background:var(--sigta-azul-medio)}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.panels{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}.panel-head h3{margin:5px 0 14px}.flow{width:100%;border:0;border-top:1px solid var(--sigta-borde-suave);background:var(--sigta-blanco);padding:15px 2px;display:flex;gap:13px;align-items:center;text-align:left;cursor:pointer}.flow div{flex:1}.flow b,.flow small{display:block}.flow small{color:var(--sigta-texto-suave);margin-top:4px}.flow>strong{font-size:20px}.copy{color:var(--sigta-texto-suave);font-size:12px;line-height:1.7}.wide{width:100%;padding:10px;border-radius:7px;border:1px solid var(--sigta-borde);cursor:pointer}.primary{background:var(--sigta-azul)!important;color:var(--sigta-blanco)!important;border-color:var(--sigta-azul)!important}.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;margin-bottom:17px;border-radius:7px}.instruction b,.instruction span{display:block}.instruction span{font-size:12px;color:var(--sigta-alerta);margin-top:4px}.mini-alerta{background:var(--sigta-error-fondo);color:var(--sigta-error);font-size:11px;font-weight:700;padding:7px 9px;border-radius:6px;margin-bottom:10px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:16px}.cards article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px}.cards article.retorno{border-color:var(--sigta-error);box-shadow:inset 3px 0 var(--sigta-error)}.top{display:flex;justify-content:space-between;gap:8px}.top span{font-size:12px;font-weight:800;color:var(--sigta-azul)}.top em{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px;font-style:normal}.cards h3{font-size:17px;margin:15px 0 7px}.cards article>p{font-size:12px;color:var(--sigta-texto-suave);min-height:42px}.datos{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:4px}.datos li{display:flex;justify-content:space-between;gap:10px;font-size:11px;border-bottom:1px dashed var(--sigta-borde-suave);padding-bottom:3px}.datos b{color:var(--sigta-texto-suave)}.datos span{color:var(--sigta-texto-suave);text-align:right}.adjunto{display:inline-block;font-size:11px;color:var(--sigta-azul);margin-bottom:10px;text-decoration:none}.actions{display:flex;gap:7px;border-top:1px solid var(--sigta-borde-suave);padding-top:13px;margin-top:10px;align-items:flex-end}.actions button{flex:1;padding:9px 6px;border-radius:7px;border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-texto);font-weight:700;cursor:pointer}.actions button:disabled{opacity:.55;cursor:not-allowed}.reject{color:var(--sigta-error)!important;border-color:var(--sigta-error)!important}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-borde);padding:65px;border-radius:10px;color:var(--sigta-texto-suave)}.empty>span{font-size:31px;color:var(--sigta-exito)}.campo{display:block;margin:14px 0;font-size:12px;font-weight:700;color:var(--sigta-texto)}.campo input,.campo select,.campo textarea{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-borde);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}.reporte-item{padding:9px 0;border-top:1px solid var(--sigta-borde-suave);font-size:13px}.detalle-modal-backdrop{position:fixed;inset:0;background:rgba(18,58,107,.55);display:grid;place-items:center;padding:20px;z-index:20}.detalle-modal{background:var(--sigta-blanco);border-radius:14px;width:min(700px,100%);max-height:88vh;display:flex;flex-direction:column}.detalle-modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--sigta-borde-suave)}.detalle-modal-header h3{margin:0}.detalle-modal-header small{color:var(--sigta-texto-suave)}.detalle-modal-close{border:0;background:transparent;font-size:20px;cursor:pointer;color:var(--sigta-texto-suave)}.detalle-modal-body{padding:20px 24px;overflow-y:auto;display:grid;gap:14px}.detalle-fila{display:grid;grid-template-columns:1fr 1fr;gap:14px}.detalle-campo b{display:block;font-size:11px;color:var(--sigta-texto-suave);margin-bottom:4px}.detalle-campo span,.detalle-campo p{font-size:13px;color:var(--sigta-texto);margin:0}

/* ====== NUEVOS ESTILOS: GESTIÓN DE TICKETS ====== */
.gestion-tickets-layout { display: flex; gap: 20px; height: calc(100vh - 160px); overflow: hidden; align-items: stretch; }
.gestion-left { width: 35%; display: flex; flex-direction: column; background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; overflow: hidden; }
.gestion-left-header { padding: 15px 20px; border-bottom: 1px solid var(--sigta-borde-suave); display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.gestion-left-header h3 { margin: 0; font-size: 14px; color: var(--sigta-texto); }
.badge { background: #e0e7ff; color: var(--sigta-azul); font-size: 11px; padding: 4px 8px; border-radius: 20px; font-weight: bold; }
.gestion-lista { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.ticket-item { padding: 14px; border: 1px solid var(--sigta-borde-suave); border-radius: 8px; cursor: pointer; transition: all 0.2s; background: var(--sigta-blanco); }
.ticket-item:hover { border-color: var(--sigta-borde); box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.ticket-item.activo { border-color: var(--sigta-azul); background: #f8fafc; }
.ticket-item.t-validar { border-left: 4px solid var(--sigta-error); }
.ticket-item.t-clasificar { border-left: 4px solid var(--sigta-mostaza); }
.ticket-item.t-designar { border-left: 4px solid var(--sigta-azul); }
.ticket-item h4 { margin: 8px 0 4px; font-size: 14px; color: var(--sigta-texto); }
.ticket-item p { margin: 0; font-size: 11px; color: var(--sigta-texto-suave); }
.e-validar { background: #fee2e2; color: #b91c1c; }
.e-clasificar { background: #fef3c7; color: #b45309; }
.e-designar { background: #e0e7ff; color: #4338ca; }
.empty-list { text-align: center; padding: 30px; font-size: 12px; color: var(--sigta-texto-suave); }

.gestion-right { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.gestion-detalle-wrapper { display: flex; flex-direction: column; gap: 15px; height: 100%; }
.ticket-header-card { background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; padding: 24px; flex-shrink: 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.t-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.t-head h2 { margin: 0; font-size: 20px; color: var(--sigta-azul); font-weight: 800; }
.codigo-badge { font-weight: bold; color: var(--sigta-texto-suave); font-size: 13px; background: #f1f5f9; padding: 4px 10px; border-radius: 6px; }
.t-meta { display: flex; gap: 16px; margin: 0 0 20px; font-size: 13px; color: var(--sigta-texto-suave); }
.t-meta span { display: flex; align-items: center; gap: 5px; }
.t-meta b { color: var(--sigta-texto); }

.t-content { display: flex; flex-direction: column; gap: 12px; }
.desc-box { background: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid var(--sigta-borde-suave); }
.desc-box strong { display: block; font-size: 11px; color: var(--sigta-texto-suave); text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; font-weight: bold; }
.desc-box p { margin: 0; font-size: 14px; line-height: 1.5; color: var(--sigta-texto); }

.evidence-box { display: flex; justify-content: space-between; align-items: center; background: #e0e7ff; border: 1px solid #c7d2fe; padding: 12px 16px; border-radius: 8px; }
.evidence-info strong { display: block; font-size: 13px; color: var(--sigta-azul); font-weight: bold; margin-bottom: 2px; }
.evidence-info span { font-size: 11px; color: #4338ca; }
.evidence-btn { background: var(--sigta-azul); color: var(--sigta-blanco); text-decoration: none; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 6px; transition: opacity 0.2s; white-space: nowrap; }
.evidence-btn:hover { opacity: 0.9; }

.workflow-card { flex: 1; background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; }
.wf-header { padding: 15px 20px; border-bottom: 1px solid var(--sigta-borde-suave); font-weight: bold; color: var(--sigta-texto); background: #f8fafc; }
.wf-body { flex: 1; overflow-y: auto; padding: 25px; display: flex; flex-direction: column; position: relative; }
.wf-body::before { content: ''; position: absolute; left: 45px; top: 35px; bottom: 35px; width: 2px; background: var(--sigta-borde-suave); z-index: 1; }

.wf-step { display: flex; margin-bottom: 30px; position: relative; z-index: 2; }
.wf-step:last-child { margin-bottom: 0; }
.step-num { width: 42px; height: 42px; border-radius: 50%; background: var(--sigta-borde); color: var(--sigta-texto-suave); display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; border: 4px solid var(--sigta-blanco); transition: all 0.3s; }
.step-content { margin-left: 20px; flex: 1; background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 10px; padding: 15px 20px; transition: all 0.3s; }
.step-content h4 { margin: 0 0 5px; font-size: 15px; display: flex; justify-content: space-between; align-items: center; }
.step-content p { margin: 0 0 15px; font-size: 12px; color: var(--sigta-texto-suave); }
.step-badge { font-size: 10px; text-transform: uppercase; background: #f0fdf4; color: #166534; padding: 3px 8px; border-radius: 10px; }

.wf-step.active .step-num { background: var(--sigta-azul); color: var(--sigta-blanco); box-shadow: 0 0 0 4px rgba(0, 42, 92, 0.1); }
.wf-step.active .step-content { border-color: var(--sigta-azul); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.wf-step.locked { opacity: 0.5; pointer-events: none; }
.wf-step.locked .step-content { background: #f8fafc; }
.wf-step.completed .step-num { background: var(--sigta-azul-medio); color: var(--sigta-blanco); }
.wf-step.completed .step-content { border-color: var(--sigta-borde-suave); background: #f8fafc; }

.step-actions { display: flex; gap: 10px; }
.flex-btn { flex: 1; text-align: center; justify-content: center; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; }
.reject { background: var(--sigta-blanco); border: 1px solid var(--sigta-error); color: var(--sigta-error); padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
.p-options { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }
.p-options label { border: 1px solid var(--sigta-borde); border-radius: 6px; padding: 8px; text-align: center; font-size: 12px; font-weight: bold; cursor: pointer; color: var(--sigta-texto-suave); }
.p-options label:has(input:checked) { background: #e0e7ff; border-color: var(--sigta-azul); color: var(--sigta-azul); }
.p-options input { display: none; }
textarea { width: 100%; border: 1px solid var(--sigta-borde); border-radius: 6px; padding: 10px; font-family: inherit; font-size: 13px; resize: vertical; margin-bottom: 15px; }
.full-select { width: 100%; border: 1px solid var(--sigta-borde); border-radius: 6px; padding: 10px; font-family: inherit; font-size: 13px; color: var(--sigta-texto); background: #fff; margin-bottom: 15px; }
.step-btn { width: 100%; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; background: var(--sigta-azul); color: var(--sigta-blanco); font-size: 14px; text-align: center; }

@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}.gestion-tickets-layout{flex-direction:column;height:auto}.gestion-left{width:100%;height:300px}}@media(max-width:760px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column;gap:12px}.detalle-fila{grid-template-columns:1fr}.p-options{grid-template-columns:1fr 1fr}}
</style>
