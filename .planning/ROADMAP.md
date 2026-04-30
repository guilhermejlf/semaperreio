# Roadmap: Sem Aperreio

**Project:** Sem Aperreio — Controle de Gastos Doméstico
**Defined:** 2026-04-24
**Current Milestone:** v2 — Orçamento, Notificações e Deploy

---

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-04-30)
- 🚧 **v2.0 Production** — Phases 5-6 (planned)

---

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-04-30</summary>

### Phase 1 — Autenticação JWT (2 plans)
- [x] Backend JWT: djangorestframework-simplejwt, endpoints auth
- [x] Frontend auth: telas login/cadastro, token storage, interceptador, logout

### Phase 2 — Grupo Familiar + Refatoração de Gastos (2 plans)
- [x] Backend: Family/FamilyMembership models, FamilyViewSet, gastos filtrados por family
- [x] Frontend: FamilyView.vue, drawer, badge no header, gerenciamento de membros

### Phase 3 — Dashboard Inteligente com Filtros (2 plans)
- [x] Backend: endpoint `/api/dashboard/` com agregações, ranking, comparativo
- [x] Frontend: seletor mês/ano, cards responsivos, gráficos Chart.js, estado vazio

### Phase 4 — ML com Dados Reais + Exportação (1 plan)
- [x] ML: previsão por categoria via LinearRegression, fallback média
- [x] Export: CSV (StreamingHttpResponse), XLSX (openpyxl)

See archive: `.planning/milestones/v1.0-ROADMAP.md`
</details>

### Phase 5 — Orçamento e Metas

**Goal:** Usuários podem definir metas de gasto por categoria e acompanhar progresso no dashboard.

**Depends on:** v1.0 (all phases)

**Requirements:** BUDG-01, BUDG-02, BUDG-03

**Deliverables:**
- Modelo `Budget` (categoria, valor meta, mês/ano, usuário/família)
- Endpoint CRUD de metas
- Dashboard: barra de progresso por categoria
- Alerta visual quando gasto ultrapassa 80% da meta

**Verification:**
- [ ] Usuário define meta de R$ 500 para "Mercado"
- [ ] Dashboard mostra progresso "R$ 320 / R$ 500 (64%)"
- [ ] Alerta aparece quando gasto > 80% da meta
- [ ] Alerta muda para crítico quando > 100%

---

### Phase 6 — Notificações e Deploy

**Goal:** Notificações push/email e infraestrutura de produção (PostgreSQL, CI/CD, deploy).

**Depends on:** Phase 5

**Requirements:** NOTF-01, NOTF-02, INFR-01, INFR-02, INFR-03

**Deliverables:**
- Lembrete semanal para registrar gastos (email ou push)
- Alerta quando gasto do mês ultrapassa média histórica
- Migração SQLite → PostgreSQL
- CI/CD GitHub Actions (testes + deploy)
- Deploy automatizado (backend Render/Railway, frontend Netlify/Vercel)

**Verification:**
- [ ] Notificação enviada semanalmente
- [ ] Alerta disparado quando gasto > média histórica + 20%
- [ ] PostgreSQL funcional em produção
- [ ] Push no main dispara deploy automático
- [ ] Frontend acessível via HTTPS

---

## Milestone Summary

| Milestone | Phases | Status |
|-----------|--------|--------|
| v1.0 | 1–4 | ✅ Shipped (2026-04-30) |
| v2.0 | 5–6 | � Planned |

---
*Last updated: 2026-04-30 after v1.0 milestone completion*
