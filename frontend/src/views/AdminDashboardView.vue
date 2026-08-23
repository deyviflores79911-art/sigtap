<template>

  <div class="dashboard-layout">

    <!-- =====================================================
         MENÚ ÚNICO DEL ADMINISTRADOR
    ====================================================== -->

    <AdminMenu />


    <!-- =====================================================
         CONTENIDO PRINCIPAL
    ====================================================== -->

    <main class="main-content">


      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="topbar">

        <div>

          <span class="breadcrumb">
            SIGTA / Administración / Dashboard
          </span>

          <h1>
            Panel de Administración
          </h1>

          <p>
            Supervisión general de los procesos y
            configuración del Sistema Integral de Gestión.
          </p>

        </div>


        <div class="user-box">

          <div class="user-avatar">
            {{ inicialesUsuario }}
          </div>

          <div>

            <strong>
              {{
                usuario?.nombre
                ||
                usuario?.nombre_completo
                ||
                'Administrador'
              }}
            </strong>

            <span>
              {{
                usuario?.email
                ||
                'admin@emi.edu.bo'
              }}
            </span>

          </div>

        </div>

      </header>


      <!-- =================================================
           RESUMEN GENERAL
      ================================================== -->

      <section class="stats-grid">


        <!-- USUARIOS -->

        <article class="stat-card">

          <span>
            Usuarios
          </span>

          <strong>
            {{ resumen.usuarios }}
          </strong>

          <small>
            Registrados en SIGTA
          </small>

        </article>


        <!-- TICKETS -->

        <article class="stat-card">

          <span>
            Requerimientos de soporte
          </span>

          <strong>
            {{ resumen.tickets }}
          </strong>

          <small>
            Registrados en Soporte Técnico
          </small>

        </article>


        <!-- NUEVOS -->

        <article class="stat-card">

          <span>
            Requerimientos nuevos
          </span>

          <strong>
            {{ resumen.nuevos }}
          </strong>

          <small>
            Solicitudes registradas pendientes de atención UTIC
          </small>

        </article>


        <!-- COMPRAS -->

        <article class="stat-card">

          <span>
            Solicitudes de compra
          </span>

          <strong>
            {{ resumen.compras }}
          </strong>

          <small>
            Registradas en el proceso de Compras
          </small>

        </article>


        <!-- ÁREAS -->

        <article class="stat-card">

          <span>
            Áreas
          </span>

          <strong>
            {{ resumen.areas }}
          </strong>

          <small>
            Áreas institucionales activas
          </small>

        </article>

      </section>


      <!-- =================================================
           MENSAJE
      ================================================== -->

      <div
        v-if="mensaje"
        class="dashboard-message"
      >
        {{ mensaje }}
      </div>


      <!-- =================================================
           PROCESOS OPERATIVOS
      ================================================== -->

      <section class="content-card">

        <div class="section-header">

          <div>

            <span class="section-kicker">
              OPERACIÓN
            </span>

            <h2>
              Procesos institucionales
            </h2>

            <p>
              Acceda a los procesos de Soporte Técnico,
              Mantenimiento y Compras.
            </p>

          </div>

        </div>


        <div class="operation-grid">


          <!-- =================================================
               SOPORTE TÉCNICO
          ================================================== -->

          <button
            class="operation-card"
            @click="
              router.push(
                '/admin/soporte'
              )
            "
          >

            <div class="operation-icon">
              ST
            </div>


            <div class="operation-content">

              <div class="operation-top">

                <strong>
                  Soporte Técnico
                </strong>

                <span class="module-status">
                  Activo
                </span>

              </div>


              <p>
                Supervise los requerimientos desde el registro de la solicitud de soporte,
                la clasificación de prioridad, la asignación del especialista,
                la revisión del equipo, la reparación técnica y la conformidad del servicio.
              </p>


              <div class="process-actions">

                <span>
                  Registrar solicitud de soporte
                </span>

                <span>
                  Registrar revisión del equipo
                </span>

                <span>
                  Clasificar prioridad
                </span>

              </div>


              <div class="operation-footer">

                <span>
                  {{ resumen.tickets }} requerimiento(s)
                </span>

                <strong>
                  {{ resumen.nuevos }} nuevo(s)
                </strong>

              </div>

            </div>

          </button>


          <!-- =================================================
               MANTENIMIENTO
          ================================================== -->

          <button
            class="operation-card"
            @click="
              router.push(
                '/admin/mantenimiento'
              )
            "
          >

            <div class="operation-icon">
              MT
            </div>


            <div class="operation-content">

              <div class="operation-top">

                <strong>
                  Mantenimiento
                </strong>

                <span class="module-status development">
                  En integración
                </span>

              </div>


              <p>
                Supervise los requerimientos de mantenimiento,
                su derivación al auxiliar, la reposición de almacén,
                la ejecución del mantenimiento y el informe del trabajo realizado.
              </p>


              <div class="process-actions">

                <span>
                  Derivar a su auxiliar
                </span>

                <span>
                  ¿Requiere reposición de almacén?
                </span>

                <span>
                  Realizar informe y fotografía del trabajo realizado
                </span>

              </div>


              <div class="operation-footer">

                <span>
                  Servicios Generales
                </span>

                <strong>
                  Proceso independiente
                </strong>

              </div>

            </div>

          </button>


          <!-- =================================================
               COMPRAS
          ================================================== -->

          <button
            class="operation-card"
            @click="
              router.push(
                '/admin/compras'
              )
            "
          >

            <div class="operation-icon">
              CP
            </div>


            <div class="operation-content">

              <div class="operation-top">

                <strong>
                  Compras
                </strong>

                <span class="module-status">
                  Activo
                </span>

              </div>


              <p>
                Consulte las solicitudes de compra y el avance del trámite desde la carga del expediente,
                la autorización del gasto, la certificación del presupuesto disponible,
                el desembolso, el ingreso y el despacho desde almacén.
              </p>


              <div class="process-actions">

                <span>
                  Cargar expediente de compra
                </span>

                <span>
                  Certificar presupuesto disponible
                </span>

                <span>
                  Registrar desembolso de dinero
                </span>

              </div>


              <div class="operation-footer">

                <span>
                  {{ resumen.compras }} solicitud(es)
                </span>

                <strong>
                  Caja Chica
                </strong>

              </div>

            </div>

          </button>


          <!-- =================================================
               PORTAL SOLICITANTE
          ================================================== -->

          <button
            class="operation-card"
            @click="
              router.push(
                '/admin/portal-solicitante'
              )
            "
          >

            <div class="operation-icon">
              PS
            </div>


            <div class="operation-content">

              <div class="operation-top">

                <strong>
                  Portal Solicitante
                </strong>

                <span class="module-status">
                  Activo
                </span>

              </div>


              <p>
                Consulte cómo los usuarios registran
                y realizan seguimiento a sus
                requerimientos institucionales.
              </p>


              <div class="process-actions">

                <span>
                  Soporte Técnico
                </span>

                <span>
                  Mantenimiento
                </span>

                <span>
                  Compras
                </span>

              </div>


              <div class="operation-footer">

                <span>
                  Portal de autoservicio
                </span>

                <strong>
                  3 procesos
                </strong>

              </div>

            </div>

          </button>

        </div>

      </section>


      <!-- =================================================
           ADMINISTRACIÓN DEL SISTEMA
      ================================================== -->

      <section class="content-card">

        <div class="section-header">

          <div>

            <span class="section-kicker">
              ADMINISTRACIÓN
            </span>

            <h2>
              Administración del sistema
            </h2>

            <p>
              Gestione identidad, permisos,
              auditoría y configuración de SIGTA.
            </p>

          </div>

        </div>


        <div class="quick-grid">


          <!-- =================================================
               USUARIOS
          ================================================== -->

          <button
            @click="
              router.push(
                '/admin/usuarios'
              )
            "
          >

            <div class="quick-icon">
              U
            </div>

            <div>

              <strong>
                Gestión de usuarios
              </strong>

              <span>
                Crear, modificar, activar e inactivar
                cuentas institucionales.
              </span>

            </div>

          </button>


          <!-- =================================================
               ROLES / PERMISOS / ÁREAS
          ================================================== -->

          <button
            @click="
              router.push(
                '/admin/roles-areas'
              )
            "
          >

            <div class="quick-icon">
              RP
            </div>

            <div>

              <strong>
                Roles, permisos y áreas
              </strong>

              <span>
                Definir qué puede visualizar y ejecutar
                cada rol dentro de SIGTA.
              </span>

            </div>

          </button>


          <!-- =================================================
               CONSULTA DE TICKETS
          ================================================== -->

          <button
            @click="
              router.push(
                '/admin/tickets'
              )
            "
          >

            <div class="quick-icon">
              T
            </div>

            <div>

              <strong>
                Consulta de requerimientos de soporte
              </strong>

              <span>
                Consulte el listado administrativo
                de requerimientos de Soporte Técnico.
              </span>

            </div>

          </button>


          <!-- =================================================
               BITÁCORA
          ================================================== -->

          <button
            @click="
              router.push(
                '/admin/bitacora'
              )
            "
          >

            <div class="quick-icon">
              B
            </div>

            <div>

              <strong>
                Bitácora
              </strong>

              <span>
                Consultar accesos, acciones
                y trazabilidad de los procesos.
              </span>

            </div>

          </button>


          <!-- =================================================
               SMTP
          ================================================== -->

          <button
            @click="
              router.push(
                '/admin/smtp'
              )
            "
          >

            <div class="quick-icon">
              @
            </div>

            <div>

              <strong>
                Correo SMTP
              </strong>

              <span>
                Configurar el canal de correo
                para recuperación y notificaciones.
              </span>

            </div>

          </button>


          <!-- =================================================
               PREFERENCIAS
          ================================================== -->

          <button
            @click="
              router.push(
                '/admin/preferencias'
              )
            "
          >

            <div class="quick-icon">
              P
            </div>

            <div>

              <strong>
                Preferencias
              </strong>

              <span>
                Configurar parámetros generales
                del funcionamiento de SIGTA.
              </span>

            </div>

          </button>

        </div>

      </section>


      <!-- =================================================
           CONTROL DE ACCESO
      ================================================== -->

      <section class="security-card">

        <div class="security-icon">
          AC
        </div>


        <div class="security-content">

          <span>
            CONTROL DE ACCESO
          </span>

          <h2>
            Roles y permisos
          </h2>

          <p>
            SIGTA utilizará los roles y permisos para
            determinar qué módulos puede visualizar cada
            usuario y qué acciones puede ejecutar dentro
            de cada proceso.
          </p>

        </div>


        <button
          type="button"
          @click="
            router.push(
              '/admin/roles-areas'
            )
          "
        >
          Administrar
        </button>

      </section>

    </main>

  </div>

