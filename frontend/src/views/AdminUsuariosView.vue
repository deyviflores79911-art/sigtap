<template>

  <div class="admin-layout">

    <!-- =====================================================
         MENÚ ÚNICO DEL ADMINISTRADOR
    ====================================================== -->

    <SuperuserMenu />


    <!-- =====================================================
         CONTENIDO
    ====================================================== -->

    <main class="main-content">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="topbar">

        <div>

          <h1>
            Gestión de Usuarios
          </h1>

          <p>
            Alta, consulta, modificación, activación
            e inactivación de usuarios.
          </p>

        </div>


        <button
          class="btn-primary"
          @click="abrirNuevo"
        >
          + Nuevo usuario
        </button>

      </header>


      <!-- =================================================
           RESUMEN
      ================================================== -->

      <section class="stats-grid">

        <article class="stat-card">

          <span>
            Total usuarios
          </span>

          <strong>
            {{ usuarios.length }}
          </strong>

          <small>
            Registrados en SIGTA
          </small>

        </article>


        <article class="stat-card">

          <span>
            Usuarios activos
          </span>

          <strong>
            {{ cantidadActivos }}
          </strong>

          <small>
            Con acceso habilitado
          </small>

        </article>


        <article class="stat-card">

          <span>
            Usuarios inactivos
          </span>

          <strong>
            {{ cantidadInactivos }}
          </strong>

          <small>
            Sin acceso al sistema
          </small>

        </article>


        <article class="stat-card">

          <span>
            Primer ingreso pendiente
          </span>

          <strong>
            {{ cantidadPrimerIngreso }}
          </strong>

          <small>
            Deben cambiar contraseña
          </small>

        </article>

      </section>


      <!-- =================================================
           FILTROS
      ================================================== -->

      <section class="filters-card">

        <div class="search-box">

          <label>
            Buscar usuario
          </label>

          <input
            v-model="busqueda"
            type="text"
            placeholder="Nombre o correo institucional..."
          />

        </div>


        <div class="filter-box">

          <label>
            Estado
          </label>

          <select
            v-model="filtroEstado"
          >

            <option value="">
              Todos los estados
            </option>

            <option value="activo">
              Activos
            </option>

            <option value="inactivo">
              Inactivos
            </option>

          </select>

        </div>

      </section>


      <!-- =================================================
           MENSAJE GENERAL
      ================================================== -->

      <div
        v-if="mensaje"
        :class="[
          'alert',
          error
            ? 'error'
            : 'success'
        ]"
      >
        {{ mensaje }}
      </div>


      <!-- =================================================
           TABLA
      ================================================== -->

      <section class="table-card">

        <div class="table-header">

          <div>

            <h2>
              Usuarios registrados
            </h2>

            <p>
              Administre las cuentas y permisos
              institucionales.
            </p>

          </div>


          <span class="result-count">
            {{ usuariosFiltrados.length }}
            resultado(s)
          </span>

        </div>


        <div
          v-if="cargando"
          class="loading"
        >
          Cargando usuarios...
        </div>


        <div
          v-else-if="
            usuariosFiltrados.length === 0
          "
          class="empty"
        >
          No se encontraron usuarios.
        </div>


        <div
          v-else
          class="table-wrapper"
        >

          <table>

            <thead>

              <tr>

                <th class="id-column">
                  ID
                </th>

                <th>
                  Usuario
                </th>

                <th>
                  Correo
                </th>

                <th>
                  Rol
                </th>

                <th>
                  Área
                </th>

                <th>
                  Estado
                </th>

                <th>
                  Primer ingreso
                </th>

                <th>
                  Acciones
                </th>

              </tr>

            </thead>


            <tbody>

              <tr
                v-for="usuario in usuariosFiltrados"
                :key="usuario.id"
              >

                <!-- ID -->
                <td class="id-column">
                  {{ usuario.id }}
                </td>

                <!-- USUARIO -->
                <td>

                  <div class="user-cell">

                    <div class="table-avatar">

                      {{
                        obtenerIniciales(
                          usuario.nombre_completo
                        )
                      }}

                    </div>


                    <div>

                      <strong>
                        {{ usuario.nombre_completo }}
                      </strong>

                    </div>

                  </div>

                </td>


                <!-- CORREO -->
                <td>

                  {{ usuario.email }}

                </td>


                <!-- ROL -->
                <td>

                  <span class="role-badge">

                    {{
                      usuario.roles?.[0]?.rol_nombre
                      || 'Sin rol'
                    }}

                  </span>

                </td>


                <!-- ÁREA -->
                <td>

                  {{
                    usuario.roles?.[0]?.area_nombre
                    || 'Global'
                  }}

                </td>


                <!-- ESTADO -->
                <td>

                  <span
                    :class="[
                      'badge',
                      usuario.is_active
                        ? 'activo'
                        : 'inactivo'
                    ]"
                  >

                    {{
                      usuario.is_active
                        ? 'Activo'
                        : 'Inactivo'
                    }}

                  </span>

                </td>


                <!-- PRIMER INGRESO -->
                <td>

                  <span
                    :class="[
                      'first-login',
                      usuario.must_change_password
                        ? 'pending'
                        : 'completed'
                    ]"
                  >

                    {{
                      usuario.must_change_password
                        ? 'Pendiente'
                        : 'Completado'
                    }}

                  </span>

                </td>


                <!-- ACCIONES -->
                <td>

                  <div class="actions">

                    <button
                      class="btn-edit"
                      @click="
                        editarUsuario(
                          usuario
                        )
                      "
                    >
                      Editar
                    </button>

                    <button
                      class="btn-reset-password"
                      @click="abrirRestablecerPassword(usuario)"
                    >
                      Restablecer contraseña
                    </button>


                    <button
                      v-if="usuario.is_active"
                      class="btn-disable"
                      @click="
                        solicitarCambioEstado(usuario, 'inactivar')
                      "
                    >
                      Inactivar
                    </button>


                    <button
                      v-else
                      class="btn-enable"
                      @click="
                        solicitarCambioEstado(usuario, 'activar')
                      "
                    >
                      Activar
                    </button>

                  </div>

                </td>

              </tr>

            </tbody>

          </table>

        </div>

      </section>


      <!-- =================================================
           MODAL
      ================================================== -->

      <div
        v-if="mostrarModal"
        class="modal-overlay"
        @click.self="cerrarModal"
      >

        <div class="modal">

          <!-- ENCABEZADO MODAL -->

          <div class="modal-header">

            <div>

              <span class="modal-kicker">
                Administración de identidad
              </span>

              <h2>

                {{
                  editando
                    ? 'Editar usuario'
                    : 'Nuevo usuario'
                }}

              </h2>


              <p>

                {{
                  editando
                    ? 'Modifique los datos permitidos del usuario.'
                    : 'Registre una nueva cuenta institucional en SIGTA.'
                }}

              </p>

            </div>


            <button
              type="button"
              class="close"
              @click="cerrarModal"
            >
              ×
            </button>

          </div>


          <!-- FORMULARIO -->

          <form
            @submit.prevent="guardarUsuario"
          >

            <div class="grid">

              <!-- NOMBRE -->

              <div v-if="editando" class="field full">

                <label>
                  Nombre completo
                  <span>*</span>
                </label>

                <input
                  v-model="form.nombre_completo"
                  type="text"
                  placeholder="Ej.: Juan Carlos Pérez"
                  required
                />

              </div>

              <template v-else>
                <div class="field">
                  <label>Primer nombre <span>*</span></label>
                  <input v-model="form.primer_nombre" type="text" placeholder="Ej.: Wendy" required :disabled="usuarioCreado" />
                </div>
                <div class="field">
                  <label>Segundo nombre</label>
                  <input v-model="form.segundo_nombre" type="text" placeholder="Ej.: Roxana" :disabled="usuarioCreado" />
                </div>
                <div class="field">
                  <label>Apellido paterno <span>*</span></label>
                  <input v-model="form.apellido_paterno" type="text" placeholder="Ej.: Caillavi" required :disabled="usuarioCreado" />
                </div>
                <div class="field">
                  <label>Apellido materno <span>*</span></label>
                  <input v-model="form.apellido_materno" type="text" placeholder="Ej.: Reyes" required :disabled="usuarioCreado" />
                </div>
              </template>


              <!-- EMAIL -->

              <div class="field full">

                <label>
                  Correo institucional
                  <span>*</span>
                </label>

                <input
                  :value="correoGenerado"
                  type="email"
                  placeholder="usuario@emi.edu.bo"
                  readonly
                  required
                />

                <small>
                  Se utilizará para iniciar sesión
                  y recibir notificaciones.
                </small>

              </div>


              <!-- ROL -->

              <div class="field">

                <label>
                  Rol
                  <span>*</span>
                </label>

                <select
                  v-model="form.tipo_usuario"
                  required
                  @change="cambioRol"
                >

                  <option
                    value=""
                    disabled
                  >
                    Seleccione tipo
                  </option>


                  <option value="JEFE">Jefe</option>
                  <option value="TECNICO">Técnico</option>
                  <option value="DIRECTOR">Director</option>
                  <option value="USUARIO">Usuario</option>
                  <option value="SUPERUSER">Superuser</option>

                </select>

              </div>


              <!-- ÁREA -->

              <div v-if="requiereArea" class="field">

                <label>
                  Área
                  <span>*</span>
                </label>


                <select
                  v-model="form.area_id"
                  required
                  @change="form.especialidad = ''"
                >

                  <option value="">

                    Seleccione área

                  </option>


                  <option
                    v-for="area in areasFormulario"
                    :key="area.id"
                    :value="area.id"
                  >
                    {{ area.nombre }}
                  </option>

                </select>


              </div>

              <div v-if="form.tipo_usuario === 'TECNICO' && form.area_id" class="field">
                <label>Especialidad <span>*</span></label>
                <select v-model="form.especialidad" required>
                  <option value="" disabled>Seleccione especialidad</option>
                  <option v-for="opcion in especialidadesDisponibles" :key="opcion.valor" :value="opcion.valor">
                    {{ opcion.nombre }}
                  </option>
                </select>
              </div>


              <!-- CONTRASEÑA -->

              <div class="field full">

                <label>

                  {{
                    editando
                      ? 'Nueva contraseña temporal'
                      : 'Contraseña temporal'
                  }}

                  <span
                    v-if="
                      !editando
                    "
                  >
                    *
                  </span>

                </label>


                <div class="password-field">
                  <input
                    v-model="form.password"
                    :type="mostrarPassword ? 'text' : 'password'"
                    readonly
                    :placeholder="editando ? 'No se modifica desde esta pantalla' : '••••••••••'"
                  />
                  <button
                    v-if="!editando"
                    type="button"
                    class="password-eye"
                    :disabled="!form.password"
                    :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    :title="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    @click="mostrarPassword = !mostrarPassword"
                  >👁</button>
                </div>


                <small>

                  {{
                    editando
                      ? 'Déjelo vacío si no desea cambiar la contraseña.'
                      : (form.password
                          ? 'Copie esta contraseña ahora: no podrá consultarse posteriormente.'
                          : 'Se generará automáticamente al crear el usuario.')
                  }}

                </small>

              </div>

            </div>


            <!-- ERROR MODAL -->

            <div
              v-if="mensajeModal"
              :class="usuarioCreado ? 'modal-success' : 'modal-error'"
            >
              {{ mensajeModal }}
            </div>


            <!-- ACCIONES MODAL -->

            <div class="modal-actions">

              <button
                type="button"
                class="btn-cancel"
                @click="cerrarModal"
              >
                {{ usuarioCreado ? 'Cerrar' : 'Cancelar' }}
              </button>


              <button
                v-if="!usuarioCreado"
                type="submit"
                class="btn-save"
                :disabled="guardando"
              >

                {{
                  guardando
                    ? 'Guardando...'
                    : (
                        editando
                          ? 'Guardar cambios'
                          : 'Crear usuario'
                      )
                }}

              </button>

            </div>

          </form>

        </div>

      </div>

      <div
        v-if="usuarioConfirmacion"
        class="modal-overlay"
        @click.self="cerrarConfirmacion"
      >
        <div class="modal confirm-modal">
          <div class="confirm-icon" :class="accionConfirmacion">!</div>
          <h2>{{ accionConfirmacion === 'inactivar' ? 'Inactivar usuario' : 'Activar usuario' }}</h2>
          <p>
            {{ accionConfirmacion === 'inactivar'
              ? '¿Está seguro de que desea inactivar a este usuario?'
              : '¿Está seguro de que desea activar nuevamente a este usuario?' }}
          </p>
          <dl class="confirm-user-data">
            <div><dt>Nombre:</dt><dd>{{ usuarioConfirmacion.nombre_completo }}</dd></div>
            <div><dt>Correo:</dt><dd>{{ usuarioConfirmacion.email }}</dd></div>
            <div><dt>Rol:</dt><dd>{{ usuarioConfirmacion.roles?.[0]?.rol_nombre || 'Sin rol' }}</dd></div>
          </dl>
          <div class="confirm-warning" :class="accionConfirmacion">
            {{ accionConfirmacion === 'inactivar'
              ? 'El usuario no podrá acceder a SIGTA mientras se encuentre inactivo.'
              : 'El usuario recuperará el acceso a SIGTA.' }}
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" :disabled="procesandoEstado" @click="cerrarConfirmacion">Cancelar</button>
            <button
              type="button"
              :class="accionConfirmacion === 'inactivar' ? 'btn-confirm-disable' : 'btn-confirm-enable'"
              :disabled="procesandoEstado"
              @click="confirmarCambioEstado"
            >
              {{ procesandoEstado
                ? 'Procesando...'
                : (accionConfirmacion === 'inactivar' ? 'Inactivar usuario' : 'Activar usuario') }}
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="usuarioRestablecimiento && !passwordRestablecida"
        class="modal-overlay"
        @click.self="cerrarRestablecimiento"
      >
        <div class="modal confirm-modal">
          <div class="confirm-icon reset-password">!</div>
          <h2>Restablecer contraseña</h2>
          <p>¿Está seguro de que desea restablecer la contraseña de este usuario?</p>
          <dl class="confirm-user-data">
            <div><dt>Usuario:</dt><dd>{{ usuarioRestablecimiento.nombre_completo }}</dd></div>
            <div><dt>Correo:</dt><dd>{{ usuarioRestablecimiento.email }}</dd></div>
          </dl>
          <div class="confirm-warning">
            La contraseña actual dejará de funcionar. Se generará una nueva contraseña temporal y el usuario deberá cambiarla en su próximo inicio de sesión.
          </div>
          <div v-if="errorRestablecimiento" class="modal-error">
            {{ errorRestablecimiento }}
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" :disabled="restableciendoPassword" @click="cerrarRestablecimiento">
              Cancelar
            </button>
            <button type="button" class="btn-confirm-reset" :disabled="restableciendoPassword" @click="confirmarRestablecimiento">
              {{ restableciendoPassword ? 'Restableciendo...' : 'Restablecer contraseña' }}
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="usuarioRestablecimiento && passwordRestablecida"
        class="modal-overlay"
      >
        <div class="modal generated-password-modal">
          <div class="confirm-icon activar">✓</div>
          <h2>Contraseña temporal generada</h2>
          <dl class="confirm-user-data">
            <div><dt>Usuario:</dt><dd>{{ usuarioRestablecimiento.nombre_completo }}</dd></div>
            <div><dt>Correo:</dt><dd>{{ usuarioRestablecimiento.email }}</dd></div>
          </dl>
          <div class="field full">
            <label>Contraseña temporal</label>
            <div class="password-field">
              <input
                :value="passwordRestablecida"
                :type="mostrarPasswordRestablecida ? 'text' : 'password'"
                readonly
              />
              <button
                type="button"
                class="password-eye"
                :aria-label="mostrarPasswordRestablecida ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                :title="mostrarPasswordRestablecida ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                @click="mostrarPasswordRestablecida = !mostrarPasswordRestablecida"
              >👁</button>
            </div>
          </div>
          <div class="one-time-notice">
            <strong>Esta contraseña temporal se mostrará únicamente en este momento.</strong>
            <span>El usuario deberá cambiarla al iniciar sesión nuevamente.</span>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-save" @click="cerrarRestablecimiento">Entendido</button>
          </div>
        </div>
      </div>

    </main>

  </div>

