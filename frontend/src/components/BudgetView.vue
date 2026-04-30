<template>
  <div class="budget-view">
    <!-- Seletor de Período -->
    <div class="period-selector">
      <select v-model="periodo.mes" class="period-select">
        <option v-for="(nome, idx) in mesesNomes" :key="idx" :value="idx + 1">{{ nome }}</option>
      </select>
      <select v-model="periodo.ano" class="period-select">
        <option v-for="ano in anosDisponiveis" :key="ano" :value="ano">{{ ano }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="dashboard-loading">
      <i class="pi pi-spin pi-spinner"></i>
      <p>Carregando metas...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!temMetas" class="empty-state">
      <i class="pi pi-bullseye"></i>
      <h3>Nenhuma meta definida</h3>
      <p v-if="periodo">
        Defina metas para acompanhar seus gastos de {{ mesNome }} {{ periodo.ano }}.
      </p>
      <button class="btn-primary" @click="abrirCriarMetaGeral">
        <i class="pi pi-plus"></i> Definir Meta Geral
      </button>
    </div>

    <!-- Conteúdo -->
    <template v-else>
      <!-- Meta Geral -->
      <div v-if="metaGeral" class="meta-geral-card" :class="metaGeral.status">
        <div class="meta-header">
          <span class="meta-icon">🎯</span>
          <span class="meta-titulo">Meta Geral — {{ mesNome }} {{ periodo.ano }}</span>
          <button class="btn-edit" @click="abrirEditar(metaGeral)">
            <i class="pi pi-pencil"></i>
          </button>
        </div>
        <div class="meta-valores">
          <span class="meta-gasto">{{ formatarValor(metaGeral.gasto_realizado) }}</span>
          <span class="meta-sep"> / </span>
          <span class="meta-meta">{{ formatarValor(metaGeral.valor_meta) }}</span>
        </div>
        <div class="meta-bar-container">
          <div class="meta-bar-fill" :class="metaGeral.status" :style="{width: pctClamped(metaGeral.percentual_usado) + '%'}"></div>
        </div>
        <div class="meta-footer">
          <span class="meta-pct" :class="metaGeral.status">{{ metaGeral.percentual_usado }}%</span>
          <span v-if="metaGeral.gasto_realizado > metaGeral.valor_meta" class="meta-aviso">
            🔴 Meta ultrapassada em {{ formatarValor(metaGeral.gasto_realizado - metaGeral.valor_meta) }}
          </span>
          <span v-else class="meta-restante">
            Restam {{ formatarValor(metaGeral.valor_meta - metaGeral.gasto_realizado) }} para o limite
          </span>
        </div>
      </div>

      <!-- Botão criar meta geral se não existir -->
      <div v-else class="criar-meta-geral">
        <button class="btn-primary" @click="abrirCriarMetaGeral">
          <i class="pi pi-plus"></i> Definir Meta Geral
        </button>
      </div>

      <!-- Bloco Categorias -->
      <div class="block-title">Metas por Categoria</div>
      <div class="categorias-grid">
        <div
          v-for="meta in metasPorCategoria"
          :key="meta.id"
          class="categoria-card"
          :class="meta.status"
        >
          <div class="categoria-header">
            <span class="categoria-nome">{{ categoriaEmoji(meta.categoria) }} {{ meta.categoria_nome }}</span>
            <button class="btn-edit" @click="abrirEditar(meta)">
              <i class="pi pi-pencil"></i>
            </button>
          </div>
          <div class="categoria-valores">
            <span class="categoria-gasto" :class="meta.status">{{ formatarValor(meta.gasto_realizado) }}</span>
            <span class="categoria-sep"> / </span>
            <span class="categoria-meta">{{ formatarValor(meta.valor_meta) }}</span>
          </div>
          <div class="categoria-bar-container">
            <div class="categoria-bar-fill" :class="meta.status" :style="{width: pctClamped(meta.percentual_usado) + '%'}"></div>
          </div>
          <div class="categoria-footer">
            <span class="categoria-pct" :class="meta.status">{{ meta.percentual_usado }}%</span>
            <span v-if="meta.gasto_realizado > meta.valor_meta" class="categoria-aviso">
              🔴 Meta ultrapassada
            </span>
            <span v-else-if="meta.percentual_usado > 80" class="categoria-aviso">
              ⚠️ {{ (100 - meta.percentual_usado).toFixed(0) }}% restante
            </span>
          </div>
        </div>

        <!-- Card para adicionar nova meta de categoria -->
        <div class="categoria-card nova-meta" @click="abrirCriarCategoria">
          <div class="nova-meta-content">
            <i class="pi pi-plus"></i>
            <span>Adicionar Meta de Categoria</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal -->
    <BudgetEditModal
      :visible="modalVisible"
      :meta="metaSelecionada"
      :periodo="periodo"
      @save="onSaveMeta"
      @cancel="modalVisible = false"
    />
  </div>
</template>

<script>
import { fetchMetas, createMeta, updateMeta } from '../config/api.js'
import BudgetEditModal from './BudgetEditModal.vue'

const MES_NOMES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

const CATEGORIA_EMOJIS = {
  'alimentacao': '🍔',
  'transporte': '🚗',
  'moradia': '🏠',
  'saude': '💊',
  'educacao': '📚',
  'lazer': '🎮',
  'vestuario': '👕',
  'servicos': '🔧',
  'outros': '📦'
}

export default {
  name: 'BudgetView',
  components: { BudgetEditModal },
  data() {
    const hoje = new Date()
    return {
      periodo: {
        mes: hoje.getMonth() + 1,
        ano: hoje.getFullYear()
      },
      metasData: { geral: null, por_categoria: [] },
      loading: false,
      modalVisible: false,
      metaSelecionada: null
    }
  },
  computed: {
    mesesNomes() {
      return MES_NOMES
    },
    anosDisponiveis() {
      const atual = new Date().getFullYear()
      return [atual, atual - 1, atual - 2]
    },
    mesNome() {
      return MES_NOMES[this.periodo.mes - 1]
    },
    temMetas() {
      return this.metaGeral || this.metasPorCategoria.length > 0
    },
    metaGeral() {
      return this.metasData && this.metasData.geral ? this.metasData.geral : null
    },
    metasPorCategoria() {
      const lista = (this.metasData && this.metasData.por_categoria) ? this.metasData.por_categoria : []
      return [...lista].sort((a, b) => (b.percentual_usado || 0) - (a.percentual_usado || 0))
    }
  },
  mounted() {
    this.carregarMetas()
  },
  watch: {
    periodo: {
      deep: true,
      handler() {
        this.carregarMetas()
      }
    }
  },
  methods: {
    async carregarMetas() {
      try {
        this.loading = true
        const data = await fetchMetas(this.periodo.mes, this.periodo.ano)
        const metas = data.metas || { geral: null, por_categoria: [] }
        // Normaliza: se API retornar lista plana, converte para objeto
        if (Array.isArray(metas)) {
          this.metasData = {
            geral: metas.find(m => m.categoria === null) || null,
            por_categoria: metas.filter(m => m.categoria !== null)
          }
        } else {
          this.metasData = metas
        }
      } catch (error) {
        console.error('Erro ao carregar metas:', error)
        this.metasData = { geral: null, por_categoria: [] }
      } finally {
        this.loading = false
      }
    },

    pctClamped(pct) {
      return Math.min(pct || 0, 100)
    },

    formatarValor(valor) {
      return parseFloat(valor || 0).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      })
    },

    categoriaEmoji(categoria) {
      return CATEGORIA_EMOJIS[categoria] || '🏷️'
    },

    abrirEditar(meta) {
      this.metaSelecionada = { ...meta, modo: 'editar' }
      this.modalVisible = true
    },

    abrirCriarMetaGeral() {
      this.metaSelecionada = {
        categoria: null,
        categoria_nome: 'Geral',
        valor_meta: '',
        mes: this.periodo.mes,
        ano: this.periodo.ano,
        modo: 'criar'
      }
      this.modalVisible = true
    },

    abrirCriarCategoria() {
      this.metaSelecionada = {
        categoria: '',
        categoria_nome: '',
        valor_meta: '',
        mes: this.periodo.mes,
        ano: this.periodo.ano,
        modo: 'criar_categoria'
      }
      this.modalVisible = true
    },

    async onSaveMeta(meta) {
      try {
        if (meta.id) {
          await updateMeta(meta.id, { valor_meta: meta.valor_meta })
        } else {
          await createMeta({
            categoria: meta.categoria,
            mes: meta.mes,
            ano: meta.ano,
            valor_meta: meta.valor_meta
          })
        }
        this.modalVisible = false
        this.carregarMetas()
      } catch (error) {
        console.error('Erro ao salvar meta:', error)
        alert(error.message || 'Erro ao salvar meta')
      }
    }
  }
}
</script>

