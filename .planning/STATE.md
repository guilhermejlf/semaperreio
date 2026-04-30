# Project State

## Current Milestone

**Milestone:** v1.0 MVP — SHIPPED (2026-04-30)
**Tag:** `v1.0`
**Next Milestone:** v2.0 — Orçamento, Notificações e Deploy

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-30)
See: `.planning/MILESTONES.md` (v1.0 retrospective)

**Core value:** Familiares conseguem registrar e visualizar todos os gastos do lar em um só lugar, com análises claras que revelam padrões de consumo e oportunidades de economia.

## v1.0 Shipped

- [x] **Phase 1 — Autenticação JWT** (2/2 plans, SUMMARY complete)
- [x] **Phase 2 — Grupo Familiar** (2/2 plans, SUMMARY complete)
- [x] **Phase 3 — Dashboard Inteligente** (2/2 plans, SUMMARY complete)
- [x] **Phase 4 — ML + Exportação** (1/1 plan, SUMMARY complete)
- [x] Git tag `v1.0` created
- [x] Archives created: `.planning/milestones/v1.0-ROADMAP.md`, `.planning/milestones/v1.0-REQUIREMENTS.md`
- [x] MILESTONES.md created with retrospective
- [x] PROJECT.md updated with validated requirements
- [x] ROADMAP.md reorganized with milestone grouping

## What's Next

Milestone v2.0 — iniciar planejamento:

1. `/gsd-new-milestone "v2.0 Production"` — questioning → research → requirements → roadmap
2. Phase 5 — Orçamento e Metas (BUDG-01/02/03)
3. Phase 6 — Notificações e Deploy (NOTF-01/02, INFR-01/02/03)

## Recent Commits

- `8a0ac9f` feat: implementa fases 1-3 do v1(auth, family, dashboard) — 2026-04-30
- `fcf429b` Initial commit - projeto limpo — 2026-04-24

## Active TODOs

- [ ] `/gsd-new-milestone` — iniciar v2.0
- [ ] Phase 5 — Budget goals backend + frontend
- [ ] Phase 6 — Notifications (email/push) + PostgreSQL + CI/CD + deploy

## Tech Debt / Notes

- Options API no Vue — Composition API migration candidate for v2
- SQLite → PostgreSQL migration required before production deploy
- ML model on-demand training — consider Celery/persisted model for large datasets
- No automated tests — only manual testing performed
- GAST-04 pagination partial (simple limit, no full metadata)
