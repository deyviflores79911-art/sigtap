# SIGTA - Sistema Integral de Gestión de Tickets y Aprobaciones

Línea base técnica y contractual para el desarrollo y operación de la plataforma SIGTA (Versión 1.0).

## Requisitos Previos (§3.2.1)
- PHP: 8.3.x (extensiones: pdo_mysql, pdo_sqlite, mbstring, openssl, fileinfo, gd, zip, intl)
- Composer: 2.7+
- Node.js: 20 LTS
- Git: 2.40+
- Docker + Docker Compose: Última versión estable
- SQLite: 3.40+

## Puesta en Marcha Local - Entorno SQLite (§3.2.2)
1. git clone <url-del-repositorio> sigta && cd sigta
2. composer install
3. npm install && npm run build
4. cp .env.example .env
5. php artisan key:generate
6. touch database/database.sqlite
7. php artisan migrate --seed
8. php artisan serve

## Cuentas de Demostración (Solo APP_ENV=local) (§3.2.2)
- Administrador: admin@sigta.local / Sigta.2026 -> Rol: ADMIN
- Aprobador Compras: aprobador@sigta.local / Sigta.2026 -> Rol: APROBADOR (Compras)
- Agente Compras: agente.cmp@sigta.local / Sigta.2026 -> Rol: AGENTE (Compras)
- Solicitante: solicitante@sigta.local / Sigta.2026 -> Rol: SOLICITANTE

## Réplica del Entorno de Staging con MySQL (§3.2.3)
docker compose up -d mysql
php artisan migrate:fresh --seed
php artisan test

## Matriz de Entornos del Proyecto (§3.2.4)
| Entorno | Base de Datos | Propósito | Datos | Despliegue |
| :--- | :--- | :--- | :--- | :--- |
| Local | SQLite 3 | Trabajo diario del desarrollador | Seeders de demostración | Manual |
| CI | SQLite y MySQL 8.0 | Verificación automática PR | Efímera | Automático |
| Staging | MySQL 8.0 | QA, Demo y UAT | Anonimizados | Automático (develop) |
| Producción | MySQL 8.0 | Operación real | Datos reales | Manual (main) |