<style scoped>
.budget-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Period Selector */
.period-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  justify-content: center;
}

.period-select {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 16px;
  color: #e5e7eb;
  font-size: 14px;
  cursor: pointer;
  min-width: 140px;
}

.period-select:focus {
  outline: none;
  border-color: #22c55e;
}

/* Meta Geral */
.meta-geral-card {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 20px;
  padding: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: 6px solid #10b981;
  margin-bottom: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.meta-geral-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.meta-geral-card.ok { border-left-color: #10b981; }
.meta-geral-card.warning { border-left-color: #f59e0b; }
.meta-geral-card.danger { border-left-color: #ef4444; }
.meta-geral-card.critical { border-left-color: #dc2626; }

.meta-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.meta-icon {
  font-size: 2rem;
}

.meta-titulo {
  flex: 1;
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
}

.btn-edit {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
}

.btn-edit:hover {
  color: #e5e7eb;
  background: rgba(255, 255, 255, 0.1);
}

.meta-valores {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: #e5e7eb;
}

.meta-gasto.ok { color: #10b981; }
.meta-gasto.warning { color: #f59e0b; }
.meta-gasto.danger { color: #ef4444; }
.meta-gasto.critical { color: #dc2626; }

.meta-sep {
  color: #64748b;
  font-weight: 400;
}

.meta-meta {
  color: #94a3b8;
  font-weight: 500;
}

.meta-bar-container {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 10px;
}

.meta-bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s ease-out;
}

.meta-bar-fill.ok { background: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.3); }
.meta-bar-fill.warning { background: #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.3); }
.meta-bar-fill.danger { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.3); }
.meta-bar-fill.critical { background: #dc2626; box-shadow: 0 0 12px rgba(220, 38, 38, 0.5); animation: pulse-critical 2s ease-in-out infinite; }

@keyframes pulse-critical {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.meta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.meta-pct {
  font-weight: 600;
}

.meta-pct.ok { color: #10b981; }
.meta-pct.warning { color: #f59e0b; }
.meta-pct.danger { color: #ef4444; }
.meta-pct.critical { color: #dc2626; }

.meta-restante {
  color: #94a3b8;
}

.meta-aviso {
  color: #f87171;
  font-weight: 500;
}

/* Categorias Grid */
.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.categoria-card {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid #10b981;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.categoria-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.categoria-card.ok { border-left-color: #10b981; }
.categoria-card.warning { border-left-color: #f59e0b; }
.categoria-card.danger { border-left-color: #ef4444; }
.categoria-card.critical { border-left-color: #dc2626; }

.categoria-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.categoria-nome {
  font-size: 1rem;
  font-weight: 600;
  color: #e5e7eb;
}

.categoria-valores {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #e5e7eb;
}

.categoria-gasto.ok { color: #10b981; }
.categoria-gasto.warning { color: #f59e0b; }
.categoria-gasto.danger { color: #ef4444; }
.categoria-gasto.critical { color: #dc2626; }

.categoria-sep {
  color: #64748b;
  font-weight: 400;
}

.categoria-meta {
  color: #94a3b8;
  font-weight: 500;
  font-size: 1rem;
}

.categoria-bar-container {
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.categoria-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease-out;
}

.categoria-bar-fill.ok { background: #10b981; }
.categoria-bar-fill.warning { background: #f59e0b; }
.categoria-bar-fill.danger { background: #ef4444; }
.categoria-bar-fill.critical { background: #dc2626; animation: pulse-critical 2s ease-in-out infinite; }

.categoria-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.categoria-pct {
  font-weight: 600;
}

.categoria-pct.ok { color: #10b981; }
.categoria-pct.warning { color: #f59e0b; }
.categoria-pct.danger { color: #ef4444; }
.categoria-pct.critical { color: #dc2626; }

.categoria-aviso {
  color: #fbbf24;
  font-weight: 500;
}

/* Nova Meta Card */
.nova-meta {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-left: 4px dashed rgba(255, 255, 255, 0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.nova-meta:hover {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.05);
}

.nova-meta-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-weight: 500;
}

.nova-meta-content i {
  font-size: 1.5rem;
}

/* Criar Meta Geral */
.criar-meta-geral {
  text-align: center;
  margin-bottom: 24px;
}

/* Buttons */
.btn-primary {
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 12px 24px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s, transform 0.2s;
}

.btn-primary:hover {
  background: #16a34a;
  transform: translateY(-1px);
}

/* Titles */
.block-title {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin: 24px 0 12px 0;
  padding-left: 4px;
}

/* Loading */
.dashboard-loading {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.dashboard-loading i {
  font-size: 2rem;
  margin-bottom: 12px;
  display: block;
}

/* Empty State */
.empty-state {
  background: rgba(30, 41, 59, 0.3);
  border-radius: 20px;
  padding: 60px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  color: #94a3b8;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
  color: #64748b;
}

.empty-state h3 {
  color: #e5e7eb;
  margin: 0 0 8px 0;
}

.empty-state p {
  margin: 0 0 20px 0;
}

/* Responsive */
@media (max-width: 768px) {
  .budget-view {
    padding: 12px;
  }

  .meta-geral-card {
    padding: 20px;
  }

  .meta-valores {
    font-size: 1.4rem;
  }

  .categorias-grid {
    grid-template-columns: 1fr;
  }

  .period-selector {
    flex-direction: column;
    align-items: stretch;
  }

  .period-select {
    width: 100%;
  }
}
</style>
