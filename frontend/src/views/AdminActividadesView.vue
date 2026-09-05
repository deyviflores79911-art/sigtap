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
            Actividades
          </h1>

          <p>
            Informes de actividad que las jefaturas remiten a la
            Dirección al cerrar un flujo.
          </p>
        </div>

      </header>


      <!-- =================================================
           SEPARACIÓN POR JEFATURA
      ================================================== -->

      <nav class="jefatura-tabs">

        <button
          type="button"
          :class="['jefatura-tab', { activa: jefatura === 'MANTENIMIENTO' }]"
          @click="jefatura = 'MANTENIMIENTO'"
        >
          <IconoSigta class="jefatura-tab-icono" nombre="mantenimiento" :tamano="18" />
          Mantenimiento
          <span class="jefatura-tab-contador">
            {{ informesMantenimiento.length }}
          </span>
        </button>

        <button
          type="button"
          :class="['jefatura-tab', { activa: jefatura === 'UTIC' }]"
          @click="jefatura = 'UTIC'"
        >
          <IconoSigta class="jefatura-tab-icono" nombre="soporte" :tamano="18" />
          Soporte Técnico
          <span class="jefatura-tab-contador">
            {{ informesUtic.length }}
          </span>
        </button>

      </nav>


      <!-- =================================================
           LISTADO
      ================================================== -->

      <div
        v-if="informesVisibles.length === 0"
        class="empty"
      >
        No hay informes de actividad registrados.
      </div>

      <section
        v-else
        class="requests-card"
      >

        <div class="request-list">

          <article
            v-for="informe in informesVisibles"
            :key="informe.id"
            class="request"
          >

            <div class="request-main">

              <div class="request-code">
                <strong>
                  {{ informe.codigo }}
                </strong>

                <small>
                  {{ informe.periodo }}
                </small>
              </div>


              <div class="request-info">

                <h3>
                  {{ informe.titulo }}
                </h3>

                <div class="meta">
                  <span>{{ informe.jefe }}</span>
                  <span>{{ informe.origen }}</span>
                  <span>{{ informe.fecha }}</span>
                </div>

                <p class="resumen">
                  {{ informe.resumen }}
                </p>

              </div>

            </div>


            <div class="request-side">

              <span
                :class="['status', informe.leido ? 'closed' : 'working']"
              >
                {{ informe.leido ? 'Revisado' : 'Nuevo' }}
              </span>

              <div class="row-actions">

                <button
                  class="view"
                  @click="verDetalle(informe)"
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
         DETALLE DEL INFORME
    ================================================== -->

    <div
      v-if="informeSeleccionado"
      class="detalle-modal-backdrop"
      @click.self="cerrarDetalle"
    >
      <div class="detalle-modal informe-modal">

        <div class="detalle-modal-header">
          <div class="informe-header-titulo">

            <IconoSigta class="informe-header-icono" nombre="auditoria" :tamano="22" />

            <div>
              <h3>{{ informeSeleccionado.codigo }}</h3>
              <small>{{ informeSeleccionado.titulo }}</small>
            </div>

          </div>

          <button
            class="detalle-modal-close"
            @click="cerrarDetalle"
          >✕</button>
        </div>

        <div class="informe-body">

          <div class="informe-cabecera">

            <div class="informe-dato">
              <b>Jefatura</b>
              <strong>{{ informeSeleccionado.jefaturaNombre }}</strong>
            </div>

            <div class="informe-dato">
              <b>Periodo</b>
              <strong>{{ informeSeleccionado.periodo }}</strong>
            </div>

            <div class="informe-dato">
              <b>Remitido</b>
              <strong>{{ informeSeleccionado.fecha }}</strong>
            </div>

          </div>

          <dl class="ficha">

            <div>
              <dt>Remitente</dt>
              <dd>{{ informeSeleccionado.jefe }}</dd>
            </div>

            <div>
              <dt>Origen</dt>
              <dd>{{ informeSeleccionado.origen }}</dd>
            </div>

            <div>
              <dt>Atendidos</dt>
              <dd>{{ informeSeleccionado.atendidos }}</dd>
            </div>

          </dl>

          <div class="informe-seccion">

            <span class="informe-titulo">
              Contenido del informe
            </span>

            <p>{{ informeSeleccionado.contenido }}</p>

          </div>

        </div>

        <div class="informe-acciones">

          <button
            class="btn-cerrar"
            @click="cerrarDetalle"
          >
            Cerrar
          </button>

        </div>

      </div>
    </div>

  </div>
</template>


<script setup>