</template>


<script setup>

import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  useRouter
} from 'vue-router'


/* =========================================================
   COMPONENTE MENÚ
========================================================= */

import SuperuserMenu
  from '../components/SuperuserMenu.vue'


const router =
  useRouter()


/* =========================================================
   DATOS
========================================================= */

const usuarios =
  ref([])

const roles =
  ref([])

const areas =
  ref([])


/* =========================================================
   ESTADOS
========================================================= */

const cargando =
  ref(true)

const guardando =
  ref(false)

const mostrarModal =
  ref(false)

const editando =
  ref(false)

const usuarioEditandoId =
  ref(null)

const busqueda =
  ref('')

const filtroEstado =
  ref('')

const mensaje =
  ref('')

const mensajeModal =
  ref('')

const error =
  ref(false)

const mostrarPassword = ref(false)
const usuarioCreado = ref(false)
const usuarioConfirmacion = ref(null)
const accionConfirmacion = ref('')
const procesandoEstado = ref(false)
const usuarioRestablecimiento = ref(null)
const passwordRestablecida = ref('')
const mostrarPasswordRestablecida = ref(false)
const restableciendoPassword = ref(false)
const errorRestablecimiento = ref('')


/* =========================================================
   FORMULARIO
========================================================= */

const form =
  reactive({

    nombre_completo: '',

    primer_nombre: '',

    segundo_nombre: '',

    apellido_paterno: '',

    apellido_materno: '',

    email: '',

    password: '',

    tipo_usuario: '',

    rol_id: '',

    area_id: '',

    especialidad: '',
  })