</template>


<script setup>

import {
  computed,
  onMounted,
  reactive,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'


/* =========================================================
   MENÚ ÚNICO
========================================================= */

import AdminMenu
  from '../components/AdminMenu.vue'


const router =
  useRouter()


/* =========================================================
   USUARIO
========================================================= */

const usuario =
  ref(null)


/* =========================================================
   RESUMEN
========================================================= */

const resumen =
  reactive({

    usuarios: 0,

    tickets: 0,

    nuevos: 0,

    compras: 0,

    areas: 0,
  })


/* =========================================================
   MENSAJE
========================================================= */

const mensaje =
  ref('')


/* =========================================================
   TOKEN
========================================================= */

const obtenerToken = () =>
  localStorage.getItem(
    'sigta_token'
  )


/* =========================================================
   INICIALES
========================================================= */

const inicialesUsuario =
  computed(() => {

    const nombre =
      usuario.value?.nombre
      ||
      usuario.value?.nombre_completo
      ||
      'Administrador'


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
  })


/* =========================================================
   INICIO
========================================================= */

onMounted(
  async () => {

    const usuarioGuardado =
      localStorage.getItem(
        'sigta_usuario'
      )


    const token =
      obtenerToken()


    if (
      !usuarioGuardado
      ||
      !token
    ) {

      router.push(
        '/login'
      )

      return
    }


    try {

      usuario.value =
        JSON.parse(
          usuarioGuardado
        )

    } catch (error) {

      console.error(
        'Error leyendo usuario:',
        error
      )


      cerrarSesion()

      return
    }


    await cargarResumen()
  }
)


/* =========================================================
   HEADERS
========================================================= */

function headersAuth() {

  return {

    Authorization:
      `Token ${obtenerToken()}`,

    Accept:
      'application/json',
  }
}


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
   CARGAR RESUMEN
========================================================= */

async function cargarResumen() {

  mensaje.value = ''


  try {

    const [
      usuariosRes,
      ticketsRes,
      areasRes,
      comprasRes
    ] =
      await Promise.all([


        /* USUARIOS */

        fetch(
          '/api/usuarios/usuarios/',
          {
            headers:
              headersAuth()
          }
        ),


        /* SOPORTE TÉCNICO */

        fetch(
          '/api/soporte/tickets/',
          {
            headers:
              headersAuth()
          }
        ),


        /* ÁREAS */

        fetch(
          '/api/usuarios/areas/',
          {
            headers:
              headersAuth()
          }
        ),


        /* COMPRAS */

        fetch(
          '/api/compras/solicitudes/',
          {
            headers:
              headersAuth()
          }
        ),

      ])


    /* =====================================================
       SESIÓN VENCIDA
    ====================================================== */

    const respuestas = [

      usuariosRes,

      ticketsRes,

      areasRes,

      comprasRes
    ]


    const sinAutorizacion =
      respuestas.some(
        respuesta =>
          respuesta.status === 401
          ||
          respuesta.status === 403
      )


    if (
      sinAutorizacion
    ) {

      cerrarSesion()

      return
    }


    /* =====================================================
       LEER DATOS
    ====================================================== */

    const usuariosDatos =
      usuariosRes.ok
        ? await usuariosRes.json()
        : []


    const ticketsDatos =
      ticketsRes.ok
        ? await ticketsRes.json()
        : []


    const areasDatos =
      areasRes.ok
        ? await areasRes.json()
        : []


    const comprasDatos =
      comprasRes.ok
        ? await comprasRes.json()
        : []


    /* =====================================================
       NORMALIZAR
    ====================================================== */

    const usuarios =
      convertirLista(
        usuariosDatos
      )


    const tickets =
      convertirLista(
        ticketsDatos
      )


    const areas =
      convertirLista(
        areasDatos
      )


    const compras =
      convertirLista(
        comprasDatos
      )


    /* =====================================================
       CONTADORES
    ====================================================== */

    resumen.usuarios =
      usuarios.length


    resumen.tickets =
      tickets.length


    resumen.compras =
      compras.length


    resumen.areas =
      areas.filter(
        area =>
          area.activo === undefined
          ||
          area.activo === true
      ).length


    resumen.nuevos =
      tickets.filter(
        ticket => {

          const codigo =
            normalizarEstado(
              ticket.estado_codigo
            )


          const nombre =
            normalizarEstado(
              ticket.estado_nombre
            )


          return (
            codigo === 'NUEVO'
            ||
            nombre === 'NUEVO'
          )
        }
      ).length


    /* =====================================================
       AVISO SI UN ENDPOINT NO RESPONDE
    ====================================================== */

    const errores = []


    if (!usuariosRes.ok) {
      errores.push('usuarios')
    }


    if (!ticketsRes.ok) {
      errores.push('soporte técnico')
    }


    if (!areasRes.ok) {
      errores.push('áreas')
    }


    if (!comprasRes.ok) {
      errores.push('compras')
    }


    if (
      errores.length > 0
    ) {

      mensaje.value =
        `No fue posible cargar completamente: ${errores.join(', ')}.`

    }


    /* =====================================================
       DEBUG
    ====================================================== */

    console.log(
      'Dashboard usuarios:',
      usuarios
    )


    console.log(
      'Dashboard tickets:',
      tickets
    )


    console.log(
      'Dashboard áreas:',
      areas
    )


    console.log(
      'Dashboard expedientes de compra:',
      compras
    )


  } catch (error) {

    console.error(
      'Error cargando Dashboard:',
      error
    )


    mensaje.value =
      'No fue posible cargar todos los indicadores del panel.'
  }
}


/* =========================================================
   NORMALIZAR ESTADO
========================================================= */

function normalizarEstado(
  valor
) {

  return String(
    valor
    ||
    ''
  )
    .trim()
    .toUpperCase()
    .replace(/\s+/g, '_')
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

.dashboard-layout {

  min-height: 100vh;

  display: flex;

  background: #f2f5f9;

  font-family:
    Arial,
    Helvetica,
    sans-serif;
}


.main-content {

  flex: 1;

  min-width: 0;

  padding: 28px;

  overflow-x: hidden;
}


/* =========================================================
   TOPBAR
========================================================= */

.topbar {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  gap: 20px;

  margin-bottom: 24px;
}


.breadcrumb {

  display: block;

  margin-bottom: 7px;

  color: #8493a0;

  font-size: 9px;
}


.topbar h1 {

  margin: 0;

  color: #17324a;

  font-size: 28px;
}


.topbar p {

  margin:
    5px
    0
    0;

  color: #758391;

  font-size: 12px;
}


/* =========================================================
   USUARIO
========================================================= */

.user-box {

  min-width: 205px;

  display: flex;

  align-items: center;

  justify-content: flex-end;

  gap: 9px;

  padding:
    10px
    14px;

  background: #ffffff;

  border-radius: 9px;

  box-shadow:
    0
    3px
    10px
    rgba(0,0,0,.07);
}


.user-avatar {

  width: 35px;

  height: 35px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  background: #f2c400;

  color: #073b6f;

  font-size: 9px;

  font-weight: 900;
}


.user-box strong,
.user-box span {

  display: block;
}


.user-box strong {

  color: #1c3449;

  font-size: 11px;
}


.user-box span {

  margin-top: 2px;

  color: #788693;

  font-size: 9px;
}


/* =========================================================
   ESTADÍSTICAS
========================================================= */

.stats-grid {

  display: grid;

  grid-template-columns:
    repeat(5,1fr);

  gap: 14px;

  margin-bottom: 22px;
}


.stat-card {

  min-width: 0;

  min-height: 120px;

  padding: 18px;

  background: #ffffff;

  border-top:
    4px solid #f2c400;

  border-radius: 10px;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.stat-card span {

  display: block;

  margin-bottom: 7px;

  color: #647484;

  font-size: 9px;

  font-weight: 800;

  text-transform: uppercase;
}


.stat-card strong {

  display: block;

  margin-bottom: 6px;

  color: #073b6f;

  font-size: 28px;
}


.stat-card small {

  color: #8995a0;

  font-size: 8px;

  line-height: 1.35;
}


/* =========================================================
   MENSAJE
========================================================= */

.dashboard-message {

  margin-bottom: 18px;

  padding:
    11px
    13px;

  border-radius: 7px;

  background: #fff2d9;

  color: #775600;

  font-size: 10px;
}


/* =========================================================
   CONTENEDORES
========================================================= */

.content-card {

  margin-bottom: 20px;

  padding: 22px;

  background: #ffffff;

  border-radius: 10px;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.section-kicker {

  display: block;

  margin-bottom: 5px;

  color: #0b5795;

  font-size: 8px;

  font-weight: 900;

  letter-spacing: .8px;
}


.section-header h2 {

  margin: 0;

  color: #1b3449;

  font-size: 18px;
}


.section-header p {

  margin:
    5px
    0
    18px;

  color: #778590;

  font-size: 10px;
}


/* =========================================================
   PROCESOS
========================================================= */

.operation-grid {

  display: grid;

  grid-template-columns:
    repeat(2,1fr);

  gap: 14px;
}


.operation-card {

  min-width: 0;

  min-height: 210px;

  display: flex;

  align-items: flex-start;

  gap: 14px;

  padding: 18px;

  border:
    1px solid #dce3e9;

  border-radius: 9px;

  background: #fbfcfd;

  text-align: left;

  cursor: pointer;

  transition:
    border-color .2s,
    background .2s,
    box-shadow .2s,
    transform .1s;
}


.operation-card:hover {

  border-color: #0a5794;

  background: #f7fafc;

  box-shadow:
    0
    5px
    14px
    rgba(0,0,0,.07);
}


.operation-card:active {

  transform: scale(.995);
}


.operation-icon {

  width: 46px;

  height: 46px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 8px;

  background: #073b6f;

  color: #ffffff;

  font-size: 9px;

  font-weight: 900;
}


.operation-content {

  flex: 1;

  min-width: 0;
}


.operation-top {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 10px;
}


.operation-top strong {

  color: #084577;

  font-size: 14px;
}


.module-status {

  flex-shrink: 0;

  padding:
    4px
    7px;

  border-radius: 12px;

  background: #e7f6ed;

  color: #257144;

  font-size: 7px;

  font-weight: 800;
}


.module-status.development {

  background: #fff4d5;

  color: #806000;
}


.operation-content > p {

  margin:
    7px
    0
    12px;

  color: #6f7e8b;

  font-size: 9px;

  line-height: 1.5;
}


/* =========================================================
   ACCIONES DEL PROCESO
========================================================= */

.process-actions {

  display: flex;

  flex-wrap: wrap;

  gap: 5px;

  margin-bottom: 13px;
}


.process-actions span {

  padding:
    5px
    7px;

  border-radius: 5px;

  background: #edf2f6;

  color: #607789;

  font-size: 7px;
}


.operation-footer {

  display: flex;

  flex-wrap: wrap;

  align-items: center;

  justify-content:
    space-between;

  gap: 8px;

  padding-top: 11px;

  border-top:
    1px solid #e8edf1;
}


.operation-footer span {

  color: #718393;

  font-size: 8px;
}


.operation-footer strong {

  color: #07518d;

  font-size: 8px;
}


/* =========================================================
   ADMINISTRACIÓN
========================================================= */

.quick-grid {

  display: grid;

  grid-template-columns:
    repeat(2,1fr);

  gap: 13px;
}


.quick-grid button {

  min-height: 105px;

  display: flex;

  align-items: center;

  gap: 13px;

  padding: 15px;

  border:
    1px solid #dce3e9;

  border-radius: 9px;

  background: #fbfcfd;

  text-align: left;

  cursor: pointer;

  transition:
    border-color .2s,
    box-shadow .2s;
}


.quick-grid button:hover {

  border-color: #0a5794;

  box-shadow:
    0
    5px
    14px
    rgba(0,0,0,.07);
}


.quick-icon {

  width: 41px;

  height: 41px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 7px;

  background: #e8f1f8;

  color: #07518d;

  font-size: 9px;

  font-weight: 900;
}


.quick-grid strong,
.quick-grid span {

  display: block;
}


.quick-grid strong {

  margin-bottom: 6px;

  color: #084577;

  font-size: 12px;
}


.quick-grid span {

  color: #6f7e8b;

  font-size: 9px;

  line-height: 1.45;
}


/* =========================================================
   SEGURIDAD / PERMISOS
========================================================= */

.security-card {

  display: flex;

  align-items: center;

  gap: 15px;

  margin-bottom: 20px;

  padding: 19px;

  border-left:
    4px solid #f2c400;

  border-radius: 9px;

  background: #ffffff;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.security-icon {

  width: 45px;

  height: 45px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 8px;

  background: #073b6f;

  color: white;

  font-size: 9px;

  font-weight: 900;
}


.security-content {

  flex: 1;
}


.security-content > span {

  color: #0b5795;

  font-size: 7px;

  font-weight: 900;
}


.security-content h2 {

  margin:
    3px
    0
    5px;

  color: #17324a;

  font-size: 14px;
}


.security-content p {

  margin: 0;

  color: #71818f;

  font-size: 9px;

  line-height: 1.5;
}


.security-card button {

  min-height: 38px;

  padding:
    0
    13px;

  border: none;

  border-radius: 6px;

  background: #073b6f;

  color: white;

  font-size: 8px;

  font-weight: 700;

  cursor: pointer;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 1200px
) {

  .stats-grid {

    grid-template-columns:
      repeat(3,1fr);
  }

}


@media (
  max-width: 900px
) {

  .stats-grid {

    grid-template-columns:
      repeat(2,1fr);
  }


  .operation-grid,
  .quick-grid {

    grid-template-columns:
      1fr;
  }

}


@media (
  max-width: 760px
) {

  .dashboard-layout {

    display: block;
  }


  .main-content {

    padding: 18px;
  }


  .topbar {

    flex-direction: column;

    align-items: flex-start;
  }


  .user-box {

    justify-content:
      flex-start;
  }


  .security-card {

    align-items:
      flex-start;

    flex-direction:
      column;
  }

}


@media (
  max-width: 520px
) {

  .stats-grid {

    grid-template-columns:
      1fr;
  }


  .operation-card {

    flex-direction: column;
  }

}

</style>