# Credenciales de prueba de SIGTA

> **Uso exclusivo para desarrollo local.** Este archivo contiene contraseñas en texto visible. No debe incluirse en un repositorio público ni utilizarse en producción.

| Rol               | Correo          | Contraseña | Ruta principal |
|---|---|---|---|
| Administrador | `admin@emi.edu.bo` | `SIGTA_Admin#2026!` | `/admin/dashboard` |
| Solicitante   | `solicitante@emi.edu.bo` | `SIGTA_Usuario#2026!` | `/usuario/dashboard` |
| Jefe de UTIC  | `jefe.utic@emi.edu.bo` | `SIGTA_JefeUTIC#2026!` | `/jefe-utic/dashboard` |
| Especialista  | `especialista@emi.edu.bo` | `SIGTA_Especialista#2026!` | `/especialista/dashboard`      |
| Tesorería     | `tesoreria@emi.edu.bo` | `SIGTA_Tesoreria#2026!` | `/tesoreria/dashboard` |
| Director      | `director@emi.edu.bo` | `SIGTA_Director#2026!` | `/director/dashboard` |
| Encargado de Compras y Almacén | `almacen@emi.edu.bo` | `SIGTA_Almacen#2026!` | `/almacen/dashboard`      |
| DAF | `daf@emi.edu.bo` | `SIGTA_DAF#2026!` | `/daf/dashboard` |

## Observaciones

- Las cuentas están activas en la base de datos local `backend/db.sqlite3`.
- Las contraseñas fueron configuradas para pruebas y deben cambiarse antes de una implementación real.
- Si la base de datos no se copia a otra instalación, estas cuentas no existirán automáticamente.
- Los roles `SERVICIOS_GENERALES` y `AUXILIAR_SERVICIOS_GENERALES` todavía no tienen cuentas de prueba creadas.