function normalizarParteCorreo(valor) {
  return String(valor || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
}

const correoGenerado = computed(() => {
  if (editando.value) return form.email
  const primero = normalizarParteCorreo(form.primer_nombre)
  const paterno = normalizarParteCorreo(form.apellido_paterno)
  const materno = normalizarParteCorreo(form.apellido_materno)
  if (!primero || !paterno || !materno) return ''
  return `${primero[0]}${paterno}${materno[0]}@emi.edu.bo`
})


/* =========================================================
   TOKEN
========================================================= */

const token = () =>
  localStorage.getItem(
    'sigta_token'
  )


/* =========================================================
   HEADERS
========================================================= */

const headers = () => ({

  'Content-Type':
    'application/json',

  Accept:
    'application/json',

  Authorization:
    `Token ${token()}`,
})


const headersLectura = () => ({

  Accept:
    'application/json',

  Authorization:
    `Token ${token()}`,
})


/* =========================================================
   CONTADORES
========================================================= */

const cantidadActivos =
  computed(() => {

    return usuarios.value.filter(
      usuario =>
        usuario.is_active
    ).length
  })


const cantidadInactivos =
  computed(() => {

    return usuarios.value.filter(
      usuario =>
        !usuario.is_active
    ).length
  })


const cantidadPrimerIngreso =
  computed(() => {

    return usuarios.value.filter(
      usuario =>
        usuario.must_change_password
    ).length
  })


/* =========================================================
   FILTRADO
========================================================= */

const usuariosFiltrados =
  computed(() => {

    const texto =
      busqueda.value
        .toLowerCase()
        .trim()


    return usuarios.value.filter(
      usuario => {

        const coincideTexto =

          !texto

          ||

          usuario.nombre_completo
            ?.toLowerCase()
            .includes(texto)

          ||

          usuario.email
            ?.toLowerCase()
            .includes(texto)


        const coincideEstado =

          !filtroEstado.value

          ||

          (
            filtroEstado.value
            === 'activo'

            &&
            usuario.is_active
          )

          ||

          (
            filtroEstado.value
            === 'inactivo'

            &&
            !usuario.is_active
          )


        return (
          coincideTexto
          &&
          coincideEstado
        )
      }
    )
  })


/* =========================================================
   ROL GLOBAL
========================================================= */

const requiereArea = computed(() => ['JEFE', 'TECNICO'].includes(form.tipo_usuario))

const areasFormulario = computed(() => {
  const oficiales = ['DAF', 'MANTENIMIENTO', 'UTIC']
  return areas.value.filter(area => oficiales.includes(String(area.codigo).toUpperCase()))
})

const areaSeleccionada = computed(() =>
  areas.value.find(area => Number(area.id) === Number(form.area_id))
)

const especialidadesDisponibles = computed(() => {
  const codigo = String(areaSeleccionada.value?.codigo || '').toUpperCase()
  if (codigo === 'UTIC') return [
    { valor: 'REDES', nombre: 'Redes' },
    { valor: 'HARDWARE_COMPUTADORAS', nombre: 'Hardware y computadoras' },
    { valor: 'SISTEMAS_CENTRALIZADOS_DATOS', nombre: 'Sistemas centralizados y datos' },
    { valor: 'EQUIPOS_AUXILIARES', nombre: 'Equipos auxiliares' },
  ]
  if (codigo === 'MANTENIMIENTO') return [
    { valor: 'CHOFER', nombre: 'Chofer' },
    { valor: 'TECNICO_MANTENIMIENTO', nombre: 'Técnico' },
  ]
  if (codigo === 'DAF') return [
    { valor: 'TECNICO_DAF', nombre: 'Técnico de la DAF' },
    { valor: 'ALMACEN_COMPRAS', nombre: 'Técnico de Almacén y Compras' },
    { valor: 'TESORERIA', nombre: 'Técnico de Tesorería' },
  ]
  return []
})

function codigoRolInterno() {
  if (form.tipo_usuario === 'SUPERUSER') return 'SUPERUSER'
  if (form.tipo_usuario === 'DIRECTOR') return 'ADMIN'
  if (form.tipo_usuario === 'USUARIO') return 'SOLICITANTE'
  const area = String(areaSeleccionada.value?.codigo || '').toUpperCase()
  if (form.tipo_usuario === 'JEFE') {
    return { UTIC: 'JEFE_UTIC', MANTENIMIENTO: 'SERVICIOS_GENERALES' }[area]
  }
  if (form.tipo_usuario === 'TECNICO') {
    if (area === 'UTIC') return 'ESPECIALISTA'
    if (area === 'MANTENIMIENTO') return 'AUXILIAR_SERVICIOS_GENERALES'
    return { TECNICO_DAF: 'DAF', ALMACEN_COMPRAS: 'ENCARGADO_COMPRAS_ALMACEN', TESORERIA: 'TESORERIA' }[form.especialidad]
  }
  return ''
}


/* =========================================================
   AL MONTAR
========================================================= */

onMounted(
  async () => {

    if (!token()) {

      router.push(
        '/login'
      )

      return
    }


    await cargarDatos()
  }
)


/* =========================================================
   NORMALIZAR RESPUESTAS
========================================================= */

function convertirLista(
  datos
) {

  if (
    Array.isArray(datos)
  ) {

    return datos
  }


  if (
    Array.isArray(
      datos?.results
    )
  ) {

    return datos.results
  }


  return []
}


/* =========================================================
   CARGAR USUARIOS, ROLES Y ÁREAS
========================================================= */

async function cargarDatos() {

  cargando.value =
    true


  try {

    const [
      usuariosRespuesta,
      rolesRespuesta,
      areasRespuesta,
    ] = await Promise.all([


      /* USUARIOS */

      fetch(
        '/api/usuarios/usuarios/',
        {
          headers:
            headersLectura(),
        }
      ),


      /* ROLES
         CORREGIDO:
         ahora también manda token
      */

      fetch(
        '/api/usuarios/roles/',
        {
          headers:
            headersLectura(),
        }
      ),


      /* ÁREAS
         CORREGIDO:
         ahora también manda token
      */

      fetch(
        '/api/usuarios/areas/',
        {
          headers:
            headersLectura(),
        }
      ),

    ])


    /* ===============================================
       VALIDAR SESIÓN
    ================================================ */

    const respuestas = [

      usuariosRespuesta,

      rolesRespuesta,

      areasRespuesta,
    ]


    const sinPermiso =
      respuestas.some(
        respuesta =>
          respuesta.status === 401
          ||
          respuesta.status === 403
      )


    if (sinPermiso) {

      cerrarSesion()

      return
    }


    /* ===============================================
       VALIDAR ERRORES
    ================================================ */

    if (!usuariosRespuesta.ok) {

      throw new Error(
        'No se pudieron cargar los usuarios.'
      )
    }


    if (!rolesRespuesta.ok) {

      throw new Error(
        'No se pudieron cargar los roles.'
      )
    }


    if (!areasRespuesta.ok) {

      throw new Error(
        'No se pudieron cargar las áreas.'
      )
    }


    /* ===============================================
       LEER JSON
    ================================================ */

    const datosUsuarios =
      await usuariosRespuesta.json()


    const datosRoles =
      await rolesRespuesta.json()


    const datosAreas =
      await areasRespuesta.json()


    /* ===============================================
       GUARDAR
    ================================================ */

    usuarios.value =
      convertirLista(
        datosUsuarios
      )


    roles.value =
      convertirLista(
        datosRoles
      )


    areas.value =
      convertirLista(
        datosAreas
      )


    console.log(
      'Usuarios:',
      usuarios.value
    )


    console.log(
      'Roles:',
      roles.value
    )


    console.log(
      'Áreas:',
      areas.value
    )


  } catch (e) {

    console.error(
      'Error cargando usuarios:',
      e
    )


    mostrarMensaje(
      e.message
      ||
      'No se pudieron cargar los datos.',
      true
    )

  } finally {

    cargando.value =
      false
  }
}


/* =========================================================
   NUEVO USUARIO
========================================================= */

function abrirNuevo() {

  editando.value =
    false

  usuarioEditandoId.value =
    null

  limpiarFormulario()

  form.password = 'Temporal2026*'

  mostrarModal.value =
    true
}


/* =========================================================
   EDITAR USUARIO
========================================================= */

function editarUsuario(
  usuario
) {

  editando.value =
    true


  usuarioEditandoId.value =
    usuario.id


  form.nombre_completo =
    usuario.nombre_completo
    || ''


  form.email =
    usuario.email
    || ''


  form.password = ''


  /*
   * Se convierte a Number para que
   * coincida correctamente con:
   *
   * :value="rol.id"
   */

  form.rol_id =
    usuario.roles?.[0]?.rol_id
      ? Number(
          usuario.roles[0].rol_id
        )
      : ''

  const asignacion = usuario.roles?.[0] || {}
  const codigoRol = asignacion.rol_codigo
  const mapaTipo = {
    SUPERUSER: 'SUPERUSER', ADMIN: 'DIRECTOR', DIRECTOR: 'DIRECTOR', SOLICITANTE: 'USUARIO',
    JEFE_UTIC: 'JEFE', SERVICIOS_GENERALES: 'JEFE',
    ESPECIALISTA: 'TECNICO', AUXILIAR_SERVICIOS_GENERALES: 'TECNICO', DAF: 'TECNICO',
    ENCARGADO_COMPRAS_ALMACEN: 'TECNICO', TESORERIA: 'TECNICO',
  }
  form.tipo_usuario = mapaTipo[codigoRol] || ''


  /*
   * Igual para Área.
   */

  form.area_id =
    usuario.roles?.[0]?.area_id
      ? Number(
          usuario.roles[0].area_id
        )
      : ''

  if (!form.area_id) {
    const codigoArea = {
      JEFE_UTIC: 'UTIC', ESPECIALISTA: 'UTIC',
      DAF: 'DAF', ENCARGADO_COMPRAS_ALMACEN: 'DAF', TESORERIA: 'DAF',
      SERVICIOS_GENERALES: 'MANTENIMIENTO', AUXILIAR_SERVICIOS_GENERALES: 'MANTENIMIENTO',
    }[codigoRol]
    form.area_id = areas.value.find(area => area.codigo === codigoArea)?.id || ''
  }

  form.especialidad = asignacion.especialidad || ({
    DAF: 'TECNICO_DAF', ENCARGADO_COMPRAS_ALMACEN: 'ALMACEN_COMPRAS', TESORERIA: 'TESORERIA',
    AUXILIAR_SERVICIOS_GENERALES: 'TECNICO_MANTENIMIENTO',
  }[codigoRol] || '')


  mensajeModal.value =
    ''


  mostrarModal.value =
    true
}


/* =========================================================
   LIMPIAR
========================================================= */

function limpiarFormulario() {

  form.nombre_completo = ''

  form.primer_nombre = ''

  form.segundo_nombre = ''

  form.apellido_paterno = ''

  form.apellido_materno = ''

  form.email = ''

  form.password = ''

  form.tipo_usuario = ''

  form.rol_id = ''

  form.area_id = ''

  form.especialidad = ''

  mensajeModal.value = ''

  mostrarPassword.value = false

  usuarioCreado.value = false
}


/* =========================================================
   CERRAR MODAL
========================================================= */

function cerrarModal() {

  mostrarModal.value =
    false

  limpiarFormulario()
}


/* =========================================================
   CAMBIO DE ROL
========================================================= */

function cambioRol() {
  form.rol_id = ''
  form.especialidad = ''
  if (!requiereArea.value) {
    form.area_id = ''
  }
}


/* =========================================================
   GUARDAR USUARIO
========================================================= */

async function guardarUsuario() {

  mensajeModal.value = ''


  /* ===============================================
     CAMPOS OBLIGATORIOS
  ================================================ */

  if (
    (editando.value
      ? !form.nombre_completo.trim()
      : (!form.primer_nombre.trim()
          || !form.apellido_paterno.trim()
          || !form.apellido_materno.trim()))
    ||
    !form.tipo_usuario
  ) {

    mensajeModal.value =
      'Complete los campos obligatorios.'

    return
  }

  if (
    form.tipo_usuario === 'JEFE'
    &&
    String(areaSeleccionada.value?.codigo || '').toUpperCase() === 'DAF'
  ) {

    mensajeModal.value =
      'La DAF no tiene jefatura: la solicitud de compra llega directamente a la DAF.'

    return
  }


  /* ===============================================
     CORREO EMI
  ================================================ */

  if (
    !correoGenerado.value.endsWith('@emi.edu.bo')
  ) {

    mensajeModal.value =
      'Ingrese un correo institucional @emi.edu.bo.'

    return
  }


  /* ===============================================
     ÁREA OBLIGATORIA
  ================================================ */

  if (
    requiereArea.value
    &&
    !form.area_id
  ) {

    mensajeModal.value =
      'Seleccione el área del usuario.'

    return
  }

  if (form.tipo_usuario === 'TECNICO' && !form.especialidad) {
    mensajeModal.value = 'Seleccione la especialidad del técnico.'
    return
  }


  guardando.value =
    true


  try {

    const codigoRol = codigoRolInterno()
    const rolInterno = roles.value.find(rol => rol.codigo === codigoRol)
    if (!rolInterno) {
      mensajeModal.value = 'No se encontró el rol interno para la selección realizada.'
      return
    }

    const payload = {

      nombre_completo:
        editando.value
          ? form.nombre_completo.trim()
          : [
              form.primer_nombre,
              form.segundo_nombre,
              form.apellido_paterno,
              form.apellido_materno,
            ]
              .map(valor => valor.trim())
              .filter(Boolean)
              .join(' '),

      email:
        correoGenerado.value,

      rol_id: Number(rolInterno.id),

      area_id:
        form.area_id
          ? Number(form.area_id)
          : null,

      especialidad: form.especialidad || '',
    }

    if (!editando.value) {
      payload.primer_nombre = form.primer_nombre.trim()
      payload.segundo_nombre = form.segundo_nombre.trim()
      payload.apellido_paterno = form.apellido_paterno.trim()
      payload.apellido_materno = form.apellido_materno.trim()
      payload.password = form.password
    }


    /*
     * La contraseña solamente se manda
     * si se escribió una.
     */

    if (editando.value && form.password) {

      payload.password =
        form.password
    }


    let url =
      '/api/usuarios/usuarios/'


    let method =
      'POST'


    if (
      editando.value
    ) {

      url =
        `/api/usuarios/usuarios/${usuarioEditandoId.value}/`


      method =
        'PATCH'
    }


    const respuesta =
      await fetch(
        url,
        {
          method,

          headers:
            headers(),

          body:
            JSON.stringify(
              payload
            ),
        }
      )


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      console.error(
        'Error guardando usuario:',
        datos
      )


      mensajeModal.value =
        obtenerError(
          datos
        )


      return
    }


    const eraEdicion =
      editando.value


    if (eraEdicion) {
      cerrarModal()
      mostrarMensaje('Usuario actualizado correctamente.')
    } else {
      form.password = datos.password_temporal || ''
      usuarioCreado.value = true
      mensajeModal.value = 'Usuario creado correctamente.'
      mostrarMensaje('Usuario creado correctamente.')
    }

    await cargarDatos()


  } catch (e) {

    console.error(
      'Error guardando usuario:',
      e
    )


    mensajeModal.value =
      'No fue posible guardar el usuario.'

  } finally {

    guardando.value =
      false
  }
}


