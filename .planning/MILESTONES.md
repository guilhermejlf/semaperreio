# Milestones: Sem Aperreio

## Milestone: v1.0 MVP — Autenticação, Grupos Familiares e Dashboard Inteligente

**Shipped:** 2026-04-30
**Tag:** `v1.0`
**Phases:** 4 | **Plans:** 7
**Git range:** `fcf429b` → `8a0ac9f`
**Files changed:** 11 files, +1,314/-501 LOC
**Timeline:** 2026-04-24 → 2026-04-30 (6 days)

### What Was Built

1. **Autenticação JWT completa** — Registro, login, refresh token, logout. Frontend com interceptador automático e tela de login/cadastro em tema escuro.
2. **Grupos Familiares** — Criação com código de convite de 6 caracteres, expiração de 7 dias, papéis admin/member, gerenciamento de membros (expulsar, sair, deletar grupo).
3. **Dashboard Inteligente** — Filtro por mês/ano, comparativo mês atual vs. anterior, ranking de categorias, evolução 12 meses, insights automáticos, estado vazio amigável.
4. **ML com Dados Reais** — Previsão por categoria usando LinearRegression (scikit-learn), fallback para média com poucos dados, dados históricos de contexto.
5. **Exportação CSV/Excel** — StreamingHttpResponse para CSV, openpyxl para XLSX, respeitando filtros ativos.
6. **Tema Escuro Responsivo** — Interface unificada com PrimeIcons, cards modulares, drawer de grupo, dropdown de usuário.

### What Worked

- Lazy-load do modelo ML (on-demand training) evitou startup lento
- Deep-clone + deferred init resolveu o loop de reatividade do Chart.js
- Auto-refresh de token silencioso no frontend melhorou UX sem complexidade extra
- SQLite para MVP permitiu zero-config no desenvolvimento

### What Was Inefficient

- Implementação fora do workflow formal `/gsd-execute-phase` — SUMMARY.md criados manualmente depois
- Fases implementadas em um único commit (`8a0ac9f`) — dificulta rastreamento histórico
- Sem testes automatizados — só testes manuais

### Patterns Established

- FamilyMembership como OneToOneField per user (um user = uma family)
- Pre-join gastos permanecem privados (não retroativemente linkados)
- `data_competencia` como data efetiva com fallback para `data`
- Dashboard data computed on-demand (sem cache para MVP)

### Key Lessons

- Options API do Vue 3 é suficiente para MVPs pequenos; migração para Composition pode ser feita no v2
- On-demand ML training é aceitável para datasets pequenos (< 1000 registros); persistir modelo faz sentido para scale
- StreamingHttpResponse é essencial para exportação de CSV com grandes datasets
- ConfirmDialog + Toast (PrimeVue) padrão para ações destrutivas no frontend

### Cost Observations

- Modelo: balanced (Sonnet para execução)
- Sessions: ~4-5 sessões de desenvolvimento
- Notável: Fase de dashboard (charts + reatividade) consumiu mais tokens que as outras combinadas
