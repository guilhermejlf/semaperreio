<template>
  <div class="receitas-page">
    <!-- Loading -->
    <div v-if="loading" class="receitas-loading">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Carregando receitas...</p>
    </div>

    <!-- Conteúdo -->
    <template v-else>
      <!-- Lista -->
      <div v-if="receitas.length === 0" class="empty-state">
        <i class="pi pi-wallet empty-icon"></i>
        <h3>Nenhuma receita cadastrada</h3>
        <p>Comece adicionando sua primeira receita!</p>
        <button @click="abrirModal" class="btn-primary">
          Adicionar Primeira Receita
        </button>
      </div>

      <div v-else>
        <div class="receitas-toolbar">
          <div class="receitas-total">
            <span class="total-label">Total do período</span>
            <span class="total-value">{{ formatarValor(totalReceitas) }}</span>
          </div>
          <button @click="abrirModal" class="btn-primary btn-sm">
            <i class="pi pi-plus"></i> Nova Receita
          </button>
        </div>
        <div class="receitas-list">
          <BaseCard
          v-for="r in receitas"
          :key="r.id"
          :title="r.descricao || 'Receita'"
          :subtitle="formatarData(r.data)"
          :value="formatarValor(r.valor)"
          valueColor="#22c55e"
        >
          <template #meta>
            <small v-if="r.user_name" class="receita-user">@{{ r.user_name }}</small>
          </template>
          <template #actions>
            <template v-if="podeEditarReceita(r)">
              <button @click="abrirEdicao(r)" class="edit-btn" title="Editar">
                <i class="pi pi-pencil"></i>
              </button>
              <button @click="excluirReceita(r.id)" class="delete-btn" title="Excluir">
                <i class="pi pi-trash"></i>
              </button>
            </template>
          </template>
        </BaseCard>
      </div>
      </div>
    </template>

    <Toast position="top-right" />

    <!-- Modal Add/Edit Receita -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="fecharModal">
        <div class="modal-card">
          <div class="modal-header">
            <h2>{{ editingReceita ? 'Editar receita' : 'Nova Receita' }}</h2>
            <button @click="fecharModal" class="modal-close">×</button>
          </div>

          <form @submit.prevent="editingReceita ? salvarEdicao() : salvarReceita()" class="receita-form">
            <div class="form-group">
              <label class="form-label">Valor</label>
              <InputNumber
                v-model="nova.valor"
                placeholder="0,00"
                mode="currency"
                currency="BRL"
                locale="pt-BR"
                :min="0.01"
                :maxFractionDigits="2"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Descrição</label>
              <InputText
                v-model="nova.descricao"
                placeholder="Ex: Salário, Freelance..."
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Data</label>
              <input
                type="date"
                v-model="nova.data"
                class="form-input"
              />
            </div>

            <Button
              type="submit"
              :label="editingReceita ? 'Salvar alterações' : 'Adicionar Receita'"
              :icon="editingReceita ? 'pi pi-check' : 'pi pi-plus'"
              class="btn-submit"
              :disabled="loadingForm || !formValido" />
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Toast from 'primevue/toast'
import BaseCard from './BaseCard.vue'
import { fetchReceitas, addReceita, updateReceita, deleteReceita } from '../config/api.js'