/* =========================================================
   INACTIVAR
========================================================= */

async function inactivarUsuario(
  usuario
) {
  try {

    const respuesta =
      await fetch(
        `/api/usuarios/usuarios/${usuario.id}/`,
        {

          method:
            'DELETE',

          headers:
            headers(),
        }
      )


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      mostrarMensaje(
        datos.detalle
        ||
        datos.detail
        ||
        'No se pudo inactivar el usuario.',
        true
      )


      return false
    }


    mostrarMensaje(
      'Usuario inactivado correctamente.'
    )


    await cargarDatos()

    return true


  } catch (e) {

    console.error(
      e
    )


    mostrarMensaje(
      'Error al inactivar el usuario.',
      true
    )
    return false
  }
}

function solicitarCambioEstado(usuario, accion) {
  usuarioConfirmacion.value = usuario
  accionConfirmacion.value = accion
}

function cerrarConfirmacion() {
  if (procesandoEstado.value) return
  usuarioConfirmacion.value = null
  accionConfirmacion.value = ''
}

async function confirmarCambioEstado() {
  if (!usuarioConfirmacion.value) return
  procesandoEstado.value = true
  const usuario = usuarioConfirmacion.value
  const accion = accionConfirmacion.value
  try {
    const completado = accion === 'inactivar'
      ? await inactivarUsuario(usuario)
      : await activarUsuario(usuario)
    if (completado) {
      usuarioConfirmacion.value = null
      accionConfirmacion.value = ''
    }
  } finally {
    procesandoEstado.value = false
  }
}


