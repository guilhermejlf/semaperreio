# Sem Aperreio — Controle de Gastos Doméstico

## What This Is

Sistema web para controle de gastos domésticos onde integrantes de uma família se autenticam, registram seus gastos por categoria e visualizam dashboards com análises que ajudam a identificar onde estão gastando mais e como economizar.

## Core Value

Familiares conseguem registrar e visualizar todos os gastos do lar em um só lugar, com análises claras que revelam padrões de consumo e oportunidades de economia.

## Requirements

### Validated (v1.0 — shipped 2026-04-30)

- ✓ Cadastro de gastos com categorias — Phase 0 (código base existente)
- ✓ Dashboard com gráficos (pizza + linha) e estatísticas — Phase 0 (código base existente)
- ✓ Previsão de gastos por mês via ML — Phase 0 (código base existente, modelo fixo)
- ✓ Interface responsiva com tema escuro — Phase 0 (código base existente)
- ✓ **AUTH-01**: Usuários podem criar conta e fazer login (JWT) — v1.0
- ✓ **AUTH-02**: Gastos ficam vinculados ao usuário logado — v1.0
- ✓ **AUTH-03**: Usuários podem pertencer a um "grupo familiar" (compartilhar gastos) — v1.0
- ✓ **DASH-01**: Dashboard exibe gastos filtrados por período (mês/ano) — v1.0
- ✓ **DASH-02**: Ranking de categorias por valor total — v1.0
- ✓ **DASH-03**: Comparativo mês atual vs. mês anterior — v1.0
- ✓ **ML-01**: Modelo de previsão treinado com dados reais do usuário/família — v1.0
- ✓ **ML-02**: Previsão considera categoria (não apenas mês) — v1.0
- ✓ **EXP-01**: Exportar gastos para CSV/Excel — v1.0

### Active (v2.0)

- [ ] **BUDG-01**: Definir meta de gasto mensal por categoria
- [ ] **BUDG-02**: Dashboard exibe progresso da meta (barra visual)
- [ ] **BUDG-03**: Alerta visual quando gasto ultrapassa 80% da meta
- [ ] **NOTF-01**: Lembrete semanal para registrar gastos
- [ ] **NOTF-02**: Alerta quando gasto do mês ultrapassa média histórica
- [ ] **INFR-01**: PostgreSQL como banco de produção
- [ ] **INFR-02**: CI/CD com GitHub Actions
- [ ] **INFR-03**: Deploy automatizado backend + frontend

### Out of Scope

| Feature | Reason |
|---------|--------|
| Integração bancária (Open Banking) | Complexidade regulatória e técnica muito alta para MVP |
| Multi-moeda (USD, EUR) | Público-alvo brasileiro; BRL suficiente |
| PWA com cache offline | Web responsive atende; offline não é crítico para registro ocasional |
| Chat entre familiares | Fora do escopo de controle de gastos |

## Context

Sistema completo de controle de gastos domésticos com autenticação JWT, grupos familiares, dashboard com filtros por período (mês/ano), ranking de categorias, comparativo mês a mês, previsão via ML com dados reais, e exportação CSV/Excel. Backend Django + DRF, frontend Vue 3 + Vite, tema escuro, responsive. MVP v1.0 entregue com sucesso.

### Tech Stack (v1.0)

- **Backend**: Django 5.x + Django REST Framework + djangorestframework-simplejwt
- **Frontend**: Vue 3 (Options API) + Vite + Chart.js + PrimeIcons
- **ML**: scikit-learn (LinearRegression por categoria)
- **Banco**: SQLite (MVP), PostgreSQL planejado para produção
- **Export**: openpyxl (XLSX), csv/StreamingHttpResponse (CSV)

### Known Issues / Tech Debt

- Options API no Vue — Composition API seria mais moderna, mas MVP usou existente
- SQLite para produção — deve migrar para PostgreSQL antes do deploy real
- Modelo ML treinado on-demand — não persistido; recomenda-se cache ou Celery para datasets grandes
- Falta paginação completa com metadados (count/next/previous) — implementado apenas limite simples (50 itens)
- Sem testes automatizados — apenas testes manuais realizados

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

## Constraints

- **Tech Stack**: Manter Django + DRF + Vue 3 + Vite (código já existe)
- **Banco de Dados**: SQLite para MVP (fácil de rodar localmente), PostgreSQL para produção futura
- **ML Framework**: scikit-learn (já instalado, evitar adicionar peso)
- **Idioma**: Português brasileiro na interface e mensagens
- **Autenticação**: JWT via Django REST Framework SimpleJWT (padrão da comunidade)
- **Deploy**: Backend no Render/Railway, frontend no Netlify/Vercel (futuro)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Manter Options API no Vue | Código já usa Options API; migrar para Composition seria retrabalho sem ganho imediato | — Pending |
| SQLite para MVP | Zero configuração para desenvolvimento local; migração para PostgreSQL é trivial com Django | — Pending |
| Lazy-load do modelo ML | pickle carregado sob demanda; evita startup lento se arquivo ausente | ✓ Good |
| JWT ao invés de session cookies | Frontend SPA separado do backend; JWT facilita CORS e mobile futuro | — Pending |
| Grupo familiar (User → Family) | Um gasto pertence a um User que pertence a uma Family; permite múltiplos usuários verem os mesmos gastos | — Pending |

## Current Milestone: v2.0 Production

**Goal:** Transformar o MVP em produção com orçamento/metas, notificações e infraestrutura de deploy.

**Target features:**
- Orçamento e metas de gasto por categoria (BUDG-01/02/03)
- Notificações push/email (NOTF-01/02)
- PostgreSQL como banco de produção (INFR-01)
- CI/CD com GitHub Actions (INFR-02)
- Deploy automatizado backend + frontend (INFR-03)

**Key context:**
- SQLite → PostgreSQL migração requerida antes do deploy
- Sem testes automatizados — CI/CD deve incluir testes mínimos
- Options API no Vue pode ser mantido ou migrado no v2
- Deploy: Render/Railway (backend), Netlify/Vercel (frontend)

---
*Last updated: 2026-04-30 after v1.0 milestone completion and v2.0 initialization*
