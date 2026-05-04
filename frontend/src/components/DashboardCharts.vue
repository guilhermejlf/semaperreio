<template>
  <div class="dashboard">
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
      <p>Carregando...</p>
    </div>

    <!-- Estado Vazio -->
    <div v-else-if="dashboardData && dashboardData.quantidade_gastos === 0 && (dashboardData.total_receitas || 0) === 0" class="empty-state">
      <i class="pi pi-inbox"></i>
      <h3>Nenhum movimento neste período</h3>
      <p v-if="dashboardData.periodo">
        Adicione uma receita ou gasto para ver o dashboard de {{ dashboardData.periodo.mes_nome }} {{ dashboardData.periodo.ano }}.
      </p>
    </div>

    <!-- Conteúdo do Dashboard -->
    <template v-else-if="dashboardData">

      <!-- BLOCO 1 — SITUAÇÃO FINANCEIRA -->
      <div class="block-title">Situação Financeira</div>
      <div class="stats-grid bloco-situacao">
        <!-- Saldo (DESTAQUE) -->
        <div class="stat-card saldo-destaque" :class="[saldoClasse, { 'risco': saldoInsuficiente }]">
          <div class="stat-icon-saldo">{{ saldoInsuficiente ? '⚠️' : saldoIcone }}</div>
          <div class="stat-content">
            <p class="saldo-label">Saldo disponível</p>
            <h2 class="saldo-valor">{{ formatarValor(dashboardData.saldo || 0) }}</h2>
            <small v-if="saldoInsuficiente" class="saldo-aviso">Saldo pode não cobrir as contas pendentes</small>
            <small v-else>Receitas - Já pagos</small>
          </div>
        </div>

        <div class="stat-card mini receita">
          <div class="stat-icon">📈</div>
          <div class="stat-content">
            <h3>{{ formatarValor(dashboardData.total_receitas || 0) }}</h3>
            <p>Receitas no mês</p>
          </div>
        </div>

        <div class="stat-card mini gasto-pago">
          <div class="stat-icon">💸</div>
          <div class="stat-content">
            <h3>{{ formatarValor(dashboardData.total_gastos_pagos || 0) }}</h3>
            <p>Já pagos</p>
          </div>
        </div>

        <div class="stat-card mini gasto-pendente" v-if="(dashboardData.total_a_pagar || 0) > 0">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <h3>{{ formatarValor(dashboardData.total_a_pagar || 0) }}</h3>
            <p>Ainda a pagar</p>
            <small>{{ dashboardData.quantidade_pendentes || 0 }} conta{{ (dashboardData.quantidade_pendentes || 0) === 1 ? '' : 's' }}</small>
          </div>
        </div>
      </div>

      <!-- Previsão de Saldo -->
      <div v-if="dashboardData.previsao_mensagem" class="previsao-card" :class="{ 'negativa': (dashboardData.saldo_projetado || 0) < 0 }">
        <span class="previsao-icon">{{ (dashboardData.saldo_projetado || 0) < 0 ? '🔮' : '🔮' }}</span>
        <p>{{ dashboardData.previsao_mensagem }}</p>
      </div>

      <!-- Insights -->
      <div v-if="insights.length" class="insights-card">
        <div class="insights-header">💡 Insights</div>
        <ul class="insights-list">
          <li v-for="(insight, idx) in insights" :key="idx" :class="insight.tipo">
            {{ insight.mensagem }}
          </li>
        </ul>
      </div>

      <!-- BLOCO 2 — COMPORTAMENTO -->
      <div class="block-title">Comportamento</div>
      <div class="stats-grid bloco-comportamento">
        <div class="stat-card mini primary">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <h3>{{ formatarValor(dashboardData.total_mes || 0) }}</h3>
            <p>Total gasto no mês</p>
            <small>{{ dashboardData.quantidade_gastos || 0 }} registros</small>
          </div>
        </div>

        <div class="stat-card mini warning" v-if="categoriaDominante">
          <div class="stat-icon">🏆</div>
          <div class="stat-content">
            <h3>{{ categoriaDominante.nome }}</h3>
            <p>Seu maior foco de gastos</p>
            <small>{{ categoriaDominante.percentual }}% dos gastos</small>
          </div>
        </div>

        <div :class="['stat-card', 'mini', 'comparativo', variacaoClasse]" v-if="mostrarComparacao">
          <div class="stat-icon">{{ variacaoIcone }}</div>
          <div class="stat-content">
            <h3>{{ formatarVariacao(dashboardData.variacao_percentual) }}</h3>
            <p>Comparado ao mês passado</p>
            <small>{{ formatarValor(Math.abs(dashboardData.variacao_absoluta)) }}</small>
          </div>
        </div>
      </div>

      <!-- BLOCO 3 — METAS DO MÊS -->
      <div v-if="metasPorCategoria.length" class="block-title">Metas do Mês</div>
      <div v-if="metasPorCategoria.length" class="budget-mini-grid">
        <div
          v-for="meta in metasPorCategoria"
          :key="meta.id"
          class="budget-mini-card"
          :class="meta.status"
        >
          <div class="budget-mini-header">
            <span class="budget-categoria">{{ meta.categoria_nome }}</span>
            <span class="budget-pct" :class="meta.status">{{ meta.percentual_usado }}%</span>
          </div>
          <div class="budget-mini-bar">
            <div class="budget-mini-fill" :class="meta.status" :style="{width: Math.min(meta.percentual_usado, 100) + '%'}"></div>
          </div>
          <div class="budget-mini-values">
            {{ formatarValor(meta.gasto_realizado) }} / {{ formatarValor(meta.valor_meta) }}
          </div>
        </div>
      </div>

      <!-- Gráficos -->
      <div class="charts-grid">
        <div class="chart-container">
          <h3>Gastos por Categoria</h3>
          <div class="chart-wrapper">
            <canvas ref="categoriaChart"></canvas>
          </div>
        </div>

        <div class="chart-container">
          <h3>Evolução Mensal</h3>
          <div class="chart-wrapper">
            <canvas ref="evolucaoChart"></canvas>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import { fetchDashboard } from '../config/api.js'