/* =========================================================
   ACTIVAR
========================================================= */

async function activarUsuario(
  usuario
) {

  try {

    const respuesta =
      await fetch(
        `/api/usuarios/usuarios/${usuario.id}/activar/`,
        {

          method:
            'POST',

          headers:
            headers(),

          body:
            JSON.stringify({}),
        }
      )


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      mostrarMensaje(
        datos.detalle
        ||
        datos.detail
        ||
        'No se pudo activar el usuario.',
        true
      )


      return false
    }


    mostrarMensaje(
      'Usuario activado correctamente.'
    )


    await cargarDatos()

    return true


  } catch (e) {

    console.error(
      e
    )


    mostrarMensaje(
      'Error al activar el usuario.',
      true
    )
    return false
  }
}


/* =========================================================
   RESTABLECER CONTRASEÑA
========================================================= */

function abrirRestablecerPassword(usuario) {
  usuarioRestablecimiento.value = usuario
  passwordRestablecida.value = ''
  mostrarPasswordRestablecida.value = false
  errorRestablecimiento.value = ''
}

function cerrarRestablecimiento() {
  if (restableciendoPassword.value) return
  usuarioRestablecimiento.value = null
  passwordRestablecida.value = ''
  mostrarPasswordRestablecida.value = false
  errorRestablecimiento.value = ''
}

