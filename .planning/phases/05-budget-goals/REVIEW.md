# Phase 5 Review — Budget Goals

**Date:** 2026-04-30
**Status:** Post-execution review

---

## Critical Bugs

### BUG-1: Wrong validator on MetaGasto.mes
**File:** `api/models.py`  
**Severity:** 🔴 High  
**Issue:** `mes` field uses `MaxLengthValidator(2)` instead of `MaxValueValidator(12)`. `MaxLengthValidator` is for strings, not integers. This will crash on migration or data validation.

**Fix:** Replace with `MaxValueValidator(12)`.

---

### BUG-2: Serializer gasto_realizado wrong for category budgets
**File:** `api/serializers.py`  
**Severity:** 🔴 High  
**Issue:** In `MetaGastoSerializer.get_gasto_realizado()`, the first query filters by `categoria=obj.categoria` but then the `if obj.categoria is None:` block reassigns `gastos` for general budgets. However, for category budgets (non-null categoria), the first query is correct but the code structure is confusing and the `categoria` filter in the first query is `categoria=obj.categoria` which works. Actually this is fine functionally, but could be clearer.

Actually: the first query has `categoria=obj.categoria if obj.categoria else None` which for general budgets would be `categoria=None` which would match only gastos with NULL category (which doesn't happen since Gasto requires a category). Then the `if` block overwrites it. This is functional but fragile.

**Fix:** Simplify: always filter by month/year, then add category filter only if not general.

---

### BUG-3: DashboardCharts mini-block uses undefined `formatarValor`
**File:** `frontend/src/components/DashboardCharts.vue`  
**Severity:** 🟡 Medium  
**Issue:** The mini budget block template calls `formatarValor(meta.gasto_realizado)` and `formatarValor(meta.valor_meta)` but `DashboardCharts` does not define this method. Vue will silently fail or show `NaN`/`undefined`.

**Fix:** Add `formatarValor(valor)` method to DashboardCharts or use inline `toLocaleString`.

---

### BUG-4: `abrirCriarCategoria` doesn't pass category list of missing categories
**File:** `frontend/src/components/BudgetView.vue`  
**Severity:** 🟡 Medium  
**Issue:** The "+ Adicionar Meta de Categoria" card opens a modal with empty category selector. User has to pick from all categories even those that already have budgets (which will fail on save due to unique constraint).

**Fix:** Filter out categories that already have budgets from the selector.

---

## UX Issues

### UX-1: No delete button on BudgetView
**File:** `frontend/src/components/BudgetView.vue`  
**Severity:** 🟡 Medium  
**Issue:** Users can create and edit budgets but cannot delete them from the UI. Must use API or admin.

**Fix:** Add delete button (with confirmation) on each budget card.

---

### UX-2: No visual distinction between "no budgets" and "loading"
**File:** `frontend/src/components/BudgetView.vue`  
**Severity:** 🟢 Low  
**Issue:** If API is slow, user sees empty state flash before loading spinner. Should show spinner first.

**Fix:** Ensure loading check comes before empty state (it does, but verify no race conditions).

---

### UX-3: DashboardCharts budget block always shows even with 0% progress
**File:** `frontend/src/components/DashboardCharts.vue`  
**Severity:** 🟢 Low  
**Issue:** The mini block shows `v-if="metasPorCategoria.length"` but will show even if all metas are at 0% which clutters the dashboard.

**Fix:** Consider only showing if any meta has non-zero gasto_realizado or if user explicitly wants to see all.

---

## Code Quality

### CQ-1: Missing `@require_auth` or explicit permission checks on budget endpoints
**File:** `api/views.py`  
**Severity:** 🟢 Low  
**Issue:** Budget views use `request.user` directly which relies on DRF's `IsAuthenticated` default. Should verify this is explicitly set in settings or add `@permission_classes([IsAuthenticated])`.

**Fix:** Add explicit `permission_classes` decorator for clarity.

---

### CQ-2: `deleteMeta` imported but unused in BudgetView
**File:** `frontend/src/components/BudgetView.vue`  
**Severity:** 🟢 Low  
**Issue:** `deleteMeta` is imported from api.js but no delete UI exists.

**Fix:** Either implement delete or remove unused import.

---

### CQ-3: MetaGasto model uses `PositiveSmallIntegerField` for `ano`
**File:** `api/models.py`  
**Severity:** 🟢 Low  
**Issue:** `ano` as `PositiveSmallIntegerField` limits to 0-32767, which is fine for years. But `mes` has `MaxLengthValidator(2)` which is wrong (should be `MaxValueValidator(12)` as noted in BUG-1).

---

## Review Checklist

- [x] Backend model correct? Mostly — fix validator
- [x] API endpoints secure? Yes, via DRF default auth
- [x] Frontend renders without errors? Yes (after fixes)
- [x] Dashboard integration works? Yes (after null-safety fix)
- [ ] Delete functionality? Missing
- [ ] Category filtering in create? Missing
- [ ] `formatarValor` in DashboardCharts? Missing
