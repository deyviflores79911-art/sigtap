<template>
  <div class="layout sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><b><img src="/img/emi.jpg" alt="EMI"></b><div><strong>SIGTA</strong><small>Mantenimiento</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="profile"><i>{{ iniciales }}</i><div><b>{{ nombre }}</b><small>Técnico de Mantenimiento</small></div></div>
      <p>MI TRABAJO</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="irA(m.id)"><span>{{ m.icono }}</span>{{ m.nombre }}<em v-if="m.total!==undefined">{{ m.total }}</em></button>
      <div class="bottom"><button @click="salir"><span>↪</span>Cerrar sesión</button></div>
    </aside>

    <main>
      <header>
        <div><small>SIGTA / MANTENIMIENTO / {{ titulo }}</small><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <button class="refresh" :disabled="cargando" @click="cargar">↻ Actualizar</button>
      </header>

      <div v-if="errorCarga" class="error-carga"><b>No se pudieron cargar los requerimientos.</b><span>{{ errorCarga }}</span></div>

      <!-- ============================ RESUMEN ============================ -->
      <section v-if="vista==='resumen'">
        <div class="hero">
          <div><small>TÉCNICO DE MANTENIMIENTO</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Órdenes de trabajo asignadas a usted.</p></div>
          <span>MT</span>
        </div>

        <div v-if="conRetorno.length" class="alerta">
          <b>⚠ {{ conRetorno.length }} orden(es) devuelta(s) por la jefatura</b>
          <span>{{ conRetorno.map(r=>r.codigo).join(', ') }} — el problema no quedó resuelto; repita la intervención.</span>
        </div>

        <div class="stats">
          <article @click="irA('ordenes')"><i class="blue">OT</i><div><small>Órdenes por recibir</small><b>{{ porRecibir.length }}</b><p>designadas por la jefatura</p></div></article>
          <article @click="irA('trabajo')"><i class="gold">RP</i><div><small>En reparación</small><b>{{ porReparar.length }}</b><p>trabajo en curso</p></div></article>
          <article @click="irA('trabajo')"><i class="green">PB</i><div><small>Por probar</small><b>{{ porProbar.length }}</b><p>pruebas e informe</p></div></article>
          <article @click="irA('recepcion')"><i class="navy">AC</i><div><small>Por recibir</small><b>{{ porRecibirComponente.length }}</b><p>componente y acta</p></div></article>
        </div>

        <div class="panels">
          <section class="panel">
            <div class="panel-head"><div><h3>Atención del mantenimiento</h3></div></div>
            <button class="flow" @click="irA('ordenes')"><i class="blue">1</i><div><b>Recibir orden de trabajo</b><small>Tomar conocimiento del requerimiento designado</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('ordenes')"><i class="blue">2</i><div><b>Inspección técnica y diagnóstico</b><small>Determinar la falla y si requiere compra</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('compras')"><i class="navy">3</i><div><b>Realizar requerimiento</b><small>Características del componente y cotización</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('recepcion')"><i class="navy">4</i><div><b>Recibir componente y acta</b><small>Confirmar la entrega de Almacén</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('trabajo')"><i class="gold">5</i><div><b>Reparación o instalación</b><small>Ejecutar y registrar la intervención</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('trabajo')"><i class="green">6</i><div><b>Pruebas e informe a la jefatura</b><small>Comprobar el funcionamiento y elevar el informe</small></div><strong>›</strong></button>
          </section>
          <section class="panel">
            <div class="panel-head"><div><small>SEGUIMIENTO</small><h3>Historial</h3></div></div>
            <p class="copy">Consulte los requerimientos que ya atendió y su estado actual.</p>
            <button class="wide primary" @click="irA('historial')">Ver historial →</button>
          </section>
        </div>
      </section>

            <!-- ==================== A. ÓRDENES DE TRABAJO (MASTER-DETAIL) ==================== -->
      <section v-else-if="vista==='recepcion'" class="gestion-tickets-layout">
        <div class="gestion-left"><div class="gestion-left-header"><h3>Componentes pendientes</h3><span class="badge gold-badge">{{ porRecibirComponente.length }} requiere acción</span></div><div class="gestion-lista">
          <article v-for="r in porRecibirComponente" :key="r.id" :class="['ticket-item', { activo: recepcionActiva?.id === r.id }]" @click="abrirRecepcion(r)"><div class="top"><span>{{ r.codigo }}</span><em class="e-clasificar">ACTA DISPONIBLE</em></div><h4>{{ r.titulo }}</h4><p>{{ r.producto_requerido || 'Componente de mantenimiento' }}</p><p class="item-meta">{{ r.codigo_compra_vinculada }} · {{ r.cantidad_requerida || 1 }} unid.</p></article>
          <div v-if="!porRecibirComponente.length" class="empty-list">Bandeja al día. No tiene componentes ni actas pendientes.</div>
        </div></div>
        <section class="gestion-right">
          <div v-if="!recepcionActiva" class="ticket-header-card selector-vacio"><span>←</span><h3>Seleccione un componente</h3><p>Revise el acta enviada por Almacén y confirme la recepción.</p></div>
          <div v-else class="gestion-detalle-wrapper"><div class="ticket-header-card"><div class="t-head"><h2>{{ recepcionActiva.codigo }}</h2><span class="codigo-badge">Recepción de componente</span></div><p>{{ recepcionActiva.titulo }}</p><div class="t-meta"><span><b>Componente:</b> {{ recepcionActiva.producto_requerido || 's/d' }}</span><span><b>Cantidad:</b> {{ recepcionActiva.cantidad_requerida || 1 }} unid.</span></div></div>
            <div class="workflow-card"><div class="wf-header">Flujo de recepción de componente</div><div class="wf-body">
              <div class="wf-step" :class="{active:pasoRecepcion===1,completed:pasoRecepcion>1}"><div class="step-num">1</div><div class="step-content"><h4>Revisar acta de conformidad</h4><p>Verifique que el componente y el acta remitidos por Almacén correspondan al requerimiento.</p><div v-if="pasoRecepcion===1" class="step-form"><div class="evidence-box"><div class="evidence-info"><strong>Acta de conformidad</strong><span>{{ recepcionActiva.codigo_compra_vinculada }}</span></div><a v-if="recepcionActiva.compra_vinculada?.acta_conformidad" :href="recepcionActiva.compra_vinculada.acta_conformidad" target="_blank" class="evidence-btn">Abrir acta</a><span v-else class="sin-adjunto">Acta no disponible</span></div><div class="step-actions"><button class="reject" @click="cerrarRecepcion">Cancelar</button><button class="flex-btn primary" :disabled="!recepcionActiva.compra_vinculada?.acta_conformidad" @click="pasoRecepcion=2">Aprobar y continuar</button></div></div></div></div>
              <div class="wf-step" :class="{active:pasoRecepcion===2,completed:pasoRecepcion>2,locked:pasoRecepcion<2}"><div class="step-num">2</div><div class="step-content"><h4>Confirmar recepción del componente</h4><p>Confirme que recibió físicamente el componente y el acta.</p><div v-if="pasoRecepcion===2" class="step-form"><label class="campo">Descripción de recepción<textarea v-model="formRecepcion.observacion" rows="3" placeholder="Estado del componente, embalaje u observación relevante..."></textarea></label><label class="confirmacion"><input v-model="formRecepcion.confirmado" type="checkbox"> Confirmo que recibí el componente y revisé el acta de conformidad.</label><div class="step-actions"><button class="reject" @click="pasoRecepcion=1">Retroceder</button><button class="flex-btn primary" :disabled="!formRecepcion.confirmado" @click="pasoRecepcion=3">Continuar</button></div></div></div></div>
              <div class="wf-step" :class="{active:pasoRecepcion===3,locked:pasoRecepcion<3}"><div class="step-num">3</div><div class="step-content"><h4>Habilitar reparación y pruebas</h4><p>Al confirmar, el requerimiento pasará a su bandeja de reparación y pruebas.</p><div v-if="pasoRecepcion===3" class="step-form"><div class="step-actions"><button class="reject" @click="pasoRecepcion=2">Retroceder</button><button class="flex-btn primary" :disabled="procesando" @click="confirmarRecepcion">Confirmar recepción</button></div></div></div></div>
            </div></div>
          </div>
        </section>
      </section>

      <section v-else-if="['ordenes','cotizaciones'].includes(vista)" class="gestion-tickets-layout">
        <div class="gestion-left">
          <div class="gestion-left-header">
            <h3>Órdenes de Trabajo</h3>
            <span class="badge">{{ (vista==='cotizaciones'?porCotizar:porRecibir).length }} Pendientes</span>
          </div>
          <div class="gestion-lista">
            <article v-for="r in (vista==='cotizaciones'?porCotizar:porRecibir)" :key="r.id" :class="['ticket-item', ordenAbierta?.id === r.id ? 'activo' : '', 't-validar']" @click="recibirOrden(r)">
              <div class="top">
                <span>{{ r.codigo }}</span>
                <em class="e-validar">{{ r.prioridad_jefatura || r.estado_codigo }}</em>
              </div>
              <h4>{{ r.titulo }}</h4>
              <p>📍 {{ r.ubicacion || 's/d' }}</p>
            </article>
            <div v-if="!(vista==='cotizaciones'?porCotizar:porRecibir).length" class="empty-list">Bandeja al día. No tiene órdenes pendientes.</div>
          </div>
        </div>

        <div class="gestion-right">
          <div v-if="!ordenAbierta" class="empty">
            <span>←</span>
            <h3>Seleccione una orden</h3>
            <p>Seleccione una orden de trabajo de la lista para registrar el diagnóstico.</p>
          </div>
          <div v-else class="gestion-detalle-wrapper">
            <div class="ticket-header-card">
              <div class="t-head">
                <h2>{{ ordenAbierta.titulo }}</h2>
                <span class="codigo-badge">{{ ordenAbierta.codigo }}</span>
              </div>
              <p class="t-meta"><b>Solicitante:</b> {{ ordenAbierta.solicitante_nombre }} • <b>Ubicación:</b> {{ ordenAbierta.ubicacion }}</p>
              <div class="desc-box">{{ ordenAbierta.descripcion }}</div>
              <a v-if="ordenAbierta.evidencia_archivo_url" class="adjunto mt-2 block" :href="ordenAbierta.evidencia_archivo_url" target="_blank">📎 Ver Evidencia Adjunta</a>
            </div>

            <div class="workflow-card">
              <div class="wf-header">Consola de Diagnóstico</div>
              <div class="wf-body">
                
                <!-- PASO 1: DIAGNÓSTICO -->
                <div :class="['wf-step', modoComponente ? 'completed' : 'active']">
                  <div class="step-num">1</div>
                  <div class="step-content">
                    <h4>Inspección técnica y diagnóstico <span v-if="modoComponente" class="step-badge">✓ Registrado</span></h4>
                    <p v-if="!modoComponente">Registre los resultados de la inspección inicial.</p>
                    <div v-if="!modoComponente">
                      <label class="campo">Diagnóstico
                        <textarea v-model="formDiagnostico.diagnostico" rows="3" placeholder="Falla detectada y componente afectado"></textarea>
                      </label>
                      <label class="campo">Plan de solución
                        <textarea v-model="formDiagnostico.plan_solucion" rows="2" placeholder="Acciones previstas para resolver el problema"></textarea>
                      </label>
                      
                      <fieldset class="compuerta" style="margin-bottom: 15px; border: 1px solid var(--sigta-borde); padding: 10px; border-radius: 6px;">
                        <legend style="font-size:12px; font-weight:bold; color:var(--sigta-texto-suave);">¿Requiere compra de componentes?</legend>
                        <label style="margin-right:15px; cursor:pointer;"><input v-model="formDiagnostico.requiere_compra" type="radio" :value="false"> No</label>
                        <label style="cursor:pointer;"><input v-model="formDiagnostico.requiere_compra" type="radio" :value="true"> Sí</label>
                      </fieldset>

                      <button class="primary step-btn" :disabled="procesando||!formDiagnostico.diagnostico.trim()||!formDiagnostico.plan_solucion.trim()" @click="guardarDiagnostico">
                        {{ formDiagnostico.requiere_compra ? 'Guardar y realizar requerimiento' : 'Guardar diagnóstico' }}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- PASO 2: REQUERIMIENTO DE COMPRA -->
                <div v-if="formDiagnostico.requiere_compra" :class="['wf-step', !modoComponente ? 'locked' : 'active']">
                  <div class="step-num">2</div>
                  <div class="step-content">
                    <h4>Realizar requerimiento de compra</h4>
                    <p>Complete la solicitud del repuesto necesario.</p>
                    <div v-if="modoComponente">
                      <label class="campo">Componente requerido
                        <input v-model="formComponente.producto_requerido" placeholder="Ej.: Compresor 12000 BTU" class="full-select">
                      </label>
                      <label class="campo">Características del componente
                        <textarea v-model="formComponente.especificacion_producto" rows="2" placeholder="Marca, modelo, voltaje..."></textarea>
                      </label>
                      <label class="campo">Cantidad
                        <input v-model="formComponente.cantidad_requerida" type="number" min="1" class="full-select">
                      </label>
                      <label class="campo">Costo estimado (Bs.)
                        <input v-monto inputmode="decimal" pattern="[0-9]+([.][0-9]{1,2})?" v-model="formComponente.costo_estimado" type="text" min="0" max="9999999999.99" step="0.01" class="full-select">
                      </label>
                      <label class="campo">Informe técnico con cuadros (obligatorio)
                        <input type="file" accept=".pdf,.doc,.docx,image/*" @change="e => formComponente.informe = e.target.files?.[0] || null">
                        <a v-if="ordenAbierta?.informe_compra" :href="ordenAbierta.informe_compra" target="_blank">Ver informe guardado</a>
                      </label>
                      <label class="campo">Cotización (obligatoria)
                        <input type="file" accept="application/pdf,image/*" @change="onCotizacion" class="full-select">
                      </label>
                      
                      <div class="step-actions mt-2">
                        <button class="reject" @click="retroceder">Retroceder</button>
                        <button class="step-btn" :disabled="procesando" @click="guardarBorradorCompra">Guardar borrador</button><button class="primary flex-btn" :disabled="procesando||!formComponente.producto_requerido.trim() || !(formComponente.informe || ordenAbierta?.informe_compra) || !(formComponente.archivo || ordenAbierta?.cotizacion_archivo)" @click="enviarRequerimiento">Enviar requerimiento</button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== EN ESPERA DE COMPRA ==================== -->
      <section v-else-if="vista==='compras'">
        <div class="instruction"><b>Requerimientos en curso</b><span>El trabajo está en pausa: se reanuda cuando Almacén entregue el componente.</span></div>
        <div v-if="enEsperaCompra.length" class="cards">
          <article v-for="r in enEsperaCompra" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_compra_componente }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <ul class="datos">
              <li><b>Componente</b><span>{{ r.producto_requerido || 's/d' }}</span></li>
              <li><b>Costo estimado</b><span>{{ r.costo_estimado ? `Bs. ${r.costo_estimado}` : 's/d' }}</span></li>
              <li><b>Expediente</b><span>{{ r.codigo_compra_vinculada || 'aún no generado' }}</span></li>
            </ul>
            <p>{{ r.estado_compra_componente === 'SOLICITADA' ? 'Pendiente de que la jefatura evalúe la viabilidad.' : 'Compra en curso en la DAF.' }}</p>
            <div class="actions"><button @click="verItem(r)">Ver detalle</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin requerimientos en curso</h3><p>Ninguna orden suya espera una compra.</p></div>
      </section>

      <!-- ============= D. REPARACIÓN, PRUEBAS E INFORME ============= -->
      <section v-else-if="['trabajo','informes'].includes(vista)" class="gestion-tickets-layout">
        <div class="gestion-left"><div class="gestion-left-header"><h3>Reparaciones pendientes</h3><span class="badge gold-badge">{{ enTrabajo.length }} requiere acción</span></div><div class="gestion-lista">
          <article v-for="r in enTrabajo" :key="r.id" :class="['ticket-item', { activo: itemActivo?.id === r.id, retorno: Number(r.rework_count) > 0 }]" @click="abrirTrabajo(r)"><div class="top"><span>{{ r.codigo }}</span><em>{{ etiqueta(r) }}</em></div><h4>{{ r.titulo }}</h4><p>{{ r.producto_requerido || r.ubicacion || 'Equipo de mantenimiento' }}</p><p class="item-meta">{{ siguientePaso(r) }}</p></article>
          <div v-if="!enTrabajo.length" class="empty-list">Bandeja al día. No hay reparaciones, pruebas ni informes pendientes.</div>
        </div></div>
        <section class="gestion-right">
          <div v-if="!itemActivo" class="ticket-header-card selector-vacio"><span>←</span><h3>Seleccione un requerimiento</h3><p>Revise primero el detalle y continúe el trabajo paso a paso.</p></div>
          <div v-else class="gestion-detalle-wrapper"><div class="ticket-header-card"><div class="t-head"><h2>{{ itemActivo.codigo }}</h2><span class="codigo-badge">Reparación y pruebas</span></div><p>{{ itemActivo.titulo }}</p><div class="t-meta"><span><b>Solicitante:</b> {{ itemActivo.solicitante_nombre || 's/d' }}</span><span><b>Ubicación:</b> {{ itemActivo.ubicacion || 's/d' }}</span></div><div class="desc-box">{{ itemActivo.diagnostico || itemActivo.descripcion }}</div></div>
            <div class="workflow-card"><div class="wf-header">Flujo de reparación y pruebas</div><div class="wf-body">
              <div class="wf-step" :class="{active:pasoTrabajo===1,completed:pasoTrabajo>1}"><div class="step-num">1</div><div class="step-content"><h4>Revisar requerimiento y documentación</h4><p>Revise el detalle, diagnóstico, evidencia y antecedentes antes de intervenir el equipo.</p><div class="step-form"><div class="revision-documentos"><div><b>Descripción del requerimiento</b><span>{{ itemActivo.descripcion || 'Sin descripción registrada.' }}</span></div><div><b>Diagnóstico técnico</b><span>{{ itemActivo.diagnostico || 'Sin diagnóstico registrado.' }}</span></div><div><b>Plan de solución</b><span>{{ itemActivo.plan_solucion || 'Sin plan registrado.' }}</span></div><a v-if="itemActivo.evidencia_archivo_url" :href="itemActivo.evidencia_archivo_url" target="_blank" class="evidence-btn">Abrir evidencia reportada</a><span v-else class="sin-adjunto">No existe evidencia adjunta.</span><a v-if="itemActivo.compra_vinculada?.acta_conformidad" :href="itemActivo.compra_vinculada.acta_conformidad" target="_blank" class="evidence-btn">Abrir acta de conformidad</a><span v-if="itemActivo.compra_vinculada && !itemActivo.compra_vinculada.acta_conformidad" class="sin-adjunto">La compra vinculada no tiene acta disponible.</span></div><button class="detalle-btn" @click="verItem(itemActivo)">Ver detalle completo</button><div v-if="pasoTrabajo===1" class="step-actions"><button class="reject" @click="cerrarTrabajo">Cancelar</button><button class="flex-btn primary" @click="pasoTrabajo=2">Siguiente</button></div></div></div></div>
              <div class="wf-step" :class="{active:pasoTrabajo===2,completed:pasoTrabajo>2,locked:pasoTrabajo<2}"><div class="step-num">2</div><div class="step-content"><h4>Registrar reparación o instalación</h4><p>El técnico documenta el trabajo ejecutado. Puede completar o corregir la información antes de continuar.</p><div v-if="pasoTrabajo>=2" class="step-form"><label class="campo">Reparación o instalación realizada<textarea v-model="formTrabajo.trabajo_realizado" rows="5" placeholder="Trabajo ejecutado sobre el equipo o instalación"></textarea></label><label class="campo">Observaciones<textarea v-model="formTrabajo.observaciones_trabajo" rows="2" placeholder="Observaciones de la intervención"></textarea></label><div v-if="pasoTrabajo===2" class="step-actions"><button class="reject" @click="pasoTrabajo=1">Retroceder</button><button class="flex-btn primary" :disabled="procesando||!formTrabajo.trabajo_realizado.trim()" @click="registrarTrabajo">Guardar reparación y continuar</button></div></div></div></div>
              <div class="wf-step" :class="{active:pasoTrabajo===3,completed:pasoTrabajo>3,locked:pasoTrabajo<3}"><div class="step-num">3</div><div class="step-content"><h4>Registrar pruebas técnicas</h4><p>El técnico registra las pruebas efectuadas y su resultado antes de preparar el informe.</p><div v-if="pasoTrabajo>=3" class="step-form"><label class="campo">Resultado de las pruebas técnicas<textarea v-model="formPruebas.resultado_pruebas" rows="4" placeholder="Pruebas efectuadas y comportamiento del equipo"></textarea></label><div v-if="pasoTrabajo===3" class="step-actions"><button class="reject" @click="pasoTrabajo=2">Retroceder</button><button class="flex-btn primary" :disabled="procesando||!formPruebas.resultado_pruebas.trim()" @click="registrarPruebas">Guardar pruebas y continuar</button></div></div></div></div>
              <div class="wf-step" :class="{active:pasoTrabajo===4,locked:pasoTrabajo<4}"><div class="step-num">4</div><div class="step-content"><h4>Elaborar informe al Jefe de Mantenimiento</h4><p>Redacte el informe con el resumen del trabajo, las pruebas y el resultado. Al enviarlo, el Jefe de Mantenimiento recibirá el caso.</p><div v-if="pasoTrabajo===4" class="step-form"><label class="campo">Informe al Jefe de Mantenimiento<textarea v-model="formInforme.informe_trabajo" rows="6" placeholder="Describa el trabajo realizado, componentes utilizados, pruebas efectuadas y resultado final."></textarea></label><label class="campo">Informe técnico con cuadros / fotografía del trabajo<input type="file" accept="application/pdf,image/*" @change="onFotografia"></label><div class="step-actions"><button class="reject" @click="pasoTrabajo=3">Retroceder</button><button class="flex-btn primary" :disabled="procesando||!formInforme.informe_trabajo.trim()" @click="registrarInforme">{{ procesando ? 'Enviando...' : 'Enviar informe al Jefe de Mantenimiento' }}</button></div></div></div></div>
            </div></div>
          </div>
        </section>
      </section>

      <!-- =========================== HISTORIAL =========================== -->
      <section v-else-if="vista==='historial'">
        <div class="instruction"><b>Historial</b><span>Requerimientos que usted atendió.</span></div>
        <div v-if="misItems.length" class="cards">
          <article v-for="r in misItems" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <p>{{ (r.descripcion||'').slice(0,130) }}</p>
            <div class="actions"><button @click="verItem(r)">Ver detalle</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin registros</h3><p>Todavía no tiene requerimientos asignados.</p></div>
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
          <div class="detalle-campo"><b>Descripción</b><p>{{ detalle.descripcion }}</p></div>
          <div class="detalle-campo"><b>Ubicación</b><span>{{ detalle.ubicacion || 's/d' }}</span></div>
          <div class="detalle-campo" v-if="detalle.diagnostico"><b>Diagnóstico</b><p>{{ detalle.diagnostico }}</p></div>
          <div class="detalle-campo" v-if="detalle.plan_solucion"><b>Plan de solución</b><p>{{ detalle.plan_solucion }}</p></div>
          <div class="detalle-campo" v-if="detalle.producto_requerido"><b>Componente</b><p>{{ detalle.producto_requerido }} — Bs. {{ detalle.costo_estimado || 's/d' }}</p></div>
          <div class="detalle-campo" v-if="detalle.motivo_no_viable"><b>Compra no viable</b><p>{{ detalle.motivo_no_viable }}</p></div>
          <div class="detalle-campo" v-if="detalle.trabajo_realizado"><b>Trabajo realizado</b><p>{{ detalle.trabajo_realizado }}</p></div>
          <div class="detalle-campo" v-if="detalle.resultado_pruebas"><b>Pruebas técnicas</b><p>{{ detalle.resultado_pruebas }}</p></div>
          <div class="detalle-campo" v-if="detalle.informe_trabajo"><b>Informe a la jefatura</b><p>{{ detalle.informe_trabajo }}</p></div>
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
const cargando = ref(false)
const errorCarga = ref('')
const procesando = ref(false)
const itemActivo = ref(null)
const pasoTrabajo = ref(1)
const ordenAbierta = ref(null)
const recepcionActiva = ref(null)
const pasoRecepcion = ref(1)
const modoComponente = ref(false)
const detalle = ref(null)