async function confirmarRestablecimiento() {
  if (!usuarioRestablecimiento.value) return

  restableciendoPassword.value = true
  errorRestablecimiento.value = ''

  try {
    const respuesta = await fetch(
      `/api/usuarios/usuarios/${usuarioRestablecimiento.value.id}/restablecer-password/`,
      {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({}),
      }
    )

    let datos = {}
    try {
      datos = await respuesta.json()
    } catch {
      datos = {}
    }

    if (!respuesta.ok || !datos.password_temporal) {
      errorRestablecimiento.value =
        respuesta.status === 401 || respuesta.status === 403
          ? 'No tiene autorización para restablecer esta contraseña.'
          : 'No fue posible restablecer la contraseña. Intente nuevamente.'
      return
    }

    passwordRestablecida.value = datos.password_temporal
    await cargarDatos()
  } catch (error) {
    console.error('Error restableciendo contraseña:', error)
    errorRestablecimiento.value =
      'No fue posible restablecer la contraseña. Intente nuevamente.'
  } finally {
    restableciendoPassword.value = false
  }
}


/* =========================================================
   ERRORES DEL BACKEND
========================================================= */

function obtenerError(
  datos
) {

  if (
    datos.email
  ) {

    return Array.isArray(
      datos.email
    )
      ? datos.email[0]
      : String(
          datos.email
        )
  }


  if (
    datos.password
  ) {

    return Array.isArray(
      datos.password
    )
      ? datos.password[0]
      : String(
          datos.password
        )
  }


  if (
    datos.area_id
  ) {

    return Array.isArray(
      datos.area_id
    )
      ? datos.area_id[0]
      : String(
          datos.area_id
        )
  }


  if (
    datos.rol_id
  ) {

    return Array.isArray(
      datos.rol_id
    )
      ? datos.rol_id[0]
      : String(
          datos.rol_id
        )
  }


  if (
    datos.detail
  ) {

    return datos.detail
  }


  if (
    datos.detalle
  ) {

    return datos.detalle
  }


  /*
   * Si DRF devuelve otros campos
   * mostramos el primero.
   */

  const errores =
    Object.entries(
      datos
    )


  if (
    errores.length > 0
  ) {

    const [
      campo,
      valor
    ] =
      errores[0]


    const texto =
      Array.isArray(valor)
        ? valor.join(', ')
        : String(valor)


    return (
      `${campo}: ${texto}`
    )
  }


  return (
    'Revise los datos ingresados.'
  )
}