Chart.register(...registerables)

const MES_NOMES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

export default {
  name: 'DashboardCharts',
  data() {
    const hoje = new Date()
    return {
      periodo: {
        mes: hoje.getMonth() + 1,
        ano: hoje.getFullYear()
      },
      dashboardData: null,
      loading: false,
      categoriaChart: null,
      evolucaoChart: null
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
    variacaoClasse() {
      if (!this.dashboardData) return 'neutral'
      return this.dashboardData.variacao_percentual <= 0 ? 'positive' : 'negative'
    },
    variacaoIcone() {
      if (!this.dashboardData) return '➖'
      return this.dashboardData.variacao_percentual <= 0 ? '↓' : '↑'
    },
    saldoClasse() {
      if (!this.dashboardData || this.dashboardData.saldo === undefined) return 'neutral'
      return this.dashboardData.saldo >= 0 ? 'positive' : 'negative'
    },
    saldoIcone() {
      if (!this.dashboardData || this.dashboardData.saldo === undefined) return '⚖️'
      return this.dashboardData.saldo >= 0 ? '🟢' : '🔴'
    },
    saldoInsuficiente() {
      if (!this.dashboardData) return false
      const saldo = this.dashboardData.saldo || 0
      const aPagar = this.dashboardData.total_a_pagar || 0
      return aPagar > 0 && saldo < aPagar
    },
    categoriaDominante() {
      const ranking = this.dashboardData?.ranking_categorias
      if (!ranking || ranking.length === 0) return null
      return ranking[0]
    },
    mostrarComparacao() {
      if (!this.dashboardData) return false
      const abs = Math.abs(this.dashboardData.variacao_absoluta || 0)
      return abs > 0.01
    },
    metasPorCategoria() {
      if (!this.dashboardData || !this.dashboardData.metas) return []
      const metas = this.dashboardData.metas.por_categoria || []
      return [...metas].sort((a, b) => b.percentual_usado - a.percentual_usado)
    },
    insights() {
      if (!this.dashboardData) return []
      const d = this.dashboardData
      const lista = []

      const receitas = d.total_receitas || 0
      const saldo = d.saldo || 0
      const variacao = d.variacao_percentual || 0
      const totalAPagar = d.total_a_pagar || 0
      const qtdPendentes = d.quantidade_pendentes || 0

      // Alerta 1: Contas pendentes
      if (totalAPagar > 0) {
        if (saldo < totalAPagar) {
          lista.push({
            tipo: 'alerta',
            mensagem: `Você ainda tem ${this.formatarValor(totalAPagar)} para pagar este mês. Seu saldo pode não ser suficiente.`
          })
        } else {
          lista.push({
            tipo: 'info',
            mensagem: `Você ainda tem ${this.formatarValor(totalAPagar)} para pagar este mês`
          })
        }
      }

      // Alerta 2: Muitas contas pendentes
      if (qtdPendentes >= 3) {
        lista.push({
          tipo: 'alerta',
          mensagem: `Você tem ${qtdPendentes} contas pendentes. Revise seus pagamentos.`
        })
      }

      // Insight 3: Metas ultrapassadas
      if (d.metas) {
        const metasGeral = d.metas.geral
        if (metasGeral && metasGeral.percentual_usado > 80) {
          lista.push({
            tipo: metasGeral.percentual_usado > 100 ? 'alerta' : 'warning',
            mensagem: `Meta geral: ${metasGeral.percentual_usado.toFixed(0)}% atingida (${this.formatarValor(metasGeral.gasto_realizado)} / ${this.formatarValor(metasGeral.valor_meta)})`
          })
        }
        const metasCriticas = (d.metas.por_categoria || [])
          .filter(m => m.percentual_usado > 80)
          .sort((a, b) => b.percentual_usado - a.percentual_usado)
          .slice(0, 2)
        metasCriticas.forEach(m => {
          lista.push({
            tipo: m.percentual_usado > 100 ? 'alerta' : 'warning',
            mensagem: `Meta ${m.categoria_nome}: ${m.percentual_usado.toFixed(0)}% atingida (${this.formatarValor(m.gasto_realizado)} / ${this.formatarValor(m.valor_meta)})`
          })
        })
      }

      // Insight 4: Variação vs mês anterior
      if (Math.abs(variacao) > 0.1) {
        lista.push({
          tipo: variacao > 0 ? 'alerta' : 'sucesso',
          mensagem: `Você gastou ${Math.abs(variacao).toFixed(1)}% ${variacao > 0 ? 'a mais' : 'a menos'} que no mês passado`
        })
      }

      // Limitar a 3 insights, priorizando alertas e warnings
      return lista
        .sort((a, b) => {
          const peso = { alerta: 4, warning: 3, info: 2, sucesso: 1 }
          return (peso[b.tipo] || 0) - (peso[a.tipo] || 0)
        })
        .slice(0, 3)
    }
  },
  mounted() {
    this.carregarDashboard()
  },
  watch: {
    periodo: {
      deep: true,
      handler() {
        this.carregarDashboard()
      }
    }
  },
  methods: {
    async carregarDashboard() {
      try {
        this.loading = true
        this.dashboardData = await fetchDashboard(this.periodo.mes, this.periodo.ano)
      } catch (error) {
        console.error('Erro ao carregar dashboard:', error)
      } finally {
        this.loading = false
        this.$nextTick(() => {
          this.destroyCharts()
          this.initCharts()
        })
      }
    },

    initCharts() {
      if (!this.dashboardData) return
      this.initCategoriaChart()
      this.initEvolucaoChart()
    },

    destroyCharts() {
      if (this.categoriaChart) {
        this.categoriaChart.destroy()
        this.categoriaChart = null
      }
      if (this.evolucaoChart) {
        this.evolucaoChart.destroy()
        this.evolucaoChart = null
      }
    },

    initCategoriaChart() {
      try {
        const ctx = this.$refs.categoriaChart
        if (!ctx) return

        if (this.categoriaChart) {
          this.categoriaChart.destroy()
          this.categoriaChart = null
        }

        const ranking = this.dashboardData.ranking_categorias
        if (!ranking || ranking.length === 0) return

        const cores = [
          '#f59e0b', '#3b82f6', '#8b5cf6', '#ef4444', '#06b6d4',
          '#ec4899', '#6b7280', '#10b981', '#f97316', '#6366f1'
        ]

        this.categoriaChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ranking.map(d => d.nome),
            datasets: [{
              data: ranking.map(d => d.total),
              backgroundColor: cores.slice(0, ranking.length),
              borderWidth: 2,
              borderColor: '#1f2937'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  color: '#e5e7eb',
                  padding: 15,
                  font: { size: 12 }
                }
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const value = this.formatarValor(context.parsed)
                    const total = context.dataset.data.reduce((a, b) => a + b, 0)
                    const percentage = ((context.parsed / total) * 100).toFixed(1)
                    return `${value} (${percentage}%)`
                  }
                }
              }
            }
          }
        })
      } catch (error) {
        console.error('Erro ao inicializar gráfico de categorias:', error)
      }
    },

    initEvolucaoChart() {
      try {
        const ctx = this.$refs.evolucaoChart
        if (!ctx) return

        if (this.evolucaoChart) {
          this.evolucaoChart.destroy()
          this.evolucaoChart = null
        }

        const evolucao = this.dashboardData.evolucao_mensal || this.dashboardData.evolucao_12meses || []
        const labels = evolucao.map(e => `${e.mes}/${e.ano.toString().slice(-2)}`)
        const dadosReceitas = evolucao.map(e => e.receitas || 0)
        const dadosGastos = evolucao.map(e => e.gastos || e.total || 0)

        this.evolucaoChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'Receitas',
                data: dadosReceitas,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#1f2937',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
              },
              {
                label: 'Gastos',
                data: dadosGastos,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.05)',
                borderWidth: 3,
                tension: 0.4,
                fill: false,
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#1f2937',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: {
                  color: '#e5e7eb',
                  font: { size: 12 },
                  usePointStyle: true
                }
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    return `${context.dataset.label}: ${this.formatarValor(context.parsed.y)}`
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                ticks: {
                  color: '#9ca3af',
                  callback: (value) => this.formatarValor(value)
                }
              },
              x: {
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                ticks: { color: '#9ca3af' }
              }
            }
          }
        })
      } catch (error) {
        console.error('Erro ao inicializar gráfico de evolução:', error)
      }
    },

    formatarValor(valor) {
      return parseFloat(valor).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      })
    },

    formatarVariacao(valor) {
      const sinal = valor > 0 ? '+' : ''
      return `${sinal}${valor.toFixed(1)}%`
    },

  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Títulos de bloco */