export default {
  name: 'ReceitasView',
  components: {
    Button,
    InputNumber,
    InputText,
    Toast,
    BaseCard
  },
  data() {
    return {
      receitas: [],
      loading: false,
      loadingForm: false,
      showModal: false,
      editingReceita: null,
      nova: {
        valor: null,
        descricao: '',
        data: new Date().toISOString().split('T')[0]
      }
    }
  },
  computed: {
    totalReceitas() {
      return this.receitas.reduce((soma, r) => soma + parseFloat(r.valor || 0), 0)
    },
    formValido() {
      return this.nova.valor && this.nova.valor > 0 && this.nova.data
    }
  },
  mounted() {
    this.carregarReceitas()
  },
  methods: {
    async carregarReceitas() {
      try {
        this.loading = true
        const res = await fetchReceitas()
        this.receitas = res.receitas || []
      } catch (error) {
        console.error('Erro ao carregar receitas:', error)
      } finally {
        this.loading = false
      }
    },
    async salvarReceita() {
      if (!this.formValido) return
      try {
        this.loadingForm = true
        await addReceita({
          valor: this.nova.valor,
          descricao: this.nova.descricao,
          data: this.nova.data
        })
        this.fecharModal()
        await this.carregarReceitas()
        this.$toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Receita adicionada!',
          life: 3000
        })
      } catch (error) {
        console.error('Erro ao adicionar receita:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Erro',
          detail: 'Erro ao adicionar receita: ' + error.message,
          life: 5000
        })
      } finally {
        this.loadingForm = false
      }
    },
    async salvarEdicao() {
      if (!this.formValido) return
      try {
        this.loadingForm = true
        await updateReceita(this.editingReceita, {
          valor: this.nova.valor,
          descricao: this.nova.descricao,
          data: this.nova.data
        })
        this.fecharModal()
        await this.carregarReceitas()
        this.$toast.add({
          severity: 'success',
          summary: 'Sucesso',
          detail: 'Receita atualizada!',
          life: 3000
        })
      } catch (error) {
        console.error('Erro ao editar receita:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Erro',
          detail: 'Erro ao editar receita: ' + error.message,
          life: 5000
        })
      } finally {
        this.loadingForm = false
      }
    },
    abrirModal() {
      this.editingReceita = null
      this.nova = {
        valor: null,
        descricao: '',
        data: new Date().toISOString().split('T')[0]
      }
      this.showModal = true
    },
    abrirEdicao(receita) {
      this.nova = {
        valor: parseFloat(receita.valor),
        descricao: receita.descricao || '',
        data: receita.data
      }
      this.editingReceita = receita.id
      this.showModal = true
    },
    fecharModal() {
      this.showModal = false
      this.editingReceita = null
    },
    podeEditarReceita(receita) {
      // Simples: todas as receitas são editáveis pelo usuário logado
      // (receitas não têm family filter complexo como gastos)
      return true
    },
    excluirReceita(id) {
      this.$confirm.require({
        message: 'Tem certeza que deseja excluir esta receita?',
        header: 'Excluir Receita',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Sim, excluir',
        rejectLabel: 'Cancelar',
        acceptClass: 'p-button-danger',
        accept: async () => {
          try {
            await deleteReceita(id)
            this.receitas = this.receitas.filter(r => r.id !== id)
            this.$toast.add({
              severity: 'success',
              summary: 'Sucesso',
              detail: 'Receita excluída!',
              life: 3000
            })
          } catch (error) {
            console.error('Erro ao excluir receita:', error)
            this.$toast.add({
              severity: 'error',
              summary: 'Erro',
              detail: 'Erro ao excluir receita: ' + error.message,
              life: 5000
            })
          }
        }
      })
    },
    formatarValor(valor) {
      return parseFloat(valor).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      })
    },
    formatarData(dataStr) {
      if (!dataStr) return ''
      const data = new Date(dataStr + 'T00:00:00')
      return data.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.receitas-page {
  margin: 0 auto;
}

.receitas-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #9ca3af;
}

.receitas-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.receitas-total {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-label {
  font-size: 0.875rem;
  color: #9ca3af;
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #10b981;
}

.receitas-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.receita-user {
  color: #64748b;
  font-size: 11px;
  display: block;
}

.edit-btn,
.delete-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

/* Empty State */
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

.receita-form {
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

.form-input {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: white;
  padding: 12px;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: #22c55e;
  background: rgba(255, 255, 255, 0.05);
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

@media (max-width: 768px) {
  .receitas-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

}
</style>