const nombre = computed(() => usuario.value.nombre || usuario.value.nombre_completo || 'Técnico de Mantenimiento')
const primerNombre = computed(() => nombre.value.split(' ')[0])
const iniciales = computed(() => nombre.value.split(' ').slice(0, 2).map(x => x[0]).join('').toUpperCase())
const saludo = computed(() => new Date().getHours() < 12 ? 'Buenos días' : new Date().getHours() < 19 ? 'Buenas tardes' : 'Buenas noches')

const misItems = computed(() => items.value.filter(r => Number(r.auxiliar_asignado) === Number(usuario.value.id)))
const enCompra = r => ['SOLICITADA', 'VIABLE'].includes(r.estado_compra_componente)

const porRecibir = computed(() => misItems.value.filter(r => r.estado_codigo === 'DERIVADO'))
const porRecibirComponente = computed(() => misItems.value.filter(r => r.estado_compra_componente === 'PENDIENTE_RECEPCION_TECNICO'))
const enEsperaCompra = computed(() => misItems.value.filter(r => r.estado_codigo === 'EN_ESPERA_COMPRA' || enCompra(r)))
const porReparar = computed(() => misItems.value.filter(r => r.estado_codigo === 'EN_MANTENIMIENTO' && !r.trabajo_realizado && !enCompra(r)))
const porProbar = computed(() => misItems.value.filter(r => r.estado_codigo === 'EN_MANTENIMIENTO' && !!r.trabajo_realizado && !enCompra(r)))
const enTrabajo = computed(() => vista.value==='informes' ? porProbar.value : porReparar.value)
const porCotizar = computed(() => misItems.value.filter(r=>r.estado_codigo==='EN_MANTENIMIENTO' && !r.estado_compra_componente))
const conRetorno = computed(() => misItems.value.filter(r => Number(r.rework_count) > 0 && r.estado_codigo === 'EN_MANTENIMIENTO'))

