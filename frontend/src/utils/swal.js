import Swal from 'sweetalert2'
import 'sweetalert2/dist/sweetalert2.min.css'

export const SigtaModal = Swal.mixin({
  confirmButtonColor: '#002A5C', // var(--sigta-azul)
  cancelButtonColor: '#d33',     // var(--sigta-error)
  allowOutsideClick: false
})

// Override nativo de alert para todo el sistema
window.alert = function(msg) {
  SigtaModal.fire({
    text: msg,
    icon: 'info',
    confirmButtonText: 'Aceptar'
  })
}

// Helpers asíncronos para reemplazar confirm y prompt
window.sigtaConfirm = async function(msg) {
  const res = await SigtaModal.fire({
    title: 'Confirmación',
    text: msg,
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, continuar',
    cancelButtonText: 'Cancelar'
  })
  return res.isConfirmed
}

window.sigtaPrompt = async function(msg, defaultText = '') {
  const res = await SigtaModal.fire({
    title: msg,
    input: 'text',
    inputValue: defaultText,
    showCancelButton: true,
    confirmButtonText: 'Aceptar',
    cancelButtonText: 'Cancelar'
  })
  return res.value // Será undefined si se cancela, o el string si se acepta
}
