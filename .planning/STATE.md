# Project State

## Current Milestone

**Milestone:** v2.0 Production — Phase 5 complete
**Phase:** 6 — Notificações e Deploy
**Plan:** —
**Status:** Phase 5 shipped, Phase 6 planning
**Last activity:** 2026-05-04 — Phase 5 completed (budget goals + alerts + UI polish)

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-30)
See: `.planning/MILESTONES.md` (v1.0 retrospective)

**Core value:** Familiares conseguem registrar e visualizar todos os gastos do lar em um só lugar, com análises claras que revelam padrões de consumo e oportunidades de economia.

## Previous Milestones

- ✅ v1.0 MVP — SHIPPED (2026-04-30) — Auth JWT, Family Groups, Dashboard, ML + Export

## What's Next

Milestone v2.0 — Planejamento em andamento:

1. ✅ `/gsd-new-milestone "v2.0 Production"` — iniciado
2. ✅ Phase 5 — Orçamento e Metas (BUDG-01/02/03) — SHIPPED 2026-05-04
3. ⏳ Phase 6 — Notificações e Deploy (NOTF-01/02, INFR-01/02/03)

## Recent Commits

- `cc3c963` chore: remove REQUIREMENTS.md for v1.0 milestone — 2026-04-30
- `ed7c783` chore: archive v1.0 milestone files — 2026-04-30
- `8a0ac9f` feat: implementa fases 1-3 do v1(auth, family, dashboard) — 2026-04-30
- `fcf429b` Initial commit - projeto limpo — 2026-04-24

## Active TODOs

- [x] Criar REQUIREMENTS.md para v2.0
- [x] Criar ROADMAP.md para v2.0 (Phases 5–6)
- [x] Phase 5 discuss-phase: decisões capturadas em `05-CONTEXT.md`
- [x] Phase 5 plan-phase: `05-01-PLAN.md` (backend) e `05-02-PLAN.md` (frontend) criados
- [x] Phase 5 ui-spec: `05-UI-SPEC.md` criado
- [x] Phase 5 execute-phase: implementar Budget models, endpoints, e UI ✅
- [x] Phase 5 review: bugs fixed (formatarValor, category filtering, delete UI)
- [ ] Phase 6 — Notifications (email/push) + PostgreSQL + CI/CD + deploy

## Accumulated Context

- Options API no Vue — Composition API migration candidate for v2
- SQLite → PostgreSQL migration required before production deploy
- ML model on-demand training — consider Celery/persisted model for large datasets
- No automated tests — only manual testing performed
- GAST-04 pagination partial (simple limit, no full metadata)
- Git tag v1.0 pushado para origin
