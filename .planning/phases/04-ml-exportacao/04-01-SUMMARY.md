---
phase: 04-ml-exportacao
plan: 01
status: completed
date_completed: 2026-04-30
---

# Summary: ML with Real Data + Export

## What Was Accomplished

### ML Pipeline (Real Data)

- Added `openpyxl>=3.1.0` to `requirements.txt`
- Implemented `prever_gasto()` in `api/views.py` (`POST /api/prever/`):
  - Queries real gastos from user's family context (same filter pattern)
  - Groups by category and builds time series from actual data
  - Uses `LinearRegression` from scikit-learn per category
  - Feature: temporal index (month sequence)
  - Fallback to simple average when < 3 months of data
  - Returns: `previsao` (total), `mes`, `ano`, `moeda`, `modo` (modelo/media), `por_categoria`, `dados_historicos` (last 6 months), `meses_de_dados`, contextual `mensagem`
  - Capped prediction at R$ 1.000.000 to avoid outliers
  - Returns 400 with friendly message if no gastos exist for prediction

### Export Endpoints

- `exportar_csv()` (`GET /api/export/csv/`):
  - `StreamingHttpResponse` with `text/csv; charset=utf-8`
  - Reuses same filters as `gastos()` view (category, date range, payment status)
  - Columns: `data`, `categoria`, `valor`, `descricao`, `pago`, `data_competencia`, `data_pagamento`, `criado_por`
  - Filename: `gastos.csv`

- `exportar_xlsx()` (`GET /api/export/xlsx/`):
  - `openpyxl` Workbook generated in memory
  - Same filter support as CSV
  - `HttpResponse` with `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - Filename: `gastos.xlsx`
  - Graceful fallback if `openpyxl` not installed

- Both endpoints registered in `api/urls.py`

### Frontend Integration

- Added `PREVER_GASTO` endpoint to `api.js`
- Dashboard displays previsão card and insights from backend data
- Export buttons available in gastos toolbar (if implemented in App.vue)

## Key Decisions

- On-demand model training (not pre-trained/pickled) — simpler, always uses latest data
- Per-category prediction rather than single total — more granular and useful
- Fallback to average for sparse data — avoids overfitting with few points
- CSV uses `StreamingHttpResponse` for memory efficiency with large datasets

## Files Modified

- `api/views.py` (prever_gasto, exportar_csv, exportar_xlsx)
- `api/urls.py` (prever, export/csv, export/xlsx routes)
- `requirements.txt` (added openpyxl)
- `frontend/src/config/api.js` (PREVER_GASTO endpoint)

## Verification

- [x] `POST /api/prever/` returns prediction based on real gastos data
- [x] Prediction changes when new gastos are added
- [x] `GET /api/export/csv/` downloads valid CSV with correct columns
- [x] `GET /api/export/xlsx/` downloads valid Excel file
- [x] Export respects active filters (category, date range)
- [x] 400 returned gracefully when insufficient data for prediction

## Notes

Implemented outside formal `/gsd-execute-phase` workflow. Committed in `8a0ac9f`. Note: Frontend export buttons may exist in App.vue but were not separately verified in this summary.
