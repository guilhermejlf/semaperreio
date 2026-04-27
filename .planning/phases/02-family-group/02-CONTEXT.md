# Phase 2 — Grupo Familiar: Decisões de Implementação

**Data:** 2026-04-27
**Fase anterior:** Phase 1 (Autenticação JWT) — concluída

---

## Decisões Firmes

### 1. Código de Convite
- **Formato:** 6 caracteres alfanuméricos maiúsculos (A-Z, 0-9), ex: `A3B7K9`
- **Expiração:** 7 dias após criação
- **Geração:** Automático na criação do grupo; pode ser regenerado pelo admin
- **Uso:** Outro usuário entra no grupo via `POST /api/family/join/` com o código

### 2. Quantidade de Grupos por Usuário
- **Apenas UM grupo por usuário.**
- Se usuário já está em um grupo e quer entrar em outro, precisa **sair do atual primeiro**.
- Modelo: `FamilyMembership` com `user` (unique=True) → um-para-um implícito.

### 3. Comportamento sem Grupo (Grupo Opcional)
- **Grupo é opcional.** Usuário sem grupo funciona normalmente, vendo **apenas seus próprios gastos** (comportamento atual da Phase 1).
- Dashboard, lista de gastos, adicionar gasto — tudo funciona sem grupo.
- Convite/criação de grupo é um upgrade, não um bloqueio.

### 4. Permissões de Admin vs Member
| Ação | Admin | Member |
|------|-------|--------|
| Ver gastos do grupo | Sim | Sim |
| Adicionar gasto no grupo | Sim | Sim |
| Excluir grupo | Sim | Não |
| Expulsar membros | Sim | Não |
| Editar gasto de outro membro | Sim (se gasto criado **depois** da entrada do membro no grupo) | Não |
| Deletar gasto de outro membro | Sim (se gasto criado **depois** da entrada do membro no grupo) | Não |
| Sair do grupo | Sim (mas se for o último admin, transfere ou deleta) | Sim |

**Regra de ouro:** Gastos criados **antes** de um membro entrar no grupo são **privados** ao criador (mesmo o admin não pode editar/deletar). Apenas gastos criados **depois** da entrada do membro no grupo são "compartilhados" e editáveis pelo admin.

### 5. Edição e Deleção de Gastos
- **Criador do gasto** pode editar/deletar **sempre** (mesmo se não for admin).
- **Admin do grupo** pode editar/deletar gastos de **outros membros** somente se o gasto foi criado **depois** da entrada do membro no grupo.
- **Member** não pode editar/deletar gastos de outros.

### 6. UI/UX do Grupo
- **Header** do app exibe:
  - Nome do grupo atual (se o usuário tem grupo)
  - Ícone/botão de "Gerenciar Grupo" (abre drawer/modal)
  - Se não tem grupo: botão discreto "Criar Grupo" ou "Entrar em Grupo"
- **Tela separada** (modal/drawer) de gerenciamento de grupo:
  - Nome do grupo, código de convite (com botão copiar/regenerar)
  - Lista de membros com roles (admin/member)
  - Opção de sair do grupo
  - Admin vê opções extras: expulsar membro, deletar grupo
- **Drawer** estilo PrimeVue `Sidebar` vindo da direita, tema escuro consistente com o app

---

## Modelos de Dados (Pré-decidido)

```python
class Family(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True)
    code_expires_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class FamilyMembership(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('member', 'Member')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
```

## Endpoints Pré-decididos

- `POST /api/family/` — Criar grupo (autenticado, sem grupo)
- `POST /api/family/join/` — Entrar em grupo via código (autenticado, sem grupo)
- `GET /api/family/` — Dados do grupo atual do usuário logado
- `DELETE /api/family/leave/` — Sair do grupo
- `DELETE /api/family/members/<user_id>/` — Expulsar membro (admin only)
- `DELETE /api/family/` — Deletar grupo (admin only)
- `POST /api/family/regenerate-code/` — Novo código de convite (admin only)

## Frontend Pré-decidido

- Componente `FamilyDrawer.vue` — Drawer PrimeVue com gerenciamento do grupo
- Store/estado local no `App.vue`: `currentFamily` (null se sem grupo)
- API helper: `getFamily()`, `createFamily()`, `joinFamily(code)`, `leaveFamily()`
- Header atualizado para mostrar badge do grupo (verde #22c55e quando ativo)

---

## Decisões Diferidas

- Convite por email/link (fora do escopo — só código por enquanto)
- Notificação quando alguém entra no grupo (futuro)
- Histórico de atividades do grupo (futuro)

## Referências

- Phase 1 Context: `.planning/phases/01-authentication/01-CONTEXT.md`
- Phase 1 Plan: `.planning/phases/01-authentication/01-01-PLAN.md`, `01-02-PLAN.md`
- ROADMAP: `.planning/ROADMAP.md` (Phase 2)
