# Requirements: Sem Aperreio — v2.0 Production

**Defined:** 2026-04-30
**Core Value:** Familiares conseguem registrar e visualizar todos os gastos do lar em um só lugar, com análises claras que revelam padrões de consumo e oportunidades de economia.

---

## v2.0 Requirements

### Orçamento e Metas (BUDG)

- [x] **BUDG-01**: Usuário pode definir meta de gasto mensal por categoria (ex: "Mercado: R$ 500")
- [x] **BUDG-02**: Dashboard exibe progresso da meta com barra visual ("R$ 320 / R$ 500 (64%)")
- [x] **BUDG-03**: Alerta visual quando gasto ultrapassa 80% da meta; alerta crítico quando > 100% (toast + dashboard insights)

### Notificações (NOTF)

- [ ] **NOTF-01**: Sistema envia lembrete semanal para registrar gastos (email ou push)
- [ ] **NOTF-02**: Alerta automático quando gasto do mês ultrapassa média histórica + 20%

### Infraestrutura e Deploy (INFR)

- [ ] **INFR-01**: Migração SQLite → PostgreSQL para produção
- [ ] **INFR-02**: CI/CD com GitHub Actions (testes + lint + deploy)
- [ ] **INFR-03**: Deploy automatizado: backend Render/Railway + frontend Netlify/Vercel

---

## Future / Out of Scope for v2.0

| Feature | Reason |
|---------|--------|
| Integração bancária (Open Banking) | Complexidade regulatória e técnica muito alta |
| Multi-moeda (USD, EUR) | Público-alvo brasileiro; BRL suficiente |
| PWA com cache offline | Web responsive atende; offline não é crítico |
| Chat entre familiares | Fora do escopo de controle de gastos |
| Receitas / controle de renda | Foco em gastos; receitas adicionaria complexidade |
| ML avançado (clustering, anomalias) | LinearRegression atende previsão básica; modelos avançados para v3 |
| Multi-tenant / SaaS | Foco em família única por instância |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUDG-01 | Phase 5 | ✅ Done 2026-05-04 |
| BUDG-02 | Phase 5 | ✅ Done 2026-05-04 |
| BUDG-03 | Phase 5 | ✅ Done 2026-05-04 |
| NOTF-01 | Phase 6 | Pending |
| NOTF-02 | Phase 6 | Pending |
| INFR-01 | Phase 6 | Pending |
| INFR-02 | Phase 6 | Pending |
| INFR-03 | Phase 6 | Pending |

**Coverage:**
- v2.0 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✓

---

*Requirements defined: 2026-04-30 after v2.0 milestone initialization*
*Updated: 2026-05-04 — Phase 5 BUDG requirements completed*
