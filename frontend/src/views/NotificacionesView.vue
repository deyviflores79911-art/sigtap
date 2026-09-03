<template>
  <main class="page">

    <header>
      <div>
        <h1>Notificaciones</h1>
        <p>
          Acciones que requieren su intervención.
        </p>
      </div>

      <button
        @click="router.push('/usuario/dashboard')"
      >
        Volver
      </button>
    </header>

    <section class="card">

      <article
        v-for="notificacion in notificaciones"
        :key="notificacion.id"
      >
        <div class="dot"></div>

        <div>
          <strong>
            {{ notificacion.titulo }}
          </strong>

          <p>
            {{ notificacion.mensaje }}
          </p>

          <small>
            {{ notificacion.fecha }}
          </small>
        </div>
      </article>

      <div
        v-if="notificaciones.length === 0"
        class="empty"
      >
        No tiene notificaciones.
      </div>

    </section>

  </main>
</template>

<script setup>
import {
  onMounted,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'

const router = useRouter()

const notificaciones = ref([])


onMounted(async () => {

  const token =
    localStorage.getItem(
      'sigta_token'
    )

  try {

    const [
      soporteRes,
      comprasRes
    ] = await Promise.all([

      fetch(
        '/api/soporte/tickets/',
        {
          headers: {
            Authorization:
              `Token ${token}`
          }
        }
      ),

      fetch(
        '/api/compras/solicitudes/',
        {
          headers: {
            Authorization:
              `Token ${token}`
          }
        }
      ),
    ])


    const soporte =
      soporteRes.ok
        ? await soporteRes.json()
        : []

    const compras =
      comprasRes.ok
        ? await comprasRes.json()
        : []


    const soporteNotif =
      soporte
        .filter(ticket => (ticket.estado_codigo || ticket.estado) === 'PENDIENTE_CONFORMIDAD')
        .map(ticket => ({
        id: `S-${ticket.id}`,

        titulo:
          `${ticket.codigo} · Validación pendiente`,

        mensaje:
          `Confirme el buen funcionamiento o reporte que el problema continúa: ${ticket.titulo}`,

        fecha:
          new Date(
            ticket.actualizado_en
          ).toLocaleString('es-BO'),
      }))


    const comprasNotif =
      compras.filter(() => false).map(compra => ({
        id: `C-${compra.id}`,

        titulo:
          `${compra.codigo} · ${compra.estado_nombre}`,

        mensaje:
          compra.titulo,

        fecha:
          new Date(
            compra.actualizado_en
          ).toLocaleString('es-BO'),
      }))


    notificaciones.value = [
      ...soporteNotif,
      ...comprasNotif,
    ]

  } catch (e) {

    console.error(e)
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 30px;
  background: var(--sigta-azul-tenue);
  font-family: var(--sigta-fuente);
}

header {
  max-width: 850px;
  margin: auto auto 20px;
  display: flex;
  justify-content: space-between;
}

h1 {
  margin: 0;
  color: var(--sigta-texto);
}

header p {
  color: var(--sigta-texto-suave);
}

header button {
  border: none;
  background: var(--sigta-azul);
  color: white;
  padding: 0 18px;
  border-radius: 7px;
}

.card {
  max-width: 850px;
  margin: auto;
  background: white;
  border-radius: 10px;
  overflow: hidden;
}

article {
  display: flex;
  gap: 13px;
  padding: 18px;
  border-bottom: 1px solid var(--sigta-azul-tenue);
}

.dot {
  width: 10px;
  height: 10px;
  margin-top: 5px;
  border-radius: 50%;
  background: var(--sigta-mostaza);
}

article strong {
  color: var(--sigta-texto);
}

article p {
  margin: 5px 0;
  color: var(--sigta-texto-suave);
  font-size: 12px;
}

article small {
  color: var(--sigta-texto-suave);
}

.empty {
  padding: 40px;
  text-align: center;
}
</style>
