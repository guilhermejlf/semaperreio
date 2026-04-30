# Phase 5 Context: Orçamento e Metas

**Captured:** 2026-04-30 via `/gsd-discuss-phase 5`
**Status:** Ready for planning

---

## Vision

Usuários podem definir metas de gasto mensal por categoria E uma meta geral mensal. O dashboard exibe o progresso dessas metas em tempo real, com alertas visuais quando o gasto se aproxima ou ultrapassa o limite. Edição de metas é permitida, mas com confirmação explícita via modal para evitar mudanças acidentais.

## Essentials

### Metas por categoria + meta geral
- Cada categoria de gasto (Moradia, Mercado, Restaurantes, Transporte, etc.) pode ter uma meta mensal específica
- Além disso, existe uma meta geral mensal (total de todos os gastos)
- Ambas coexistem no mesmo sistema

### Metas por mês específico
- Usuário define meta para um mês/ano específico (ex: "Dezembro 2026: R$ 800 em Lazer")
- Não é meta recorrente automática — cada mês é configurado manualmente
- Interface mostra mês/ano selecionado para edição

### Alertas visuais duplos
1. **Barra de progresso no dashboard:** verde (< 50%), amarela (50–80%), vermelha (> 80%), crítica (> 100%)
2. **Toast/popup ao adicionar gasto:** quando o gasto adicionado faz a categoria ou total ultrapassar 80% ou 100% da meta

### Edição com confirmação
- Usuário pode editar uma meta já definida
- Antes de salvar, modal de confirmação aparece com mensagem: "Você já gastou R$ 450 de R$ 500. Alterar a meta para R$ 700?"
- Cancelar volta para a tela de edição sem salvar
- Confirmar salva a nova meta e atualiza o progresso em tempo real

## Boundaries

- NÃO: metas recorrentes automáticas (repetir todo mês) — fora do escopo v2.0
- NÃO: metas por família (compartilhadas) — por enquanto, cada usuário define suas próprias metas
- NÃO: notificação push/email para metas — isso é Phase 6 (Notificações)
- NÃO: histórico de metas anteriores — apenas meta atual do mês/ano
- NÃO: meta por semana — apenas mensal

## Decisions

| Decision | Rationale |
|----------|-----------|
| Meta geral + por categoria | Meta geral dá panorama; por categoria dá granularidade para ação |
| Mês específico (não recorrente) | Mais controle; evita "meta vazia" em meses sem planejamento |
| Alerta ao adicionar gasto (toast) | Feedback imediato no momento da ação mais relevante |
| Modal de confirmação na edição | Evita mudanças acidentais; aumenta conscientização do impacto |
| Apenas usuário próprio (não family-wide) | Simplifica MVP; family-wide pode ser v2.1 |

## UI Direction

- Nova aba "Metas" no app (ao lado de Dashboard, Gastos, Receitas, Grupo)
- Tela de metas: lista de categorias com meta atual + gasto realizado + barra de progresso
- Card de meta geral no topo (destaque visual)
- Seletor de mês/ano para navegar entre metas de diferentes períodos
- Botão "Definir Meta" por categoria (abre modal/form)
- Dashboard: mini progress bars nas categorias já existentes (ou novo card "Metas do Mês")

## Integration Points

- Reusa `DashboardCharts.vue` — adiciona card/barra de metas
- Reusa `api/views.py` `dashboard()` — adiciona dados de meta ao response
- Novo model `Budget`/`Meta` no backend
- Novo endpoint `/api/metas/` CRUD
