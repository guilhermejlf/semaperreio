<template>
  <div class="page">

    <!-- AUTH VIEW -->
    <AuthView v-if="!isAuth" @authenticated="handleLoginSuccess" />

    <!-- APP CONTENT -->
    <template v-else>
    <!-- HEADER -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
          <img :src="logo" class="logo" />
          <h1 class="brand">Sem Aperreio</h1>
        </div>
        
        <div class="header-right">
        <nav class="nav-menu">
          <button 
            :class="['nav-item', { active: activeTab === 'dashboard' }]"
            @click="activeTab = 'dashboard'"
          >
            Dashboard
          </button>
          <button 
            :class="['nav-item', { active: activeTab === 'metas' }]"
            @click="activeTab = 'metas'"
          >
            <i class="pi pi-bullseye"></i>
            Metas
          </button>
          <button 
            :class="['nav-item', { active: activeTab === 'gastos' }]"
            @click="activeTab = 'gastos'"
          >
            Gastos
          </button>
          <button 
            :class="['nav-item', { active: activeTab === 'grupo' }]"
            @click="activeTab = 'grupo'"
          >
            Grupo
          </button>
          <button 
            :class="['nav-item', { active: activeTab === 'receitas' }]"
            @click="activeTab = 'receitas'"
          >
            Receitas
          </button>
        </nav>
        <div class="header-actions">
          <div v-if="currentUser" class="user-menu-wrapper">
            <button class="user-name" @click="showUserMenu = !showUserMenu">
              <span class="user-avatar">{{ (currentUser.first_name || currentUser.username || '?').charAt(0).toUpperCase() }}</span>
              <span class="user-label">{{ currentUser.first_name || currentUser.username }}</span>
              <i class="pi pi-chevron-down" :class="{ rotated: showUserMenu }"></i>
            </button>
            <div v-if="showUserMenu" class="user-dropdown">
              <div class="dropdown-header">
                <span class="user-avatar">{{ (currentUser.first_name || currentUser.username || '?').charAt(0).toUpperCase() }}</span>
                <div class="dropdown-info">
                  <span class="dropdown-name">{{ currentUser.first_name || currentUser.username }}</span>
                  <span class="dropdown-email">{{ currentUser.email || '' }}</span>
                </div>
              </div>
              <div class="dropdown-divider"></div>
              <div v-if="currentFamily" class="dropdown-group-info">
                <span class="group-label">Grupo</span>
                <span class="group-name">{{ currentFamily.name }}</span>
              </div>
              <div v-if="currentFamily" class="dropdown-divider"></div>
              <button @click="handleLogout" class="dropdown-item danger">
                <i class="pi pi-sign-out"></i>
                <span>Sair</span>
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </header>

    <!-- LOADING -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="pi pi-spin pi-spinner"></i>
        <p>Carregando...</p>
      </div>
    </div>

    <!-- ERROR MESSAGE -->
    <div v-if="error" class="error-message">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ error }}</span>
      <button @click="error = null" class="close-error">×</button>
    </div>

    <!-- MAIN CONTENT -->
    <main class="main-content">
      
      <!-- DASHBOARD TAB -->
      <div v-if="activeTab === 'dashboard'" class="tab-content">
        <DashboardCharts />
      </div>

      <!-- METAS TAB -->
      <div v-if="activeTab === 'metas'" class="tab-content">
        <BudgetView />
      </div>

      <!-- GASTOS TAB -->
      <div v-if="activeTab === 'gastos'" class="tab-content">
        <div class="gastos-container">
          <div v-if="gastos.length === 0" class="empty-state">
            <i class="pi pi-inbox"></i>
            <h3>Nenhum gasto cadastrado</h3>
            <p>Comece adicionando seu primeiro gasto para ver o dashboard completo!</p>
            <button @click="showAddModal = true" class="btn-primary">
              Adicionar Primeiro Gasto
            </button>
          </div>

          <div v-else>
            <div class="gastos-toolbar">
              <div v-if="currentFamily" class="gasto-filter-tabs">
                <button
                  :class="['filter-tab', { active: gastoFilter === 'todos' }]"
                  @click="gastoFilter = 'todos'"
                >
                  Todos ({{ gastos.length }})
                </button>
                <button
                  :class="['filter-tab', { active: gastoFilter === 'grupo' }]"
                  @click="gastoFilter = 'grupo'"
                >
                  Grupo ({{ gastosGrupo.length }})
                </button>
                <button
                  :class="['filter-tab', { active: gastoFilter === 'meus' }]"
                  @click="gastoFilter = 'meus'"
                >
                  Meus ({{ gastosMeus.length }})
                </button>
              </div>
              <button @click="showAddModal = true" class="btn-primary btn-sm">
                <i class="pi pi-plus"></i> Adicionar Gasto
              </button>
            </div>

            <div class="gastos-list">
              <div v-if="gastosFiltrados.length === 0" class="empty-filter">
                <p>Nenhum gasto nesta categoria.</p>
              </div>
              <BaseCard
                v-for="g in gastosFiltrados"
                :key="g.id"
                :icon="getCategoriaIcon(g.categoria)"
                :title="getCategoriaLabel(g.categoria)"
                :subtitle="formatarData(g.data)"
                :value="formatarValor(g.valor)"
                :isGroup="g.is_group"
              >
                <template #header-badge>
                  <span v-if="g.is_group" class="group-badge">Grupo</span>
                </template>
                <template #extras>
                  <small v-if="g.data_competencia && g.data_competencia !== g.data" class="gasto-desc">
                    Mês do gasto: {{ formatarData(g.data_competencia) }}
                  </small>
                  <small v-if="g.data_pagamento" class="gasto-desc">
                    Quando foi pago: {{ formatarData(g.data_pagamento) }}
                  </small>
                  <small v-if="g.descricao" class="gasto-desc">{{ g.descricao }}</small>
                </template>
                <template #meta>
                  <small v-if="g.user_name" class="gasto-user">@{{ g.user_name }}</small>
                </template>
                <template #badges>
                  <span v-if="g.pago" class="pago-badge">Pago</span>
                  <span v-else class="pendente-badge">Pendente</span>
                </template>
                <template #actions>
                  <template v-if="podeEditarGasto(g)">
                    <button @click="abrirEdicao(g)" class="edit-btn" title="Editar">
                      <i class="pi pi-pencil"></i>
                    </button>
                    <button @click="excluirGasto(g.id)" class="delete-btn" title="Excluir">
                      <i class="pi pi-trash"></i>
                    </button>
                  </template>
                </template>
              </BaseCard>
            </div>
          </div>
        </div>
      </div>

      <!-- GRUPO TAB -->
      <div v-if="activeTab === 'grupo'" class="tab-content">
        <FamilyView
          :family="currentFamily"
          :current-user="currentUser"
          @family-action="handleFamilyAction"
        />
      </div>

      <!-- RECEITAS TAB -->
      <div v-if="activeTab === 'receitas'" class="tab-content">
        <div class="gastos-container">
          <ReceitasView />
        </div>
      </div>

    </main>

    <!-- ADD/EDIT EXPENSE MODAL -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="fecharModal">
      <div class="modal-card">
        <div class="modal-header">
          <h2>{{ editingGasto ? 'Editar gasto' : 'Adicionar Novo Gasto' }}</h2>
          <button @click="fecharModal" class="modal-close">×</button>
        </div>

        <form @submit.prevent="editingGasto ? salvarEdicao() : adicionarGasto()" class="gasto-form">
          <div class="form-group">
            <label class="form-label">Valor</label>
            <InputNumber
              v-model="novo.valor"
              placeholder="R$ 0,00"
              mode="currency"
              currency="BRL"
              locale="pt-BR"
              :min="0.01"
              :maxFractionDigits="2"
              class="form-input"
              ref="inputValor"
              autofocus
            />
          </div>

          <div class="form-group">
            <label class="form-label">Onde você gastou?</label>
            <select v-model="novo.categoria" class="form-select">
              <option value="">Selecione uma categoria</option>
              <option v-for="cat in categorias" :key="cat.value" :value="cat.value">
                {{ cat.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Descrição</label>
            <InputText
              v-model="novo.descricao"
              placeholder="Ex: Mercado, Uber, McDonald's..."
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Mês do gasto</label>
            <input
              type="date"
              v-model="novo.data_competencia"
              class="form-input"
            />
          </div>

          <div class="form-group checkbox-group">
            <label class="form-checkbox">
              <input
                type="checkbox"
                v-model="novo.pago"
              />
              <span>Já paguei esse gasto</span>
            </label>
          </div>

          <div class="form-group" v-if="novo.pago">
            <label class="form-label">Quando foi pago</label>
            <input
              type="date"
              v-model="novo.data_pagamento"
              class="form-input"
            />
          </div>

          <Button
            type="submit"
            :label="editingGasto ? 'Salvar alterações' : 'Salvar gasto'"
            :icon="editingGasto ? 'pi pi-check' : 'pi pi-plus'"
            class="btn-submit"
            :disabled="loading || !formValido" />
        </form>
      </div>
    </div>

    <Toast position="top-right" />
    <ConfirmDialog />
  </template>
  </div>
</template>

<script>
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import DashboardCharts from './components/DashboardCharts.vue'
import AuthView from './components/AuthView.vue'
import FamilyView from './components/FamilyView.vue'
import ReceitasView from './components/ReceitasView.vue'
import BudgetView from './components/BudgetView.vue'
import BaseCard from './components/BaseCard.vue'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import logo from './assets/logo.png'
import {
  API_ENDPOINTS,
  API_BASE_URL,
  apiRequest,
  isAuthenticated,
  clearTokens,
  getFamily
} from './config/api.js'

export default {
  components: {
    Button,
    InputNumber,
    InputText,
    DashboardCharts,
    AuthView,
    FamilyView,
    ReceitasView,
    BudgetView,
    BaseCard,
    Toast,
    ConfirmDialog
  },

  data() {
    return {
      logo,
      isAuth: false,
      activeTab: 'dashboard',
      currentFamily: null,
      currentUser: null,
      showFamilyDrawer: false,
      showUserMenu: false,
      gastos: [],
      gastoFilter: 'todos', // 'todos' | 'grupo' | 'meus'
      novo: {
        valor: null,
        categoria: '',
        descricao: '',
        data: new Date().toISOString().split('T')[0],
        data_competencia: '',
        data_pagamento: '',
        pago: false
      },
      loading: false,
      error: null,
      showAddModal: false,
      editingGasto: null,
      categorias: [
        { value: 'moradia', label: 'Moradia' },
        { value: 'mercado', label: 'Mercado' },
        { value: 'restaurantes', label: 'Restaurantes / Delivery' },
        { value: 'transporte', label: 'Transporte' },
        { value: 'saude', label: 'Saúde' },
        { value: 'educacao', label: 'Educação' },
        { value: 'lazer', label: 'Lazer' },
        { value: 'contas', label: 'Contas e serviços' },
        { value: 'compras', label: 'Compras' },
        { value: 'outros', label: 'Outros' }
      ]
    }
  },

  computed: {
    gastosDoMes() {
      const mesAtual = new Date().getMonth() + 1
      const anoAtual = new Date().getFullYear()
      
      return this.gastos.filter(g => {
        const dataGasto = new Date(g.data)
        return dataGasto.getMonth() + 1 === mesAtual && 
               dataGasto.getFullYear() === anoAtual
      })
    },

    totalMes() {
      return this.gastosDoMes
        .reduce((soma, g) => soma + parseFloat(g.valor), 0)
    },

    formValido() {
      return this.novo.valor && 
             this.novo.valor > 0 && 
             this.novo.categoria && 
             this.novo.data_competencia
    },

    gastosGrupo() {
      return this.gastos.filter(g => g.is_group)
    },
    gastosMeus() {
      // Todos os gastos que EU criei (grupo ou individual)
      const myId = this.currentUser?.id
      return this.gastos.filter(g => g.user === myId)
    },
    gastosFiltrados() {
      if (this.gastoFilter === 'grupo') return this.gastosGrupo
      if (this.gastoFilter === 'meus') return this.gastosMeus
      return this.gastos
    }
  },

  async mounted() {
    this.isAuth = isAuthenticated()
    if (this.isAuth) {
      await this.fetchUser()
      await this.fetchFamily()
      this.carregarGastos()
    }
  },

  methods: {
    async carregarGastos() {
      try {
        this.loading = true
        this.error = null
        const data = await apiRequest(API_ENDPOINTS.GASTOS_LIST)
        this.gastos = data.gastos || []
      } catch (error) {
        this.error = 'Erro ao carregar gastos: ' + error.message
        console.error('Erro ao carregar gastos:', error)
      } finally {
        this.loading = false
      }
    },

    abrirEdicao(gasto) {
      this.novo = {
        valor: parseFloat(gasto.valor),
        categoria: gasto.categoria,
        descricao: gasto.descricao || '',
        data_competencia: gasto.data_competencia || '',
        data_pagamento: gasto.data_pagamento || '',
        pago: gasto.pago || false
      }
      this.editingGasto = gasto.id
      this.showAddModal = true
    },

    fecharModal() {
      this.showAddModal = false
      this.editingGasto = null
      this.novo = {
        valor: null,
        categoria: '',
        descricao: '',
        data_competencia: '',
        data_pagamento: '',
        pago: false
      }
    },

    async adicionarGasto() {
      try {
        this.loading = true
        this.error = null
        
        // Validação básica
        if (!this.novo.valor || this.novo.valor <= 0) {
          this.error = 'Informe um valor válido'
          return
        }
        
        if (!this.novo.data_competencia) {
          this.error = 'Informe o mês do gasto'
          return
        }

        const payload = { ...this.novo, data: this.novo.data_competencia || this.novo.data }
        const response = await apiRequest(API_ENDPOINTS.GASTOS_LIST, {
          method: 'POST',
          body: JSON.stringify(payload)
        })

        this.$toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Gasto adicionado!',
          life: 3000
        })

        if (response.alerta_meta) {
          this.$toast.add({
            severity: response.alerta_meta.status === 'critical' ? 'error' : 'warn',
            summary: 'Meta de Gastos',
            detail: response.alerta_meta.mensagem,
            life: 6000
          })
        }

        this.fecharModal()
        
        // Recarregar lista
        await this.carregarGastos()

      } catch (error) {
        this.error = 'Erro ao adicionar gasto: ' + error.message
        console.error('Erro ao adicionar gasto:', error)
      } finally {
        this.loading = false
      }
    },

    async salvarEdicao() {
      try {
        this.loading = true
        this.error = null

        if (!this.novo.valor || this.novo.valor <= 0) {
          this.error = 'Informe um valor válido'
          return
        }

        if (!this.novo.data_competencia) {
          this.error = 'Informe o mês do gasto'
          return
        }

        const payload = { ...this.novo, data: this.novo.data_competencia || this.novo.data }
        const response = await apiRequest(API_ENDPOINTS.GASTO_DETAIL(this.editingGasto), {
          method: 'PUT',
          body: JSON.stringify(payload)
        })

        this.$toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Gasto atualizado!',
          life: 3000
        })

        if (response.alerta_meta) {
          this.$toast.add({
            severity: response.alerta_meta.status === 'critical' ? 'error' : 'warn',
            summary: 'Meta de Gastos',
            detail: response.alerta_meta.mensagem,
            life: 6000
          })
        }

        this.fecharModal()
        await this.carregarGastos()

      } catch (error) {
        this.error = 'Erro ao editar gasto: ' + error.message
        console.error('Erro ao editar gasto:', error)
      } finally {
        this.loading = false
      }
    },

    formatarData(dataStr) {
      try {
        let processedDate = dataStr
        
        // Tratar diferentes formatos de data
        if (typeof dataStr === 'string') {
          // Se for formato YYYY-MM-DD (ISO date)
          if (/^\d{4}-\d{2}-\d{2}$/.test(dataStr)) {
            processedDate = dataStr + 'T12:00:00' // Adiciona hora para evitar timezone issues
          }
          // Se for formato ISO completo
          else if (dataStr.includes('T')) {
            // Mantém como está
          }
          // Se for outro formato, tenta converter
          else {
            const partes = dataStr.split('/')
            if (partes.length === 3) {
              // Formato DD/MM/YYYY -> YYYY-MM-DD
              processedDate = `${partes[2]}-${partes[1]}-${partes[0]}T12:00:00`
            }
          }
        }
        
        const data = new Date(processedDate)
        
        // Verificar se a data é válida
        if (isNaN(data.getTime())) {
          return 'Data inválida'
        }
        
        // Formatar para brasileiro
        return data.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: '2-digit', 
          year: 'numeric'
        })
      } catch (error) {
        console.error('Erro ao formatar data:', error, 'Input:', dataStr)
        return 'Data inválida'
      }
    },

    formatarValor(valor) {
      return parseFloat(valor).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      })
    },

    getCategoriaLabel(categoriaValue) {
      const categoria = this.categorias.find(c => c.value === categoriaValue)
      return categoria ? categoria.label : categoriaValue
    },

    podeEditarGasto(gasto) {
      // Se não tem usuário logado, não pode editar
      if (!this.currentUser) return false
      
      // Se o gasto é do próprio usuário, pode editar
      if (Number(gasto.user) === Number(this.currentUser.id)) return true
      
      // Se é admin do grupo, pode editar qualquer gasto do grupo
      if (this.currentFamily && this.currentFamily.user_role === 'admin') return true
      
      return false
    },

    getCategoriaIcon(categoria) {
      const icons = {
        moradia: '🏠',
        mercado: '🛒',
        restaurantes: '🍔',
        transporte: '🚗',
        saude: '🏥',
        educacao: '📚',
        lazer: '🎮',
        contas: '💡',
        compras: '🛍️',
        outros: '📦'
      }
      return icons[categoria] || '💳'
    },

    formatarTempo(dataStr) {
      try {
        const data = new Date(dataStr)
        
        // Verificar se a data é válida
        if (isNaN(data.getTime())) {
          return 'Data inválida'
        }
        
        const agora = new Date()
        const diffMs = agora - data
        const diffMin = Math.floor(diffMs / 60000)
        const diffHoras = Math.floor(diffMs / 3600000)
        const diffDias = Math.floor(diffMs / 86400000)

        if (diffMin < 1) return 'agora'
        if (diffMin < 60) return `${diffMin} min atrás`
        if (diffHoras < 24) return `${diffHoras}h atrás`
        if (diffDias < 7) return `${diffDias} dias atrás`
        
        return data.toLocaleDateString('pt-BR')
      } catch (error) {
        console.error('Erro ao formatar tempo:', error)
        return 'Data inválida'
      }
    },

    async excluirGasto(id) {
      this.$confirm.require({
        message: 'Tem certeza que deseja excluir este gasto?',
        header: 'Excluir Gasto',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Excluir',
        rejectLabel: 'Cancelar',
        acceptClass: 'p-button-danger',
        accept: async () => {
          try {
            this.loading = true
            this.error = null

            await apiRequest(API_ENDPOINTS.GASTO_DETAIL(id), {
              method: 'DELETE'
            })

            // Remove o gasto da lista localmente
            this.gastos = this.gastos.filter(g => g.id !== id)

            this.$toast.add({
              severity: 'success',
              summary: 'Sucesso',
              detail: 'Gasto excluído!',
              life: 3000
            })
          } catch (error) {
            this.error = 'Erro ao excluir gasto: ' + error.message
            console.error('Erro ao excluir gasto:', error)
          } finally {
            this.loading = false
          }
        }
      })
    },

    async handleLoginSuccess() {
      this.isAuth = true
      await this.fetchUser()
      await this.fetchFamily()
      this.carregarGastos()
    },

    async fetchUser() {
      try {
        const data = await apiRequest(API_ENDPOINTS.AUTH_USER)
        this.currentUser = data
      } catch (error) {
        console.warn('Não foi possível obter dados do usuário:', error)
      }
    },

    async fetchFamily() {
      try {
        this.currentFamily = await getFamily()
      } catch (error) {
        console.warn('Não foi possível obter dados da família:', error)
        this.currentFamily = null
      }
    },

    handleFamilyAction({ action }) {
      if (action === 'created' || action === 'joined') {
        this.fetchFamily()
        this.carregarGastos()
      } else if (action === 'left' || action === 'deleted') {
        this.currentFamily = null
        this.carregarGastos()
      } else if (action === 'code-regenerated' || action === 'member-removed') {
        this.fetchFamily()
      }
    },

    handleLogout() {
      clearTokens()
      this.isAuth = false
      this.activeTab = 'dashboard'
      this.gastos = []
      this.currentFamily = null
      this.currentUser = null
      this.showFamilyDrawer = false
      this.showUserMenu = false
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  background: radial-gradient(circle at top, #0f172a, #020617);
  color: white;
  padding: 40px 20px;
}

/* LOGO */
.logo-container {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  width: 90px;
}

.brand {
  font-size: 32px;
  background: linear-gradient(90deg, #a78bfa, #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tag {
  color: #94a3b8;
}

/* CARD */
.card {
  max-width: 420px;
  margin: auto;
  background: #0b1220;
  padding: 25px;
  border-radius: 18px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}

/* FORM */
.form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-group {
  display: flex;
  align-items: center;
  background: #020617;
  padding: 10px;
  border-radius: 10px;
}

.icon {
  margin-right: 10px;
}

/* BOTÃO */
.btn {
  margin-top: 10px;
  background: linear-gradient(90deg, #22c55e, #4ade80);
  border: none;
}

/* TOTAL */
.total-card {
  margin-top: 25px;
  padding: 15px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1e293b, #020617);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-card h2 {
  color: #22c55e;
}

.trend {
  font-size: 30px;
}

/* LISTA */
.lista {
  margin-top: 20px;
}

.item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #1e293b;
}

.left {
  display: flex;
  gap: 10px;
}

.circle {
  background: #22c55e;
  border-radius: 50%;
  padding: 8px;
}

.valor {
  color: #22c55e;
}

/* LOADING */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
  color: white;
}

.loading-spinner i {
  font-size: 2rem;
  margin-bottom: 10px;
}

/* ERROR MESSAGE */
.error-message {
  background: #dc2626;
  color: white;
  padding: 15px 20px;
  border-radius: 10px;
  margin: 20px auto;
  max-width: 600px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideIn 0.3s ease;
  box-shadow: 0 10px 30px rgba(220, 38, 38, 0.3);
}

.close-error {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  margin-left: auto;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.close-error:hover {
  opacity: 1;
}

/* MAIN CONTENT */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.tab-content {
  animation: fadeIn 0.5s ease;
}

/* HEADER */
.header {
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 2px;
}

.logo {
  width: 56px;
  height: 56px;
  border-radius: 8px;
}

.brand {
  font-size: 22px;
  font-weight: 600;
  color: white;
  margin: 0;
  background: none;
  -webkit-background-clip: initial;
  -webkit-text-fill-color: initial;
}

/* NAV MENU */
.nav-menu {
  display: flex;
  gap: 4px;
}

.nav-item {
  padding: 8px 16px;
  background: none;
  border: none;
  color: #94a3b8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  color: white;
  background: rgba(34, 197, 94, 0.15);
}

/* GASTOS CONTAINER */
.gastos-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gastos-container {
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.gastos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.gastos-header h2 {
  font-size: 28px;
  margin: 0;
  background: linear-gradient(90deg, #22c55e, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.gastos-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.stat-badge.primary {
  background: linear-gradient(90deg, #22c55e, #3b82f6);
}

/* EMPTY STATE */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 24px;
  margin: 20px 0 10px;
  color: #e5e7eb;
}

.empty-state p {
  margin: 0 0 30px;
  font-size: 16px;
  line-height: 1.6;
}

.btn-primary {
  background: linear-gradient(90deg, #22c55e, #3b82f6);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
}

.btn-primary.btn-sm {
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.gastos-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.gastos-toolbar .btn-sm {
  margin-left: auto;
}

.gasto-desc {
  color: #64748b;
  font-style: italic;
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
}

.gasto-time {
  color: #64748b;
  font-size: 11px;
}

.delete-btn {
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px;
  line-height: 1;
}

.delete-btn:hover {
  color: #3b82f6;
}

.edit-btn {
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px;
  line-height: 1;
}

.edit-btn:hover {
  color: #3b82f6;
}

/* GASTO FILTER TABS */
.gasto-filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.user-menu-wrapper {
  position: relative;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #d1d5db;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.06);
}

.user-name i.rotated {
  transform: rotate(180deg);
}

.user-name i {
  font-size: 11px;
  transition: transform 0.2s ease;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #22c55e;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-label {
  color: #d1d5db;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 8px;
  min-width: 240px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  z-index: 1000;
  animation: dropdownIn 0.15s ease;
}

@keyframes dropdownIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
}

.dropdown-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dropdown-name {
  color: #f3f4f6;
  font-size: 14px;
  font-weight: 500;
}

.dropdown-email {
  color: #6b7280;
  font-size: 12px;
}

.dropdown-divider {
  height: 1px;
  background: #374151;
  margin: 4px 0;
}

.dropdown-group-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}

.group-label {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.group-name {
  font-size: 13px;
  color: #22c55e;
  font-weight: 600;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  background: none;
  border: none;
  color: #d1d5db;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #f3f4f6;
}

.dropdown-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.filter-tab {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  color: #94a3b8;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #e5e7eb;
}

.filter-tab.active {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.group-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.gasto-user {
  display: block;
  margin-top: 4px;
  color: #64748b;
  font-size: 11px;
}

.pago-badge {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  background: linear-gradient(90deg, #22c55e, #4ade80);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
}

.pendente-badge {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  background: linear-gradient(90deg, #ef4444, #f87171);
  color: #ffffff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
}

.empty-filter {
  text-align: center;
  padding: 32px;
  color: #94a3b8;
  font-size: 14px;
}

/* FORM CONTAINER */
.form-container {
  max-width: 400px;
  margin: 0 auto;
}

.form-card {
  background: rgba(30, 41, 59, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.form-card h2 {
  text-align: center;
  margin: 0 0 24px 0;
  font-size: 22px;
  color: white;
  font-weight: 600;
}

.gasto-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  color: #e5e7eb;
  font-weight: 500;
  font-size: 13px;
}

.form-input,
.form-select {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: white;
  padding: 12px;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #22c55e;
  background: rgba(255, 255, 255, 0.05);
}

.form-select option {
  background: #1e293b;
  color: white;
}

.btn-submit {
  background: #22c55e;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  color: white;
  margin-top: 8px;
}

.btn-submit:hover:not(:disabled) {
  background: #16a34a;
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ANIMATIONS */
@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* HEADER RIGHT */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.25);
}

.logout-btn i {
  font-size: 14px;
}

/* FAMILY BUTTON */
.family-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid transparent;
  color: #9ca3af;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.family-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #d1d5db;
}

.family-btn.has-family {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.family-btn.has-family:hover {
  background: rgba(34, 197, 94, 0.15);
}

.family-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.family-dot {
  color: #22c55e;
  font-size: 10px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .header-content {
    padding: 12px 16px;
  }

  .logo {
    width: 34px;
    height: 34px;
  }

  .brand {
    font-size: 20px;
  }

  .header-right {
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .nav-item {
    padding: 6px 12px;
    font-size: 13px;
  }

  .logout-btn {
    padding: 6px 10px;
    font-size: 12px;
  }

  .main-content {
    padding: 20px 15px;
  }

  .gastos-container,
  .form-card {
    padding: 20px;
  }

  .gastos-header {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .nav-tabs {
    flex-direction: column;
    width: 100%;
  }

  .tab-btn {
    width: 100%;
    justify-content: center;
  }

  .logo-section {
    flex-direction: column;
  }

  .brand-section .brand {
    font-size: 20px;
  }
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

.modal-card {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 22px;
  background: linear-gradient(90deg, #22c55e, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.modal-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #94a3b8;
  font-size: 24px;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .modal-card {
    padding: 20px;
  }
}
</style>