const menu = computed(() => [
  { id: 'resumen', icono: '⌂', nombre: 'Resumen' },
  { id: 'ordenes', icono: 'OT', nombre: 'Órdenes de trabajo', total: porRecibir.value.length },
  { id: 'recepcion', icono: 'AC', nombre: 'Recibir componente y acta', total: porRecibirComponente.value.length },
  { id: 'trabajo', icono: 'RP', nombre: 'Trabajos y anotaciones', total: porReparar.value.length },
  { id: 'cotizaciones', icono: 'CT', nombre: 'Cotizaciones y requerimientos', total: porCotizar.value.length },
  { id: 'informes', icono: 'IF', nombre: 'Pruebas e informes', total: porProbar.value.length },
  { id: 'compras', icono: 'CO', nombre: 'En espera de compra', total: enEsperaCompra.value.length },
  { id: 'historial', icono: 'HI', nombre: 'Historial' },
])

const titulo = computed(() => ({
  resumen: 'Panel del Técnico de Mantenimiento',
  ordenes: ordenAbierta.value ? 'Inspección técnica y diagnóstico' : 'Bandeja de órdenes de trabajo',
  recepcion: 'Recibir componente y acta',
  trabajo: 'Reparación, pruebas e informe',
  cotizaciones: 'Cotizaciones y requerimientos',
  informes: 'Pruebas e informes técnicos',
  compras: 'Requerimientos en espera de compra',
  historial: 'Historial de requerimientos',
}[vista.value]))

