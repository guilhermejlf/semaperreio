# Project State

## Current Phase

**Phase:** Phase 1 — Autenticação JWT (completed)
**Next Phase:** Phase 2 — Family Group

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-24)

**Core value:** Familiares conseguem registrar e visualizar todos os gastos do lar em um só lugar, com análises claras que revelam padrões de consumo e oportunidades de economia.

## What's Done

- [x] Código base mapeado (`.planning/codebase/`)
- [x] `PROJECT.md` criado
- [x] `REQUIREMENTS.md` criado
- [x] `ROADMAP.md` criado
- [x] Phase 1 planejada (`01-01-PLAN.md`, `01-02-PLAN.md`)
- [x] Discuss-phase completada — decisões capturadas em `01-CONTEXT.md`
- [x] Planos atualizados com decisões do discuss-phase
- [x] UI-SPEC gerado (`01-UI-SPEC.md`)
- [x] **Backend JWT:** djangorestframework-simplejwt instalado, endpoints `/auth/register/`, `/auth/login/`, `/auth/refresh/`, Gasto model com FK User, `IsAuthenticated` em todas as views, filtros por `request.user`
- [x] **Frontend Auth:** `AuthView.vue` com tabs (login/registro), `LoginForm.vue`, `RegisterForm.vue`, token storage `sa_access_token`/`sa_refresh_token`, auto-refresh em 401, logout button, integração condicional no `App.vue`
- [x] **Database:** Reset SQLite, migrations recriadas, testes manuais OK (cadastro, login, add gasto, dashboard charts, logout, re-login)
- [x] **Bugfix:** Chart.js reactivity loop resolvido com deep-clone e deferred init

## What's Next

Phase 2 — Family Group (planejamento e execução)

## Recent Commits

- Initial project initialization (2026-04-24)
- Codebase mapping completed (2026-04-24)
- Phase 1 — JWT Authentication implemented (2026-04-27)

## Active TODOs

- [x] Phase 2 discuss-phase: decisões capturadas em `02-CONTEXT.md`
- [x] Phase 2 UI-SPEC: `02-UI-SPEC.md` gerado
- [x] Phase 2 plan-phase: `02-01-PLAN.md` (backend) e `02-02-PLAN.md` (frontend) gerados
- [ ] Phase 2 execute-phase: implementar Family models, endpoints, e UI drawer
