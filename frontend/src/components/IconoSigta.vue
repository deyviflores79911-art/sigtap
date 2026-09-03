<template>
  <svg
    class="icono-sigta"
    :width="tamano"
    :height="tamano"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <g v-html="trazo"></g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

/* =========================================================
   ICONOS DEL SISTEMA

   Un solo juego de iconos de trazo, en el color que herede
   del menú. Sustituyen a los emoji de colores, que rompían
   la paleta institucional y daban aspecto improvisado.
========================================================= */

const props = defineProps({
  nombre: { type: String, required: true },
  tamano: { type: [Number, String], default: 19 },
})

const TRAZOS = {
  panel: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
  inicio: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M9.5 20v-6h5v6"/>',
  solicitudes: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8.5 8h7M8.5 12h7M8.5 16h4"/>',
  perfil: '<circle cx="12" cy="8" r="3.5"/><path d="M4.5 20c1.2-3.6 4-5.5 7.5-5.5s6.3 1.9 7.5 5.5"/>',
  configuracion: '<circle cx="12" cy="12" r="3"/><path d="M12 2v2.5M12 19.5V22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M2 12h2.5M19.5 12H22M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
  usuarios: '<circle cx="9" cy="8" r="3.2"/><path d="M2.5 20c1-3.2 3.5-5 6.5-5s5.5 1.8 6.5 5"/><path d="M16.5 5.2a3.2 3.2 0 0 1 0 5.6M18 15.2c2 .7 3.3 2.3 3.9 4.8"/>',
  roles: '<rect x="4.5" y="10" width="15" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15" r="1.4"/>',
  auditoria: '<path d="M6 3h9l4 4v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14.5 3v4.5H19"/><path d="M8.5 12.5h7M8.5 16.5h5"/>',
  compras: '<path d="M3 4h2.2l2.3 11.2a1.5 1.5 0 0 0 1.5 1.2h8.2a1.5 1.5 0 0 0 1.5-1.2L20.5 8H6"/><circle cx="9.5" cy="20" r="1.3"/><circle cx="17" cy="20" r="1.3"/>',
  almacen: '<path d="M3 9.5 12 4l9 5.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M8.5 21v-6.5h7V21"/>',
  soporte: '<rect x="2.5" y="4.5" width="19" height="12" rx="2"/><path d="M8.5 20.5h7M12 16.5v4"/>',
  mantenimiento: '<path d="M14.7 6.3a4.5 4.5 0 0 0 6 6l-2.6 2.6-6-6z"/><path d="M12.1 8.9 5 16a2.1 2.1 0 0 0 3 3l7.1-7.1"/>',
  tickets: '<path d="M3 8.5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2V10a2 2 0 0 0 0 4v1.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V14a2 2 0 0 0 0-4z"/><path d="M14 6.5v11"/>',
  portal: '<circle cx="12" cy="12" r="9"/><path d="M3.2 9.5h17.6M3.2 14.5h17.6"/><path d="M12 3c2.5 2.4 3.8 5.5 3.8 9s-1.3 6.6-3.8 9c-2.5-2.4-3.8-5.5-3.8-9S9.5 5.4 12 3z"/>',
  correo: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/>',
  salir: '<path d="M9.5 20H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3.5"/><path d="M15 8.5 19 12l-4 3.5"/><path d="M19 12H9.5"/>',
  notificaciones: '<path d="M6.5 10a5.5 5.5 0 0 1 11 0c0 4 1.5 5.5 1.5 5.5H5S6.5 14 6.5 10z"/><path d="M10 19a2.2 2.2 0 0 0 4 0"/>',
}

const trazo = computed(() => TRAZOS[props.nombre] || TRAZOS.panel)
</script>

<style scoped>
.icono-sigta {
  flex-shrink: 0;
  display: block;
}
</style>
