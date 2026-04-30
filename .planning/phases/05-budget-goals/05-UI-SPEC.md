# UI Design Contract: Phase 5 — Orçamento e Metas

**Phase:** 05-budget-goals
**UI-SPEC:** 05-UI-SPEC.md
**Date:** 2026-04-30
**Theme:** Dark (consistent with existing v1.0 UI)
**Framework:** Vue 3 Options API + PrimeIcons + Chart.js

---

## Design Principles

1. **Consistency with v1.0** — Reuse existing card patterns, color system, and spacing from DashboardCharts.vue
2. **Visual hierarchy** — Meta geral (top) > categorias (list below), progress bars for quick scanning
3. **Action feedback** — Color-coded progress (green/yellow/red/critical) for immediate status recognition
4. **Confirmation for destructive/impactful actions** — Modal before editing an active budget to prevent accidental changes

---

## Color Palette (extends existing)

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-card` | `linear-gradient(135deg, #1e293b, #0f172a)` | Card backgrounds |
| `--border-subtle` | `rgba(255,255,255,0.1)` | Card borders |
| `--text-primary` | `#e5e7eb` | Headings, values |
| `--text-secondary` | `#94a3b8` | Labels, descriptions |
| `--text-muted` | `#64748b` | Small text, hints |
| `--accent-green` | `#10b981` | < 50% budget used |
| `--accent-yellow` | `#f59e0b` | 50–80% budget used |
| `--accent-red` | `#ef4444` | > 80% budget used |
| `--accent-critical` | `#dc2626` | > 100% budget used (darker red) |
| `--accent-blue` | `#3b82f6` | Primary actions, meta geral accent |
| `--bg-input` | `rgba(30,41,59,0.8)` | Form inputs |
| `--bg-hover` | `rgba(255,255,255,0.05)` | Hover states |

**Progress bar color mapping:**
- `< 50%` → `--accent-green` (fill), light green glow
- `50–80%` → `--accent-yellow` (fill), subtle pulse on hover
- `> 80%` → `--accent-red` (fill), warning glow
- `> 100%` → `--accent-critical` (fill), critical pulse animation (like `.risco` in DashboardCharts)

---

## Typography (matches existing)

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Page title | `1.5rem` | 700 | `#e5e7eb` |
| Block title (section) | `0.9rem` | 600 | `#94a3b8`, uppercase, letter-spacing 0.08em |
| Card heading (category name) | `1.1rem` | 600 | `#e5e7eb` |
| Value (R$ amount) | `1.3rem` | 700 | context-dependent (green/yellow/red) |
| Label | `0.9rem` | 500 | `#94a3b8` |
| Small / hint | `0.8rem` | 400 | `#64748b` |
| Progress percentage | `0.85rem` | 600 | context-dependent |

---

## Layout: Budget View (BudgetView.vue)

### Page Structure

```
<BudgetView>
  ├── Period Selector (same as Dashboard: month/year selects)
  ├── Loading State (pi-spinner)
  ├── Empty State (no budgets set)
  └── Content
      ├── Meta Geral Card (highlight — full width, prominent)
      ├── Block Title: "Metas por Categoria"
      ├── Category Budget Grid (responsive list)
      │   └── CategoryBudgetCard (repeated)
      └── Toast Container (for alerts when adding gasto)
```

### Period Selector

Same component as DashboardCharts.vue:
- Two `<select>` side by side: month (Portuguese names) + year (current, -1, -2)
- Centered, `margin-bottom: 20px`
- Changing period re-fetches budgets for that month/year

### Meta Geral Card

**Layout:** Full-width card (spans grid), larger padding (28px), more prominent.

```
┌─────────────────────────────────────────────┐
│  [icon: 🎯]  Meta Geral — Junho 2026        │
│                                             │
│  R$ 1.200,00 / R$ 2.000,00                  │
│  ████████████░░░░░░░░░░  60%                │
│  Restam R$ 800,00 para o limite             │
└─────────────────────────────────────────────┘
```

**Visual specs:**
- Background: `--bg-card` with left border 6px in current status color
- Icon: `🎯` (or `pi pi-bullseye` if PrimeIcons has it), 3rem
- Amount: `2rem` weight 800, color = status color
- Progress bar: height 12px, border-radius 6px, background `rgba(255,255,255,0.1)`, fill with status color + subtle glow
- Percentage text: inline to the right of bar, `0.85rem` weight 600
- "Restam..." text: `0.9rem`, `--text-secondary`
- Hover: `translateY(-3px)`, shadow like saldo-destaque

### Category Budget Cards Grid

**Layout:** `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`, gap 16px

**CategoryBudgetCard:**

```
┌─────────────────────────────────┐
│ 🍔 Restaurantes          [Edit] │
│                                 │
│ R$ 450,00 / R$ 500,00         │
│ ████████████████░░░░  90%       │
│ ⚠️ 10% restante — cuidado!     │
└─────────────────────────────────┘
```

**Visual specs:**
- Background: `--bg-card`, border-radius 16px, padding 18px
- Left border: 4px in status color (like mini cards in DashboardCharts)
- Top row: icon (emoji per category or `pi pi-tag`) + category name + edit button
  - Edit button: `pi pi-pencil`, small, gray, hover turns white
- Amount row: `R$ {spent} / R$ {budget}`, `1.2rem` weight 700
  - Spent color: status color
  - Budget color: `--text-primary`
- Progress bar: height 8px, border-radius 4px (smaller than meta geral)
- Warning message (conditional, > 80%): `⚠️ {pct}% restante` or `🔴 Meta ultrapassada em R$ {over}`
  - Color: yellow or red, `0.85rem`

### Empty State (no budgets for selected period)

```
┌─────────────────────────────────┐
│       [pi pi-inbox]             │
│   Nenhuma meta definida          │
│   Defina metas para acompanhar   │
│   seus gastos de Junho 2026     │
│       [Definir Meta Geral]       │
└─────────────────────────────────┘
```

- Same styling as dashboard empty state
- Centered, `padding: 60px 20px`
- Button: green background (#22c55e), white text, border-radius 10px

---

## Layout: Budget Edit Modal

**Modal overlay:** `rgba(0,0,0,0.7)` backdrop, centered card

**Modal card:**
- Width: `min(480px, 90vw)`
- Background: `#1e293b` (solid, slightly lighter than cards for elevation)
- Border: `1px solid rgba(255,255,255,0.15)`
- Border-radius: 20px
- Padding: 28px
- Shadow: `0 24px 48px rgba(0,0,0,0.5)`

**Header:**
```
┌─────────────────────────────────┐
│ ✏️ Editar Meta — Restaurantes    │
│                                 │
│ Você já gastou R$ 450,00         │
│ de R$ 500,00 nesta categoria    │
└─────────────────────────────────┘
```
- Icon + title: `1.2rem` weight 700
- Context text: `0.9rem`, `--text-secondary`, margin-bottom 20px

**Form fields:**
```
Valor da Meta (R$)
┌───────────────────────────────┐
│ R$ [      500,00      ]       │
└───────────────────────────────┘

[Cancelar]        [Salvar Meta]
```

- Input: same style as period-select but wider, `font-size: 1.1rem`, text centered
- Prefix "R$ " inside input, grayed
- Buttons:
  - Cancelar: transparent bg, border `1px solid rgba(255,255,255,0.2)`, text `--text-secondary`, hover `--text-primary`
  - Salvar Meta: bg `#22c55e`, white text, weight 600, border-radius 10px, hover brighter green

**Confirmation step (if editing existing with spend > 0):**

When user clicks "Salvar Meta" and there's already spend in this category/period:

```
┌─────────────────────────────────┐
│ ⚠️ Confirme a alteração         │
│                                 │
│ Você já gastou R$ 450,00 em     │
│ Restaurantes este mês.          │
│                                 │
│ Alterar a meta de R$ 500,00     │
│ para R$ 700,00?                 │
│                                 │
│ [Voltar]         [Confirmar]    │
└─────────────────────────────────┘
```

- Same modal style, but header in yellow (`#f59e0b`)
- "Voltar" = secondary button
- "Confirmar" = green button

---

## Layout: Dashboard Integration (mini progress bars)

In `DashboardCharts.vue`, add a new block between "Comportamento" and "Gráficos":

```
<!-- BLOCO 3 — METAS DO MÊS -->
<div class="block-title">Metas do Mês</div>
<div class="budget-grid">
  <div class="budget-mini-card" v-for="meta in metasComProgresso" :key="meta.categoria">
    <div class="budget-mini-header">
      <span class="budget-categoria">{{ meta.nome }}</span>
      <span class="budget-pct" :class="meta.statusClass">{{ meta.pct }}%</span>
    </div>
    <div class="budget-mini-bar">
      <div class="budget-mini-fill" :class="meta.statusClass" :style="{width: meta.pctClamped + '%'}"></div>
    </div>
    <div class="budget-mini-values">
      {{ formatarValor(meta.gasto) }} / {{ formatarValor(meta.meta) }}
    </div>
  </div>
</div>
```

**Visual specs (mini):**
- `.budget-grid`: `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))`, gap 12px
- `.budget-mini-card`: bg `--bg-card`, border-radius 12px, padding 14px, border-left 3px status color
- `.budget-mini-header`: flex, space-between, margin-bottom 8px
- `.budget-categoria`: `0.85rem` weight 600, `--text-primary`
- `.budget-pct`: `0.8rem` weight 700, status color
- `.budget-mini-bar`: height 6px, bg `rgba(255,255,255,0.08)`, border-radius 3px
- `.budget-mini-fill`: height 100%, border-radius 3px, status color
- `.budget-mini-values`: `0.8rem`, `--text-secondary`, margin-top 6px

---

## Interactions & Animations

### Progress bar fill animation
On mount/update, progress bar fills from 0% to actual percentage over 600ms with `ease-out`.

### Hover on category card
`translateY(-2px)`, shadow increase (same as existing stat-card.mini hover).

### Status change glow
When a category crosses 80% or 100% threshold (either by adding gasto or editing budget), card gets a temporary 1.5s pulse glow animation (reuse `@keyframes pulse-risco` from DashboardCharts with adapted color).

### Toast alert on gasto add (triggered from App.vue)
When user adds a gasto that causes a category to exceed 80% or 100%:
- Toast appears at bottom-right (or top-center)
- Background: status color with 10% opacity, border-left 4px status color
- Message: `"⚠️ Você atingiu 85% da meta para Restaurantes em Junho 2026"`
- Auto-dismiss after 5 seconds or click to close

### Modal open/close
- Open: backdrop fades in (200ms), card scales from 0.95 to 1 + fades in (300ms, ease-out)
- Close: reverse animation

---

## Responsive Behavior

**Desktop (> 768px):**
- Meta geral: full width, large
- Category grid: 2-3 columns
- Dashboard mini metas: 3-4 columns

**Mobile (≤ 768px):**
- Meta geral: single column, padding 20px, font sizes reduce slightly
- Category grid: single column
- Dashboard mini metas: 2 columns (or single if very narrow)
- Modal: 95vw, full height with scroll if needed

---

## Iconography

| Context | Icon | Source |
|---------|------|--------|
| Meta geral | `🎯` or `pi pi-bullseye` | Emoji / PrimeIcons |
| Category (default) | `🏷️` or `pi pi-tag` | Emoji / PrimeIcons |
| Edit | `pi pi-pencil` | PrimeIcons |
| Save | `pi pi-check` | PrimeIcons |
| Warning | `⚠️` | Emoji |
| Critical | `🔴` | Emoji |
| Success/under budget | `🟢` | Emoji |
| Close modal | `pi pi-times` | PrimeIcons |
| Add budget | `pi pi-plus` | PrimeIcons |

---

## Accessibility Notes

- Progress bars: add `aria-valuenow`, `aria-valuemin`, `aria-valuemax` to bar elements
- Color is not the only indicator: text percentage always visible, icons change (🟢→🟡→🔴)
- Focus states: inputs get green border on focus (`#22c55e`)
- Modal: trap focus inside, ESC to close, return focus to trigger button on close

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `frontend/src/components/BudgetView.vue` | Create | Main budget management view |
| `frontend/src/components/BudgetEditModal.vue` | Create | Modal for creating/editing budgets |
| `frontend/src/components/BudgetMiniBlock.vue` | Create (or inline) | Mini progress bars for dashboard |
| `frontend/src/App.vue` | Modify | Add "Metas" tab, integrate BudgetView, add toast on gasto add |
| `frontend/src/components/DashboardCharts.vue` | Modify | Add "Metas do Mês" block with mini progress bars |
| `frontend/src/config/api.js` | Modify | Add budget endpoints |