.block-title {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin: 24px 0 12px 0;
  padding-left: 4px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  gap: 16px;
  margin-bottom: 20px;
}

/* BLOCO 1: Situação Financeira */
.bloco-situacao {
  grid-template-columns: 1.5fr repeat(3, 1fr);
  align-items: stretch;
}

/* Saldo Destaque */
.saldo-destaque {
  grid-row: span 1;
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 20px;
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.saldo-destaque:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.saldo-destaque.positive {
  border-left: 6px solid #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), #1e293b);
}

.saldo-destaque.negative {
  border-left: 6px solid #ef4444;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), #1e293b);
}

.saldo-destaque .stat-icon-saldo {
  font-size: 3rem;
  flex-shrink: 0;
}

.saldo-destaque .stat-content {
  flex: 1;
}

.saldo-label {
  margin: 0 0 6px 0;
  color: #94a3b8;
  font-size: 0.95rem;
  font-weight: 500;
}

.saldo-valor {
  font-size: 2.4rem;
  font-weight: 800;
  margin: 0 0 6px 0;
  letter-spacing: -0.02em;
}

.saldo-destaque.positive .saldo-valor { color: #10b981; }
.saldo-destaque.negative .saldo-valor { color: #ef4444; }
.saldo-destaque.neutral .saldo-valor { color: #e5e7eb; }

/* Estado de risco: saldo insuficiente para contas pendentes */
.saldo-destaque.risco {
  border-left: 6px solid #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), #1e293b);
  animation: pulse-risco 2s ease-in-out infinite;
}

.saldo-destaque.risco .saldo-valor {
  color: #f59e0b;
}

.saldo-aviso {
  color: #fbbf24 !important;
  font-weight: 500;
}

@keyframes pulse-risco {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.2); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
}

.saldo-destaque .stat-content small {
  color: #94a3b8;
  font-size: 0.85rem;
}

/* Mini Cards */
.stat-card.mini {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card.mini:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.stat-card.mini .stat-icon {
  font-size: 1.8rem;
  opacity: 0.85;
  flex-shrink: 0;
}

.stat-card.mini .stat-content h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #e5e7eb;
}

.stat-card.mini .stat-content p {
  margin: 0 0 2px 0;
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-card.mini .stat-content small {
  color: #64748b;
  font-size: 0.8rem;
}

/* Cores por tipo */
.stat-card.receita { border-left: 4px solid #10b981; }
.stat-card.receita .stat-content h3 { color: #10b981; }

.stat-card.gasto-pago { border-left: 4px solid #ef4444; }
.stat-card.gasto-pago .stat-content h3 { color: #ef4444; }

.stat-card.gasto-pendente { border-left: 4px solid #f59e0b; }
.stat-card.gasto-pendente .stat-content h3 { color: #f59e0b; }

.stat-card.primary { border-left: 4px solid #3b82f6; }
.stat-card.primary .stat-content h3 { color: #3b82f6; }

.stat-card.warning { border-left: 4px solid #f59e0b; }
.stat-card.warning .stat-content h3 { color: #f59e0b; }

/* Comparativo */
.stat-card.comparativo.positive { border-left-color: #10b981; }
.stat-card.comparativo.positive .stat-content h3 { color: #10b981; }
.stat-card.comparativo.negative { border-left-color: #ef4444; }
.stat-card.comparativo.negative .stat-content h3 { color: #ef4444; }
.stat-card.comparativo.neutral { border-left-color: #6b7280; }

/* BLOCO 2: Comportamento */
.bloco-comportamento {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

/* Previsão Card */
.previsao-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), #1e293b);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 14px;
  padding: 16px 22px;
  margin-bottom: 20px;
  font-size: 0.95rem;
  color: #93c5fd;
  line-height: 1.5;
}

.previsao-card.negativa {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), #1e293b);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
  animation: pulse-risco 2.5s ease-in-out infinite;
}

.previsao-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.previsao-card p {
  margin: 0;
}

/* Insights Card */
.insights-card {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 20px 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
}

.insights-header {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
  margin-bottom: 12px;
}

.insights-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.insights-list li {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.95rem;
  line-height: 1.4;
}

.insights-list li.sucesso {
  background: rgba(16, 185, 129, 0.1);
  color: #34d399;
  border-left: 3px solid #10b981;
}

.insights-list li.alerta {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border-left: 3px solid #ef4444;
}

.insights-list li.info {
  background: rgba(59, 130, 246, 0.1);
  color: #93c5fd;
  border-left: 3px solid #3b82f6;
}

.insights-list li.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #fbbf24;
  border-left: 3px solid #f59e0b;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-top: 8px;
}

.chart-container {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-container h3 {
  margin: 0 0 18px 0;
  color: #e5e7eb;
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
}

.chart-wrapper {
  position: relative;
  height: 280px;
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

.period-select option {
  background: #1e293b;
  color: #e5e7eb;
}

/* Dashboard Loading */
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
.dashboard .empty-state {
  background: rgba(30, 41, 59, 0.3);
  border-radius: 20px;
  padding: 60px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
  }

  .bloco-situacao {
    grid-template-columns: 1fr;
  }

  .saldo-destaque {
    padding: 20px;
  }

  .saldo-valor {
    font-size: 1.8rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .bloco-comportamento {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .chart-wrapper {
    height: 240px;
  }

  .insights-card {
    padding: 16px;
  }

  .period-selector {
    flex-direction: column;
    align-items: stretch;
  }

  .period-select {
    width: 100%;
  }
}

/* Budget Mini Block */
.budget-mini-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.budget-mini-card {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border-radius: 12px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: 3px solid #10b981;
}

.budget-mini-card.ok { border-left-color: #10b981; }
.budget-mini-card.warning { border-left-color: #f59e0b; }
.budget-mini-card.danger { border-left-color: #ef4444; }
.budget-mini-card.critical { border-left-color: #dc2626; }

.budget-mini-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.budget-categoria {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e5e7eb;
}

.budget-pct {
  font-size: 0.8rem;
  font-weight: 700;
}

.budget-pct.ok { color: #10b981; }
.budget-pct.warning { color: #f59e0b; }
.budget-pct.danger { color: #ef4444; }
.budget-pct.critical { color: #dc2626; }

.budget-mini-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.budget-mini-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease-out;
}

.budget-mini-fill.ok { background: #10b981; }
.budget-mini-fill.warning { background: #f59e0b; }
.budget-mini-fill.danger { background: #ef4444; }
.budget-mini-fill.critical { background: #dc2626; }

.budget-mini-values {
  font-size: 0.8rem;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .budget-mini-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .budget-mini-grid {
    grid-template-columns: 1fr;
  }
}
</style>