const subtitulo = computed(() => ({
  resumen: 'Diagnóstico, reparación y pruebas de los requerimientos asignados a usted.',
  ordenes: 'Requerimientos designados por la jefatura de mantenimiento.',
  recepcion: 'Componentes entregados por Almacén que requieren su confirmación.',
  trabajo: 'Intervención técnica e informe dirigido a la jefatura.',
  compras: 'Requerimientos cuyo trabajo está en pausa hasta recibir el componente.',
  historial: 'Todos los requerimientos que usted atendió.',
}[vista.value]))

function etiqueta(r) {
  if (enCompra(r)) return 'En espera de compra'
  if (!r.trabajo_realizado) return 'En reparación'
  if (!r.resultado_pruebas) return 'Por probar'
  return 'Por informar'
}

function siguientePaso(r) {
  if (!r.trabajo_realizado) return 'Registrar reparación'
  if (!r.resultado_pruebas) return 'Registrar pruebas'
  return 'Elaborar informe'
}

function fecha(valor) {
  return valor ? new Date(valor).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' }) : 's/d'
}

const base = '/api/mantenimiento/requerimientos'
const token = () => localStorage.getItem('sigta_token')

function cerrarSesionExpirada() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.replace({ path: '/login', query: { motivo: 'sesion-expirada' } })
}