/* =========================================================
   ACTIVIDADES (SOLO VISTA)

   Pantalla de maqueta: muestra cómo verá la Dirección los
   informes de actividad que remiten la Jefatura de UTIC y la
   de Mantenimiento al cerrar un flujo, separados por jefatura.

   Los datos de abajo son DE MUESTRA y están escritos a mano.
   Esta vista no llama a ninguna API ni modifica nada; el
   backend ya tiene el modelo InformeJefatura y el endpoint
   /api/usuarios/informes-jefatura/, pendientes de conectar.
========================================================= */

import { computed, ref } from 'vue'

import AdminMenu
  from '../components/AdminMenu.vue'

import IconoSigta
  from '../components/IconoSigta.vue'

import { INFORMES_MUESTRA }
  from '../data/informesActividad.js'


const jefatura =
  ref('MANTENIMIENTO')




const informesMantenimiento =
  computed(() =>
    INFORMES_MUESTRA.filter(
      informe => informe.jefatura === 'MANTENIMIENTO'
    )
  )


const informesUtic =
  computed(() =>
    INFORMES_MUESTRA.filter(
      informe => informe.jefatura === 'UTIC'
    )
  )


const informesVisibles =
  computed(() =>
    jefatura.value === 'MANTENIMIENTO'
      ? informesMantenimiento.value
      : informesUtic.value
  )


const informeSeleccionado =
  ref(null)


function verDetalle(informe) {

  informeSeleccionado.value =
    informe
}


function cerrarDetalle() {

  informeSeleccionado.value =
    null
}

</script>


<style scoped>

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


/* =========================================================
   PESTAÑAS POR JEFATURA
========================================================= */

.jefatura-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 18px;
  border-bottom: 2px solid var(--sigta-azul-tenue);
}


.jefatura-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  background: transparent;
  color: var(--sigta-texto-suave);
  font-family: inherit;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}


.jefatura-tab:hover {
  color: var(--sigta-azul-oscuro);
}


.jefatura-tab.activa {
  color: var(--sigta-azul-oscuro);
  border-bottom-color: var(--sigta-mostaza);
}


.jefatura-tab-icono {
  flex-shrink: 0;
}


.jefatura-tab-contador {
  padding: 1px 8px;
  border-radius: 10px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 12px;
}


.jefatura-tab.activa .jefatura-tab-contador {
  background: var(--sigta-mostaza);
  color: var(--sigta-azul-oscuro);
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
  grid-template-columns: 175px 1fr;
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


.resumen {
  margin: 7px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 14px;
  line-height: 1.45;
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
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-family: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}


.empty {
  padding: 34px;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
  color: var(--sigta-texto-suave);
  font-size: 16px;
  text-align: center;
}


/* =========================================================
   DETALLE DEL INFORME
========================================================= */

.informe-modal {
  max-width: 720px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}


.informe-header-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
}


.informe-header-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--sigta-mostaza-suave);
}


.informe-body {
  flex: 1;
  min-height: 0;
  padding: 16px 22px 18px;
  overflow-y: auto;
}


.informe-cabecera {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--sigta-azul-tenue);
  border-left: 5px solid var(--sigta-mostaza);
}


.informe-dato b {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-texto-suave);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.informe-dato strong {
  display: block;
  color: var(--sigta-azul-oscuro);
  font-size: 16px;
}


.ficha {
  margin: 0 0 14px;
}


.ficha > div {
  display: grid;
  grid-template-columns: 116px 1fr;
  gap: 14px;
  align-items: baseline;
  padding: 7px 0;
  border-top: 1px solid var(--sigta-azul-tenue);
}


.ficha > div:first-child {
  border-top: none;
}


.ficha dt {
  color: var(--sigta-texto-suave);
  font-size: 13px;
  font-weight: 700;
}


.ficha dd {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 15px;
  line-height: 1.45;
}


.informe-seccion {
  padding-top: 14px;
  border-top: 1px solid var(--sigta-azul-tenue);
}


.informe-titulo {
  display: block;
  margin-bottom: 8px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.informe-seccion p {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
}


.informe-acciones {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  padding: 12px 22px;
  border-top: 1px solid var(--sigta-azul-tenue);
  background: var(--sigta-blanco);
  border-radius: 0 0 14px 14px;
}


.btn-cerrar {
  min-height: 40px;
  padding: 0 20px;
  border: none;
  border-radius: 7px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
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


  .request {
    flex-direction: column;
    align-items: flex-start;
  }


  .request-main {
    grid-template-columns: 1fr;
  }


  .request-side {
    align-items: flex-start;
  }


  .informe-cabecera {
    grid-template-columns: 1fr;
  }

}

</style>
