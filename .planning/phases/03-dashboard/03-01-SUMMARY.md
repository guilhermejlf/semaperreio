---
phase: 03-dashboard
plan: 01
status: completed
date_completed: 2026-04-30
---

# Summary: Backend Dashboard API

## What Was Accomplished

- Created `dashboard()` view in `api/views.py` (`GET /api/dashboard/?mes=&ano=`):
  - Filters gastos by family/user context (same pattern as `gastos()` view)
  - Validates `mes` (1-12) and `ano` (YYYY) query params; returns 400 if missing/invalid
  - Returns comprehensive JSON:
    - `periodo`: {mes, ano, mes_nome}
    - `total_gastos`, `total_receitas`, `saldo`, `saldo_projetado`
    - `total_gastos_pagos`, `total_a_pagar`, `quantidade_pendentes`
    - `total_mes_anterior`, `variacao_absoluta`, `variacao_percentual`
    - `media_diaria`
    - `maior_gasto`: {valor, categoria, descricao}
    - `quantidade_gastos`
    - `ranking_categorias`: top categories sorted by total desc, with percentage
    - `evolucao_12meses`: last 12 months chronologically, with totals and counts
    - `insights`: auto-generated tips (e.g., "Você gastou X% em categoria Y")
    - `previsao_mensagem`: contextual message about projected balance
  - Uses Django ORM `annotate()`, `aggregate()`, `Coalesce`, `TruncMonth` for efficiency
  - Safe empty-state handling (returns zeros/empty arrays, not 500)
- Registered route `path('dashboard/', views.dashboard)` in `api/urls.py`

## Key Decisions

- Dashboard data computed on-demand (not cached) — acceptable for MVP scale
- `data_competencia` used as effective date (fallback to `data`)
- 12-month evolution is rolling (last 12 months from current), not fixed calendar year

## Files Modified

- `api/views.py` (dashboard view)
- `api/urls.py` (dashboard route)

## Verification

- [x] `GET /api/dashboard/?mes=6&ano=2026` returns all expected fields
- [x] Ranking ordered by total descending
- [x] 12-month evolution has correct data points
- [x] Previous month calculation handles January→December year transition
- [x] Empty data returns zeros/empty arrays (no 500)
- [x] Family filtering isolates data correctly

## Notes

Implemented outside formal `/gsd-execute-phase` workflow. Committed in `8a0ac9f`.