async function cargar() {
  cargando.value = true
  errorCarga.value = ''
  try {
    const r = await fetch(`${base}/`, { headers: { Authorization: `Token ${token()}` } })
    if (r.status === 401) {
      cerrarSesionExpirada()
      return
    }
    if (!r.ok) throw new Error(`El servidor respondió con código ${r.status}.`)
    const d = await r.json()
    items.value = Array.isArray(d) ? d : (d.results || [])
    if (ordenAbierta.value) ordenAbierta.value = items.value.find(x => x.id === ordenAbierta.value.id) || null
    if (itemActivo.value) itemActivo.value = items.value.find(x => x.id === itemActivo.value.id) || null
    if (recepcionActiva.value) recepcionActiva.value = items.value.find(x => x.id === recepcionActiva.value.id) || null
  } catch (e) {
    items.value = []
    errorCarga.value = e.message || 'Intente actualizar nuevamente.'
  } finally {
    cargando.value = false
  }
}

async function postAccion(item, endpoint, body, esFormData = false) {
  procesando.value = true
  try {
    const headers = { Authorization: `Token ${token()}` }
    if (!esFormData) headers['Content-Type'] = 'application/json'
    const r = await fetch(`${base}/${item.id}/${endpoint}/`, {
      method: 'POST',
      headers,
      body: esFormData ? body : JSON.stringify(body || {}),
    })
    const d = await r.json().catch(() => ({}))
    if (r.status === 401) {
      cerrarSesionExpirada()
      throw new Error('La sesión expiró. Inicie sesión nuevamente.')
    }
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible completar la acción.')
    await cargar()
    return d
  } finally {
    procesando.value = false
  }
}

