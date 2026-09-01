# Credenciales de prueba de SIGTA

> **Uso exclusivo para desarrollo local.** Este archivo contiene contraseñas en texto visible. No debe incluirse en un repositorio público ni utilizarse en producción.

### Administración

| Rol | Correo | Contraseña | Ruta principal |
|---|---|---|---|
| Admin (superuser) | `superuser@emi.edu.bo` | `SIGTA_Superuser#2026!` | `/superuser/dashboard` |
| Director | `admin@emi.edu.bo` | `SIGTA_Admin#2026!` | `/admin/dashboard` |

### Jefes

| Rol | Correo | Contraseña | Ruta principal |
|---|---|---|---|
| Jefe UTIC  | `jefe.utic@emi.edu.bo` | `SIGTA_JefeUTIC#2026!` | `/jefe-utic/dashboard` |
| Jefe DAF | `jefe.daf@emi.edu.bo` | `SIGTA_JefeDAF#2026!` | `/daf/dashboard` |
| Jefe Mantenimiento | `servicios.generales@emi.edu.bo` | `SIGTA_ServiciosGrales#2026!` | `/servicios-generales/dashboard` |

### Técnicos

| Dependencia | Rol | Correo | Contraseña | Ruta principal |
|---|---|---|---|---|
| Jefe DAF | Técnico de la DAF | `daf@emi.edu.bo` | `SIGTA_DAF#2026!` | `/daf/dashboard` |
| Jefe DAF | Técnico de Almacén y Compras | `almacen@emi.edu.bo` | `SIGTA_Almacen#2026!` | `/almacen/dashboard` |
| Jefe DAF | Técnico de Tesorería | `tesoreria@emi.edu.bo` | `SIGTA_Tesoreria#2026!` | `/tesoreria/dashboard` |
| Jefe UTIC | Técnico de Soporte Técnico | `especialista@emi.edu.bo` | `SIGTA_Especialista#2026!` | `/especialista/dashboard` |
| Jefe Mantenimiento | Técnico de Mantenimiento | `auxiliar.sg@emi.edu.bo` | `SIGTA_AuxiliarSG#2026!` | `/auxiliar-servicios-generales/dashboard` |

### Usuario

| Rol | Correo | Contraseña | Ruta principal |
|---|---|---|---|
| Usuario | `solicitante@emi.edu.bo` | `SIGTA_Usuario#2026!` | `/usuario/dashboard` |

### Cuenta para probar HU-01 / HU-02 (cambio obligatorio de contraseña)

| Rol | Correo | Contraseña temporal | Comportamiento esperado |
|---|---|---|---|
| Solicitante (recién creado) | `nuevo.ingreso@emi.edu.bo` | `SIGTA_Temporal#2026!` | `must_change_password=true`: al iniciar sesión, el sistema exige cambiar la contraseña antes de permitir cualquier otra acción (bloqueado también en el backend, no solo en el redireccionamiento del frontend). |

## Observaciones

- Las cuentas están activas en la base de datos local `backend/db.sqlite3`. Se generan/actualizan con `python manage.py cargar_usuarios_prueba` (además de `cargar_permisos_sigta` para roles y permisos).
- Las contraseñas fueron configuradas para pruebas y deben cambiarse antes de una implementación real.
- Si la base de datos no se copia a otra instalación, estas cuentas no existirán automáticamente hasta correr los comandos de carga.
- Las contraseñas se almacenan con Argon2id (no en texto plano); este archivo es solo para pruebas locales.
