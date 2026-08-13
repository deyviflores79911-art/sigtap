# Guía Oficial de Contribución y Calidad - SIGTA

## Flujo de Trabajo en Git (§3.4.2)
Ramas permanentes protegidas: main y develop.

### Nomenclatura Estricta de Ramas (§3.4.2)
- feat/HU-nn-descripcion-corta
- fix/descripcion-corta
- hotfix/descripcion-corta
- release/vX.Y.Z

### Formato de Commits (Conventional Commits §3.4.2)
- feat(modulo), fix(modulo), test(modulo), refactor(modulo), chore(ci), docs(readme), perf(query)

## Pautas y Límites de Codificación (§3.3.1, §3.3.3)
- Estándar: PSR-12 (Laravel Pint)
- Tipado: declare(strict_types=1);
- Idioma: Código en inglés. Comentarios y vistas en español.
- Límites: Controlador max 20 líneas/acción; Servicio max 50 líneas/método; Clase max 400 líneas.

## Reglas de Seguridad No Negociables (§3.3.4)
1. Inyección SQL: Cero concatenación.
2. Registro de Logs: Sin contraseñas ni tokens.
3. URLs: Exponer UUID.
4. Archivos: Validar MIME real.
5. Secretos: Exclusivamente en .env.
6. Auditoría: Registro obligatorio en activity_log.

## Metas de Cobertura de Pruebas (§4.1.1)
- Workflow, Approval, Auth >= 90%
- Global >= 70%

## Checklist Obligatorio del Pull Request (§3.4.4)
- [ ] Pruebas unitarias/integración agregadas y en verde
- [ ] Suite ejecutada en SQLite y MySQL
- [ ] Cobertura mantenida
- [ ] Migración reversible
- [ ] Registro en activity_log
- [ ] Verificación de autorización 403
- [ ] Sin lógica en controladores ni vistas
- [ ] Sin secretos ni datos reales
- [ ] Cero dependencias externas no autorizadas
- [ ] Formatos en español (DD/MM/AAAA, BOB)