function irA(id) {
  vista.value = id
  menuAbierto.value = false
  ordenAbierta.value = null
  itemActivo.value = null
  pasoTrabajo.value = 1
  recepcionActiva.value = null
  pasoRecepcion.value = 1
  modoComponente.value = false
}

function verItem(item) { detalle.value = item }

function salir() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.push('/login')
}

/* ---------- Diagnóstico y requerimiento ---------- */
const formDiagnostico = reactive({ diagnostico: '', plan_solucion: '', requiere_compra: false })
const formComponente = reactive({
  producto_requerido: '', especificacion_producto: '',
  cantidad_requerida: 1, costo_estimado: '', archivo: null, informe: null,
})
const formTrabajo = reactive({ trabajo_realizado: '', observaciones_trabajo: '' })
const formPruebas = reactive({ resultado_pruebas: '' })
const formInforme = reactive({ informe_trabajo: '', fotografia: null })
const formRecepcion = reactive({ confirmado: false, observacion: '' })

function abrirRecepcion(item) {
  recepcionActiva.value = item
  pasoRecepcion.value = 1
  formRecepcion.confirmado = false
  formRecepcion.observacion = ''
}

function cerrarRecepcion() {
  recepcionActiva.value = null
  pasoRecepcion.value = 1
}

async function confirmarRecepcion() {
  try {
    await postAccion(recepcionActiva.value, 'recibir-componente-acta', {
      observacion_recepcion_componente: formRecepcion.observacion.trim(),
    })
    cerrarRecepcion()
    vista.value = 'trabajo'
    alert('Recepción registrada. Ya puede realizar la reparación y las pruebas.')
  } catch (e) { alert(e.message) }
}

function recibirOrden(item) {
  ordenAbierta.value = item
  modoComponente.value = vista.value === 'cotizaciones'
  formDiagnostico.diagnostico = item.diagnostico || ''
  formDiagnostico.plan_solucion = item.plan_solucion || ''
  formDiagnostico.requiere_compra = false
  formComponente.producto_requerido = item.producto_requerido || ''
  formComponente.especificacion_producto = item.especificacion_producto || ''
  formComponente.cantidad_requerida = item.cantidad_requerida || 1
  formComponente.costo_estimado = item.costo_estimado || ''
  formComponente.archivo = null
  formComponente.informe = null
}

function cerrarOrden() {
  ordenAbierta.value = null
  modoComponente.value = false
}

function retroceder() {
  modoComponente.value = false
}

async function guardarDiagnostico() {
  try {
    await postAccion(ordenAbierta.value, 'registrar-diagnostico', {
      diagnostico: formDiagnostico.diagnostico.trim(),
      plan_solucion: formDiagnostico.plan_solucion.trim(),
    })
    const requiereCompra = formDiagnostico.requiere_compra
    cerrarOrden()
    vista.value = requiereCompra ? 'cotizaciones' : 'trabajo'
  } catch (e) { alert(e.message) }
}

function onCotizacion(evento) {
  formComponente.archivo = evento.target.files?.[0] || null
}

async function guardarBorradorCompra() {
  try {
    const fd = new FormData()
    for (const campo of ['producto_requerido','especificacion_producto','cantidad_requerida','costo_estimado']) fd.append(campo, formComponente[campo] ?? '')
    if (formComponente.archivo) fd.append('cotizacion_archivo', formComponente.archivo)
    if (formComponente.informe) fd.append('informe_compra', formComponente.informe)
    await postAccion(ordenAbierta.value, 'guardar-borrador-requerimiento', fd, true)
    alert('Borrador guardado. Puede continuar después desde Cotizaciones y requerimientos.')
  } catch(e) { alert(e.message) }
}