/* =========================================================
   MENSAJE
========================================================= */

function mostrarMensaje(
  texto,
  esError = false
) {

  mensaje.value =
    texto


  error.value =
    esError


  setTimeout(
    () => {

      mensaje.value = ''

    },
    3500
  )
}


/* =========================================================
   INICIALES
========================================================= */

function obtenerIniciales(
  nombre
) {

  if (!nombre) {

    return 'U'
  }


  return nombre
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(
      palabra =>
        palabra
          .charAt(0)
          .toUpperCase()
    )
    .join('')
}


/* =========================================================
   CERRAR SESIÓN
========================================================= */

function cerrarSesion() {

  localStorage.removeItem(
    'sigta_token'
  )


  localStorage.removeItem(
    'sigta_usuario'
  )


  router.push(
    '/login'
  )
}

</script>


<style scoped>

* {
  box-sizing: border-box;
}


/* =========================================================
   LAYOUT
========================================================= */

.admin-layout {

  min-height: 100vh;

  display: flex;

  background: var(--sigta-azul-tenue);

  font-family: var(--sigta-fuente);
}


.main-content {

  flex: 1;

  min-width: 0;

  padding: 28px;

  overflow-x: hidden;
}


/* =========================================================
   ENCABEZADO
========================================================= */

.topbar {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  gap: 20px;

  margin-bottom: 21px;
}


.breadcrumb {

  display: block;

  margin-bottom: 7px;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


.topbar h1 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 28px;
}


.topbar p {

  margin:
    5px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 18px;
}


.btn-primary {

  min-height: 43px;

  padding:
    0
    18px;

  border: none;

  border-radius: 8px;

  background: var(--sigta-mostaza);

  color: var(--sigta-azul);

  font-size: 17px;

  font-weight: 800;

  cursor: pointer;
}


.btn-primary:hover {

  background: var(--sigta-mostaza);
}


/* =========================================================
   ESTADÍSTICAS
========================================================= */

.stats-grid {

  display: grid;

  grid-template-columns:
    repeat(4,1fr);

  gap: 13px;

  margin-bottom: 18px;
}


.stat-card {

  min-height: 105px;

  padding: 16px;

  border-top:
    3px solid var(--sigta-mostaza);

  border-radius: 9px;

  background: white;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.05);
}


.stat-card span {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 15px;

  font-weight: 800;

  text-transform: uppercase;
}


.stat-card strong {

  display: block;

  margin:
    7px
    0;

  color: var(--sigta-azul);

  font-size: 25px;
}


.stat-card small {

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


/* =========================================================
   FILTROS
========================================================= */

.filters-card {

  display: grid;

  grid-template-columns:
    1fr 210px;

  gap: 12px;

  margin-bottom: 16px;

  padding: 14px;

  border-radius: 9px;

  background: var(--sigta-blanco);

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.search-box,
.filter-box {

  display: flex;

  flex-direction: column;

  gap: 6px;
}


.filters-card label {

  color: var(--sigta-texto-suave);

  font-size: 15px;

  font-weight: 700;
}


.filters-card input,
.filters-card select {

  width: 100%;

  height: 41px;

  padding:
    0
    12px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;

  color: var(--sigta-azul);

  font-size: 17px;

  outline: none;
}


.filters-card input:focus,
.filters-card select:focus {

  border-color: var(--sigta-texto-suave);

  box-shadow:
    0
    0
    0
    3px
    rgba(11,87,149,.08);
}


/* =========================================================
   ALERTAS
========================================================= */

.alert {

  margin-bottom: 14px;

  padding:
    11px
    14px;

  border-radius: 7px;

  font-size: 17px;
}


.alert.success {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}


.alert.error {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


/* =========================================================
   TABLA
========================================================= */

.table-card {

  overflow: hidden;

  border-radius: 10px;

  background: white;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.06);
}


.table-header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 12px;

  padding:
    17px
    18px;

  border-bottom:
    1px solid var(--sigta-borde);
}


.table-header h2 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 21px;
}


.table-header p {

  margin:
    3px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


.result-count {

  padding:
    5px
    8px;

  border-radius: 15px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 14px;

  font-weight: 700;
}


.table-wrapper {

  width: 100%;

  overflow-x: auto;
}


table {

  width: 100%;

  min-width: 1100px;

  border-collapse:
    collapse;
}


th {

  padding:
    13px
    14px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  text-align: left;

  font-size: 15px;

  font-weight: 800;

  text-transform:
    uppercase;
}


td {

  padding:
    14px;

  border-top:
    1px solid var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 16px;

  vertical-align: middle;
}


td strong {

  color: var(--sigta-azul);
}


/* =========================================================
   USUARIO TABLA
========================================================= */

.user-cell {

  display: flex;

  align-items: center;

  gap: 9px;
}


.table-avatar {

  width: 32px;

  height: 32px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);

  font-size: 15px;

  font-weight: 900;
}


.user-cell strong,
.user-cell small {

  display: block;
}


