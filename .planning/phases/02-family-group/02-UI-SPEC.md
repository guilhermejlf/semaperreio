# UI-SPEC: Phase 2 — Grupo Familiar (FamilyDrawer + Header)

**Phase:** 2 — Grupo Familiar | **Data:** 2026-04-27

---

## 1. Visão Geral

Drawer lateral direito (`FamilyDrawer.vue`) acionado por botão no header. Três estados: **sem grupo**, **membro**, **admin**. Grupo é opcional.

## 2. Header

### Sem Grupo
```
[Logo]          [Grupo ▾]  [Sair]
```
- Botão "Grupo" discreto, texto cinza #9ca3af, ícone `pi pi-users`

### Com Grupo
```
[Logo]  [Família Silva ●]  [Grupo ▾]  [Sair]
```
- Badge nome do grupo: fundo `rgba(34,197,94,0.15)`, texto #22c55e, borda 1px verde
- Ponto `●` verde solid indicando grupo ativo

## 3. Drawer — Sem Grupo

```
┌─────────────────────────────────────┐
│  Grupo Familiar              [X]    │
├─────────────────────────────────────┤
│  [Ícone pi pi-users, 48px, #4b5563]│
│  Você não está em nenhum grupo.     │
│  Crie ou entre em um para           │
│  compartilhar gastos.               │
│  [+ Criar Grupo Familiar]           │  ← btn primário verde, w-full
│  ─────────── ou ───────────         │
│  [Entrar com Código]                │  ← btn outline verde, w-full
└─────────────────────────────────────┘
```

**Botões:**
- Criar: `p-button severity="success" w-full`, fundo #22c55e, hover #16a34a
- Entrar: `p-button outlined severity="success" w-full`, borda #22c55e, texto #22c55e

## 4. Drawer — Form Criar Grupo

```
│  Nome do Grupo *                    │
│  ┌─────────────────────────────┐  │
│  │ Família Silva               │  │  ← InputText, fundo #1f2937
│  └─────────────────────────────┘  │
│  [Criar Grupo]                      │  ← verde w-full
│  [Cancelar]                         │  ← link cinza
```

## 5. Drawer — Form Entrar com Código

```
│  Código de Convite *                │
│  ┌─────────────────────────────┐  │
│  │ A3B7K9                      │  │  ← InputText, maxlength=6, uppercase
│  └─────────────────────────────┘  │
│  [Entrar no Grupo]                  │  ← verde w-full
│  [Cancelar]                         │
```

- Placeholder: "Ex: A3B7K9", transforma uppercase automaticamente

## 6. Drawer — Membro de Grupo

```
│  Família Silva                      │  ← font-bold text-lg
│  ─────────────────────────────────  │
│  Código de Convite                  │
│  ┌─────────────────────────────┐  │
│  │ A3B7K9            [Copiar] │  │  ← monospace, btn copiar sm
│  └─────────────────────────────┘  │
│  Expira em 5 dias                   │  ← #6b7280 text-sm
│  ─────────────────────────────────  │
│  Membros (3)                        │
│  ┌─────────────────────────────┐  │
│  │ ● Guilherme (Admin) [Você]  │  │
│  ├─────────────────────────────┤  │
│  │ ● Maria                     │  │
│  ├─────────────────────────────┤  │
│  │ ● João                      │  │
│  └─────────────────────────────┘  │
│  ─────────────────────────────────  │
│  [Sair do Grupo]                    │  ← outlined danger
│
```

**Membros:**
- Cada linha: avatar (inicial + cor baseada no nome) + nome + badge role
- Badge "Admin": fundo #22c55e, texto branco, font-xs
- Badge "Você": fundo #374151, texto #9ca3af

**Expiração código:**
- >24h: texto #6b7280 normal
- <24h: texto #f59e0b (amarelo)
- Expirado: texto #ef4444 + botão "Gerar Novo" (só admin)

## 7. Drawer — Admin de Grupo

Mesmo layout do membro, mas com ações extras:

```
│  ┌─────────────────────────────┐  │
│  │ ● Maria            [Expulsar]│  │  ← btn ícone vermelho, p-button-sm
│  ├─────────────────────────────┤  │
│  │ ● João             [Expulsar]│  │
│  └─────────────────────────────┘  │
│                                     │
│  [Gerar Novo Código]                │  ← btn outline verde
│  [Excluir Grupo]                    │  ← btn outlined danger
│  [Sair do Grupo]                    │
```

**Botões admin:**
- "Gerar Novo Código": `p-button outlined severity="success"`, regenera código com nova expiração
- "Excluir Grupo": `p-button outlined severity="danger"`, confirmação `ConfirmDialog` PrimeVue
- "Expulsar" membro: ícone `pi pi-trash`, tooltip "Expulsar", confirmação

**Confirmação excluir grupo:**
- Título: "Excluir Grupo?"
- Mensagem: "Todos os membros serão removidos e os gastos permanecerão vinculados apenas aos criadores."
- Botões: "Cancelar" / "Excluir" (vermelho)

**Confirmação sair do grupo (admin único):**
- Título: "Transferir Admin?"
- Mensagem: "Você é o único admin. Escolha um membro para transferir admin antes de sair."
- Select dropdown com membros + botões "Cancelar" / "Sair e Transferir"

## 8. Estilos Globais Drawer

- Drawer: `position="right"`, largura `w-96` (384px)
- Fundo: `#111827` (gray-900)
- Borda esquerda: 1px `#1f2937`
- Sombra: `-4px 0 15px rgba(0,0,0,0.3)`
- Títulos: branco `#ffffff`, `font-medium`
- Labels: `#9ca3af`, `text-sm`, `font-medium`
- Texto geral: `#d1d5db`
- Inputs: fundo `#1f2937`, borda `#374151`, texto branco
- Dividers: 1px `#374151`, com texto "ou" centralizado em #6b7280
- Padding geral: `p-4` (1rem)
- Gap entre seções: `gap-4`

## 9. Estados Vazios / Loading

**Loading:**
- Skeleton PrimeVue: 3 linhas de `p-skeleton` para membros
- Texto "Carregando grupo..."

**Erro:**
- Toast PrimeVue: `severity="error"`, sumário "Erro", detalhe da mensagem

## 10. Fluxo de Interação

```
Usuário clica "Grupo" no header
  → Drawer abre
    → Se sem grupo: mostra opções Criar/Entrar
      → Criar: expande form → submit → loading → sucesso → drawer recarrega (estado com grupo)
      → Entrar: expande form → submit → loading → sucesso → drawer recarrega
    → Se com grupo: mostra dados do grupo
      → Copiar código: toast "Código copiado!"
      → Sair: confirmação → saída → drawer recarrega (estado sem grupo)
      → Admin: expulsar (confirmação), gerar código, excluir grupo (confirmação)
```

## 11. Responsivo

- Desktop: drawer `w-96` fixo à direita
- Mobile (< 640px): drawer `w-full`, cobre tela toda
- Header em mobile: badge grupo truncado com `max-w-[120px] truncate`

---

*Next: 02-01-PLAN.md (backend) e 02-02-PLAN.md (frontend)*