async function enviarRequerimiento() {
  procesando.value = true
  try {
    const token = localStorage.getItem('sigta_token');
    
    // 1. Guardar diagnóstico primero (solo si aún está en DERIVADO)
    if (ordenAbierta.value.estado_codigo === 'DERIVADO') {
      const respDiag = await fetch(`/api/mantenimiento/requerimientos/${ordenAbierta.value.id}/registrar-diagnostico/`, {
        method: 'POST',
        headers: { Authorization: `Token ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          diagnostico: formDiagnostico.diagnostico.trim(),
          plan_solucion: formDiagnostico.plan_solucion.trim(),
        })
      })
      
      if (!respDiag.ok) {
        const d = await respDiag.json().catch(() => ({}))
        throw new Error(d.detalle || 'Error al guardar el diagnóstico.')
      }
      
      // Marcar localmente para no repetir en caso de que el paso 2 falle
      ordenAbierta.value.estado_codigo = 'EN_MANTENIMIENTO';
    }

    // 2. Solicitar requerimiento
    const datos = new FormData()
    datos.append('producto_requerido', formComponente.producto_requerido.trim())
    datos.append('especificacion_producto', formComponente.especificacion_producto.trim())
    datos.append('cantidad_requerida', String(formComponente.cantidad_requerida || 1))
    if (formComponente.costo_estimado) datos.append('costo_estimado', formComponente.costo_estimado)
    if (formComponente.archivo) datos.append('cotizacion_archivo', formComponente.archivo)
    if (formComponente.informe) datos.append('informe_compra', formComponente.informe)
    
    await postAccion(ordenAbierta.value, 'solicitar-requerimiento', datos, true)
    
    cerrarOrden()
    vista.value = 'compras'
    alert('Requerimiento derivado al Jefe de Mantenimiento para proceder con la solicitud de compra.')
  } catch (e) { alert(e.message) }
  finally { procesando.value = false }
}

/* ---------- Reparación, pruebas e informe ---------- */
function abrirTrabajo(item) {
  itemActivo.value = item
  pasoTrabajo.value = item.resultado_pruebas ? 4 : item.trabajo_realizado ? 3 : 1
  formTrabajo.trabajo_realizado = item.trabajo_realizado || ''
  formTrabajo.observaciones_trabajo = item.observaciones_trabajo || ''
  formPruebas.resultado_pruebas = item.resultado_pruebas || ''
  formInforme.informe_trabajo = item.informe_trabajo || ''
  formInforme.fotografia = null
}

function cerrarTrabajo() {
  itemActivo.value = null
  pasoTrabajo.value = 1
}

async function registrarTrabajo() {
  try {
    await postAccion(itemActivo.value, 'realizar-mantenimiento', {
      trabajo_realizado: formTrabajo.trabajo_realizado.trim(),
      observaciones_trabajo: formTrabajo.observaciones_trabajo.trim(),
    })
    pasoTrabajo.value = 3
    vista.value = 'informes'
  } catch (e) { alert(e.message) }
}

async function registrarPruebas() {
  try {
    await postAccion(itemActivo.value, 'pruebas-tecnicas', {
      resultado_pruebas: formPruebas.resultado_pruebas.trim(),
    })
    pasoTrabajo.value = 4
  } catch (e) { alert(e.message) }
}

function onFotografia(evento) {
  formInforme.fotografia = evento.target.files?.[0] || null
}

async function registrarInforme() {
  if (!formInforme.informe_trabajo.trim()) {
    pasoTrabajo.value = 4
    alert('Debe registrar el informe de trabajo antes de enviarlo a la jefatura.')
    return
  }
  try {
    const datos = new FormData()
    datos.append('informe_trabajo', formInforme.informe_trabajo.trim())
    if (formInforme.fotografia) datos.append('fotografia_trabajo', formInforme.fotografia)
    await postAccion(itemActivo.value, 'registrar-informe', datos, true)
    itemActivo.value = null
    alert('Informe enviado. La jefatura verificará el funcionamiento.')
  } catch (e) { alert(e.message) }
}

onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.layout{min-height:100vh;background:var(--sigta-fondo);color:var(--sigta-texto);font-family:var(--sigta-fuente)}aside{position:fixed;inset:0 auto 0 0;width:var(--sigta-sidebar);background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand,.profile{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 20px;border-bottom:1px solid rgba(255,255,255,.2)}.brand>b{background:var(--sigta-mostaza);color:var(--sigta-azul);padding:14px 10px;border-radius:9px}.brand strong,.brand small,.profile b,.profile small{display:block}.brand strong{font-size:23px}.brand small,.profile small{color:var(--sigta-azul-texto-claro);margin-top:3px}.profile{padding:22px 10px}.profile>i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}aside>p{font-size:10px;color:var(--sigta-azul-texto-claro);font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{border:0;background:transparent;color:var(--sigta-blanco);border-radius:8px;padding:12px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0;width:100%}aside button>span{font-size:10px;font-weight:900;width:28px}aside button em{margin-left:auto;background:rgba(255,255,255,.16);padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:rgba(255,255,255,.13)}.bottom{margin-top:auto;border-top:1px solid rgba(255,255,255,.2);padding-top:10px}.bottom button{width:100%}main{margin-left:var(--sigta-sidebar);padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header small{color:var(--sigta-texto-suave)}h1{font-size:var(--sigta-titulo);margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.refresh{border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-azul);padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-azul-medio));color:var(--sigta-blanco);border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small,.hoja-head small{font-size:10px;font-weight:800;letter-spacing:1.4px;color:var(--sigta-mostaza-clara)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero>span{width:68px;height:68px;border:1px solid var(--sigta-mostaza);border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px;display:flex;gap:13px;cursor:pointer}.stats i,.flow i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:var(--sigta-blanco);font-size:10px;font-weight:900}.blue{background:var(--sigta-azul)}.gold{background:var(--sigta-mostaza);color:var(--sigta-texto)!important}.green{background:var(--sigta-azul-medio)}.navy{background:var(--sigta-azul-medio)}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.panels{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}.panel-head h3{margin:5px 0 14px}.flow{width:100%;border:0;border-top:1px solid var(--sigta-borde-suave);background:var(--sigta-blanco);padding:15px 2px;display:flex;gap:13px;align-items:center;text-align:left;cursor:pointer}.flow div{flex:1}.flow b,.flow small{display:block}.flow small{color:var(--sigta-texto-suave);margin-top:4px}.flow>strong{font-size:20px}.copy{color:var(--sigta-texto-suave);font-size:12px;line-height:1.7}.wide{width:100%;padding:10px;border-radius:7px;border:1px solid var(--sigta-borde);cursor:pointer}.primary{background:var(--sigta-azul)!important;color:var(--sigta-blanco)!important;border-color:var(--sigta-azul)!important}.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;margin-bottom:17px;border-radius:7px}.instruction b,.instruction span{display:block}.instruction span{font-size:12px;color:var(--sigta-alerta);margin-top:4px}.alerta{background:var(--sigta-error-fondo);border-left:4px solid var(--sigta-error);padding:14px 17px;margin:0 0 17px;border-radius:7px}.alerta b,.alerta span{display:block}.alerta b{color:var(--sigta-error)}.alerta span{font-size:12px;color:var(--sigta-error);margin-top:4px}.mini-alerta{background:var(--sigta-error-fondo);color:var(--sigta-error);font-size:11px;font-weight:700;padding:7px 9px;border-radius:6px;margin-bottom:10px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.cards article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px}.cards article.retorno{border-color:var(--sigta-error);box-shadow:inset 3px 0 var(--sigta-error)}.top{display:flex;justify-content:space-between;gap:8px}.top span{font-size:12px;font-weight:800;color:var(--sigta-azul)}.top em{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px;font-style:normal;white-space:nowrap}.cards h3{font-size:17px;margin:15px 0 7px}.cards article>p{font-size:12px;color:var(--sigta-texto-suave);min-height:42px}.datos{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:4px}.datos li{display:flex;justify-content:space-between;gap:10px;font-size:11px;border-bottom:1px dashed var(--sigta-borde-suave);padding-bottom:3px}.datos b{color:var(--sigta-texto-suave)}.datos span{color:var(--sigta-texto-suave);text-align:right}.adjunto{display:inline-block;font-size:11px;color:var(--sigta-azul);margin-bottom:10px;text-decoration:none}.actions{display:flex;gap:7px;border-top:1px solid var(--sigta-borde-suave);padding-top:13px;margin-top:10px}.actions button{flex:1;padding:9px 6px;border-radius:7px;border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-texto);font-weight:700;cursor:pointer}.actions button:disabled{opacity:.55;cursor:not-allowed}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-borde);padding:65px;border-radius:10px;color:var(--sigta-texto-suave)}.empty>span{font-size:31px;color:var(--sigta-exito)}.campo{display:block;margin:14px 0;font-size:12px;font-weight:700;color:var(--sigta-texto)}.campo input,.campo select,.campo textarea{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-borde);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}.hoja{max-width:820px}.hoja-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:16px}.hoja-head h3{margin:5px 0 0}.compuerta{border:1px solid var(--sigta-borde);border-radius:8px;padding:12px 15px;margin:16px 0;display:flex;gap:22px;align-items:center}.compuerta legend{font-size:12px;font-weight:700;color:var(--sigta-texto);padding:0 6px}.compuerta label{font-size:13px;display:flex;align-items:center;gap:6px;font-weight:600}.compuerta input{margin:0}.detalle-modal-backdrop{position:fixed;inset:0;background:rgba(18,58,107,.55);display:grid;place-items:center;padding:20px;z-index:20}.detalle-modal{background:var(--sigta-blanco);border-radius:14px;width:min(700px,100%);max-height:88vh;display:flex;flex-direction:column}.detalle-modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--sigta-borde-suave)}.detalle-modal-header h3{margin:0}.detalle-modal-header small{color:var(--sigta-texto-suave)}.detalle-modal-close{border:0;background:transparent;font-size:20px;cursor:pointer;color:var(--sigta-texto-suave)}.detalle-modal-body{padding:20px 24px;overflow-y:auto;display:grid;gap:14px}.detalle-fila{display:grid;grid-template-columns:1fr 1fr;gap:14px}.detalle-campo b{display:block;font-size:11px;color:var(--sigta-texto-suave);margin-bottom:4px}.detalle-campo span,.detalle-campo p{font-size:13px;color:var(--sigta-texto);margin:0}
/* ====== NUEVOS ESTILOS: GESTIÓN DE TICKETS (MASTER-DETAIL) ====== */
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
.ticket-header-card { background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; padding: 20px; flex-shrink: 0; }
.t-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.t-head h2 { margin: 0; font-size: 18px; color: var(--sigta-texto); }
.codigo-badge { font-weight: bold; color: var(--sigta-azul); font-size: 14px; }
.t-meta { margin: 0 0 12px; font-size: 12px; color: var(--sigta-texto-suave); }
.desc-box { background: #f8fafc; padding: 12px; border-radius: 8px; font-size: 13px; line-height: 1.5; color: var(--sigta-texto); border: 1px solid var(--sigta-borde-suave); }

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
.step-btn { width: 100%; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; background: var(--sigta-azul); color: var(--sigta-blanco); font-size: 14px; text-align: center; margin-top:10px; }
.error-carga{background:var(--sigta-error-fondo);border-left:4px solid var(--sigta-error);padding:12px 16px;border-radius:7px;margin:-10px 0 17px}.error-carga b,.error-carga span{display:block}.error-carga b{color:var(--sigta-error);font-size:13px}.error-carga span{color:var(--sigta-error);font-size:12px;margin-top:3px}
.detalle-btn{width:100%;background:var(--sigta-blanco);border:1px solid var(--sigta-borde);color:var(--sigta-azul);padding:10px;border-radius:6px;font-weight:700;cursor:pointer;margin:0 0 14px}
.revision-documentos,.registro-resumen,.envio-resumen{display:grid;gap:8px;background:#f8fafc;border:1px solid var(--sigta-borde-suave);border-radius:8px;padding:13px;margin:0 0 14px}.revision-documentos>div{display:grid;gap:3px;padding-bottom:8px;border-bottom:1px solid var(--sigta-borde-suave)}.revision-documentos>div:last-of-type{border-bottom:0;padding-bottom:0}.revision-documentos b,.registro-resumen b,.envio-resumen b{font-size:11px;color:var(--sigta-texto-suave)}.revision-documentos span,.registro-resumen span,.envio-resumen span{font-size:12px;color:var(--sigta-texto);line-height:1.45}.envio-resumen{grid-template-columns:auto 1fr}.envio-resumen b{align-self:start}
.gold-badge{background:#fef3c7;color:#854d0e}.item-meta{margin-top:6px!important;color:var(--sigta-mostaza-oscuro)!important;font-weight:700}.selector-vacio{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:var(--sigta-texto-suave)}.selector-vacio>span{font-size:30px;color:var(--sigta-exito)}.evidence-box{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#f8fafc;border:1px solid var(--sigta-borde-suave);border-radius:8px;padding:12px;margin:14px 0}.evidence-info{display:flex;flex-direction:column;gap:3px}.evidence-info strong{font-size:13px}.evidence-info span,.sin-adjunto{font-size:11px;color:var(--sigta-texto-suave)}.evidence-btn{background:var(--sigta-azul);color:var(--sigta-blanco);padding:7px 11px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:700}.confirmacion{display:flex;gap:8px;align-items:flex-start;margin:14px 0 18px;font-size:12px;font-weight:700;line-height:1.45}.confirmacion input{margin:2px 0 0;width:auto}

@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:760px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column;gap:12px}.detalle-fila{grid-template-columns:1fr}}
</style>