.user-cell small {

  margin-top: 2px;

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


/* =========================================================
   BADGES
========================================================= */

.badge {

  display: inline-block;

  padding:
    5px
    9px;

  border-radius: 20px;

  font-size: 14px;

  font-weight: 700;
}


.badge.activo {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}


.badge.inactivo {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


.role-badge {

  display: inline-block;

  padding:
    5px
    7px;

  border-radius: 5px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


.first-login {

  font-size: 15px;

  font-weight: 700;
}


.first-login.pending {

  color: var(--sigta-mostaza-oscuro);
}


.first-login.completed {

  color: var(--sigta-exito);
}


/* =========================================================
   ACCIONES
========================================================= */

.actions {

  display: flex;

  gap: 6px;
}


.actions button {

  padding:
    6px
    9px;

  border: none;

  border-radius: 5px;

  font-size: 14px;

  font-weight: 700;

  cursor: pointer;
}


.btn-edit {

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);
}


.btn-disable {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


.btn-enable {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}

.btn-reset-password {
  background: #fff7d6;
  color: var(--sigta-azul);
}


/* =========================================================
   CARGA / VACÍO
========================================================= */

.loading,
.empty {

  padding: 45px;

  text-align: center;

  color: var(--sigta-texto-suave);

  font-size: 17px;
}


/* =========================================================
   MODAL
========================================================= */

.modal-overlay {

  position: fixed;

  inset: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  padding: 20px;

  background:
    rgba(7,35,60,.58);

  z-index: 1000;
}


.modal {

  width: 100%;

  max-width: 610px;

  max-height: 90vh;

  overflow-y: auto;

  padding: 24px;

  border-top:
    4px solid var(--sigta-mostaza);

  border-radius: 12px;

  background: white;

  box-shadow:
    0
    20px
    60px
    rgba(0,0,0,.25);
}


.modal-header {

  display: flex;

  justify-content:
    space-between;

  gap: 15px;

  margin-bottom: 20px;
}


.modal-kicker {

  display: block;

  margin-bottom: 5px;

  color: var(--sigta-texto-suave);

  font-size: 14px;

  text-transform:
    uppercase;

  font-weight: 800;
}


.modal-header h2 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 20px;
}


.modal-header p {

  margin:
    4px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 16px;
}


.close {

  border: none;

  background: transparent;

  color: var(--sigta-texto-suave);

  font-size: 27px;

  cursor: pointer;
}


/* =========================================================
   FORMULARIO
========================================================= */

.grid {

  display: grid;

  grid-template-columns:
    1fr
    1fr;

  gap: 14px;
}


.field {

  display: flex;

  flex-direction: column;

  gap: 6px;
}


.field.full {

  grid-column:
    1 / -1;
}


.field label {

  color: var(--sigta-azul);

  font-size: 16px;

  font-weight: 700;
}


.field label span {

  color: var(--sigta-error);
}


.field input,
.field select {

  width: 100%;

  height: 42px;

  padding:
    0
    12px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;

  color: var(--sigta-azul);

  outline: none;

  font-size: 17px;
}


.field input:focus,
.field select:focus {

  border-color: var(--sigta-texto-suave);

  box-shadow:
    0
    0
    0
    3px
    rgba(11,87,149,.1);
}


.field select:disabled {

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  cursor: not-allowed;
}


.field small {

  color: var(--sigta-texto-suave);

  font-size: 14px;

  line-height: 1.4;
}

.id-column {
  width: 54px;
  padding-right: 8px;
  padding-left: 12px;
  text-align: center;
  white-space: nowrap;
}

.password-field {
  position: relative;
}

.password-field input {
  padding-right: 48px;
}

.password-eye {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
  cursor: pointer;
}

.password-eye:disabled {
  cursor: not-allowed;
  opacity: .45;
}


/* =========================================================
   ERROR MODAL
========================================================= */

.modal-error {

  margin-top: 14px;

  padding: 10px;

  border-radius: 6px;

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);

  font-size: 16px;
}

.modal-success {
  margin-top: 14px;
  padding: 10px;
  border-radius: 6px;
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
  font-size: 16px;
}

.confirm-modal {
  max-width: 500px;
  text-align: center;
}

.confirm-modal h2 {
  margin: 12px 0 8px;
  color: var(--sigta-azul);
}

.confirm-modal > p {
  color: var(--sigta-texto-suave);
}

.confirm-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto;
  border-radius: 50%;
  font-size: 26px;
  font-weight: 800;
}

.confirm-icon.inactivar {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}

.confirm-icon.activar {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}

.confirm-icon.reset-password {
  background: #fff7d6;
  color: var(--sigta-azul);
}

.confirm-user-data {
  margin: 20px 0;
  padding: 14px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: var(--sigta-azul-tenue);
  text-align: left;
}

.confirm-user-data div {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 8px;
  padding: 4px 0;
}

.confirm-user-data dt { font-weight: 700; color: var(--sigta-azul); }
.confirm-user-data dd { margin: 0; overflow-wrap: anywhere; }

.confirm-warning {
  padding: 12px;
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: 6px;
  background: #fff9e6;
  text-align: left;
}

.btn-confirm-disable,
.btn-confirm-enable {
  min-height: 40px;
  padding: 0 16px;
  border: 0;
  border-radius: 7px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm-disable { background: var(--sigta-error); }
.btn-confirm-enable { background: var(--sigta-azul); }

.btn-confirm-reset {
  min-height: 40px;
  padding: 0 16px;
  border: 0;
  border-radius: 7px;
  background: var(--sigta-azul);
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm-reset:disabled {
  cursor: not-allowed;
  opacity: .6;
}

.generated-password-modal {
  max-width: 520px;
}

.generated-password-modal h2 {
  margin: 12px 0 18px;
  color: var(--sigta-azul);
  text-align: center;
}

.one-time-notice {
  margin-top: 16px;
  padding: 12px;
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: 6px;
  background: #fff9e6;
  color: var(--sigta-texto-suave);
}

.one-time-notice strong,
.one-time-notice span {
  display: block;
}

.one-time-notice span {
  margin-top: 4px;
}


/* =========================================================
   ACCIONES MODAL
========================================================= */

.modal-actions {

  display: flex;

  justify-content:
    flex-end;

  gap: 10px;

  margin-top: 22px;
}


.btn-cancel,
.btn-save {

  min-height: 40px;

  padding:
    0
    16px;

  border-radius: 7px;

  font-size: 16px;

  font-weight: 700;

  cursor: pointer;
}


.btn-cancel {

  border:
    1px solid var(--sigta-borde);

  background: white;

  color: var(--sigta-texto-suave);
}


.btn-save {

  border: none;

  background: var(--sigta-azul);

  color: white;
}


.btn-save:disabled {

  opacity: .6;

  cursor: not-allowed;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 1050px
) {

  .stats-grid {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 760px
) {

  .admin-layout {

    display: block;
  }


  .main-content {

    padding: 18px;
  }


  .topbar {

    align-items:
      flex-start;

    flex-direction:
      column;
  }


  .stats-grid {

    grid-template-columns:
      1fr
      1fr;
  }


  .filters-card {

    grid-template-columns:
      1fr;
  }


  .grid {

    grid-template-columns:
      1fr;
  }


  .field.full {

    grid-column: auto;
  }

}


@media (
  max-width: 480px
) {

  .stats-grid {

    grid-template-columns:
      1fr;
  }


  .modal-actions {

    flex-direction:
      column-reverse;
  }


  .btn-cancel,
  .btn-save {

    width: 100%;
  }

}

</style>
