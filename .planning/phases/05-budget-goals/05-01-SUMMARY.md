# Phase 5 - Backend Summary: Budget Model and API

**Phase:** 05-budget-goals
**Plan:** 05-01 (backend)
**Status:** ✅ Completed
**Date:** 2026-04-30

## What Was Built

### Database Model
- **`MetaGasto`** model in `api/models.py`:
  - `user` (FK to User) — owner of the budget
  - `categoria` (optional, null = general monthly budget)
  - `mes`, `ano` — month and year of the budget
  - `valor_meta` — budget target amount
  - `unique_together = [user, categoria, mes, ano]`
  - Migration: `0005_alter_gasto_categoria_metagasto.py`

### API Endpoints
- `GET /api/metas/?mes=&ano=` — list budgets for period with computed fields
- `POST /api/metas/criar/` — create budget
- `PUT /api/metas/<id>/` — update budget value
- `DELETE /api/metas/<id>/deletar/` — delete budget

### Computed Fields (Serializer)
- `gasto_realizado` — sum of user's expenses in that category/month/year
- `percentual_usado` — (spent / budget) × 100
- `status` — `ok` (<50%), `warning` (50-80%), `danger` (>80%), `critical` (>100%)
- `categoria_nome` — display name or "Geral"

### Dashboard Integration
- Dashboard response now includes `"metas"` object:
  - `geral` — general budget or null
  - `por_categoria` — list of category budgets with progress
- Budget insights added to insights list when thresholds exceeded

### Helper Functions
- `_get_meta_status(pct)` — status mapping
- `_get_gasto_realizado(user, categoria, mes, ano)` — aggregate spend query
- `_build_metas_context(user, mes, ano)` — builds metas payload for dashboard

## Files Modified
- `api/models.py` — added `MetaGasto` model
- `api/migrations/0005_alter_gasto_categoria_metagasto.py` — migration
- `api/serializers.py` — added `MetaGastoSerializer`
- `api/views.py` — added CRUD views + `_build_metas_context`
- `api/urls.py` — registered 4 new routes

## Key Decisions
- General budget (`categoria=null`) and category budgets coexist
- One budget per user/category/month/year (unique constraint)
- Computed fields in serializer to avoid redundant DB columns
- Dashboard integration pushes meta data to frontend with each load

## Verification
- [x] Model exists with correct fields and constraints
- [x] GET /api/metas/ returns computed fields
- [x] POST creates budget, 400 on duplicate
- [x] PUT updates value
- [x] DELETE removes budget
- [x] Dashboard includes metas in response
- [x] All endpoints require authentication
- [x] User isolation enforced
