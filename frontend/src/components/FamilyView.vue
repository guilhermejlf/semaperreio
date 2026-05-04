<template>
  <div class="family-page">
    <!-- Loading -->
    <div v-if="loading" class="family-loading">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Carregando...</p>
    </div>

    <!-- Sem Grupo -->
    <div v-else-if="pageState === 'no-group'" class="family-empty">
      <i class="pi pi-users empty-icon"></i>
      <h3 class="empty-title">Nenhum grupo criado</h3>
      <p class="empty-sub">Crie um grupo ou entre em um existente para compartilhar gastos com sua família.</p>

      <button
        class="btn-primary"
        @click="pageState = 'create-form'"
      >
        Criar Grupo Familiar
      </button>

      <div class="divider">
        <span>ou</span>
      </div>

      <button
        class="btn-primary-outlined"
        @click="pageState = 'join-form'"
      >
        Entrar com Código
      </button>
    </div>

    <!-- Form Criar Grupo -->
    <div v-else-if="pageState === 'create-form'" class="family-form">
      <h3 class="family-title">Criar Grupo Familiar</h3>

      <div class="form-field">
        <label>Nome do Grupo <span class="required">*</span></label>
        <input
          v-model="newGroupName"
          type="text"
          class="native-input"
          placeholder="Ex: Família Silva"
          @keyup.enter="handleCreate"
        />
      </div>

      <button
        class="btn-primary"
        :disabled="actionLoading"
        @click="handleCreate"
      >
        {{ actionLoading ? 'Criando...' : 'Criar Grupo' }}
      </button>
      <button class="cancel-link" @click="pageState = 'no-group'">
        Cancelar
      </button>
    </div>

    <!-- Form Entrar com Código -->
    <div v-else-if="pageState === 'join-form'" class="family-form">
      <h3 class="family-title">Entrar em Grupo</h3>

      <div class="form-field">
        <label>Código de Convite <span class="required">*</span></label>
        <input
          v-model="joinCode"
          type="text"
          class="native-input code-input"
          placeholder="Ex: A3B7K9"
          maxlength="6"
          @input="joinCode = joinCode.toUpperCase()"
          @keyup.enter="handleJoin"
        />
      </div>

      <button
        class="btn-primary"
        :disabled="actionLoading"
        @click="handleJoin"
      >
        {{ actionLoading ? 'Entrando...' : 'Entrar no Grupo' }}
      </button>
      <button class="cancel-link" @click="pageState = 'no-group'">
        Cancelar
      </button>
    </div>

    <!-- Com Grupo -->
    <div v-else-if="pageState === 'has-group'" class="family-group">
      <h3 class="family-title">{{ familyData.name }}</h3>

      <!-- Código de Convite -->
      <div class="section">
        <label class="section-label">Código de Convite</label>
        <div class="code-box">
          <span class="code-text">{{ familyData.code }}</span>
          <button
            class="edit-btn"
            @click="copyCode"
            title="Copiar"
          >
            <i class="pi pi-copy"></i>
          </button>
        </div>
        <p class="expiration-text" :class="codeExpiringSoon ? 'expiring' : ''">
          {{ expirationText }}
        </p>
        <button
          v-if="isAdmin"
          class="btn-primary btn-sm mt-2"
          :disabled="actionLoading"
          @click="handleRegenerateCode"
        >
          {{ actionLoading ? 'Gerando...' : 'Gerar Novo Código' }}
        </button>
      </div>

      <!-- Membros -->
      <div class="section">
        <label class="section-label">Membros ({{ members.length }})</label>
        <div class="members-list">
          <BaseCard
            v-for="member in members"
            :key="member.id"
            :title="member.user.first_name || member.user.username"
            :subtitle="'@' + member.user.username"
          >
            <template #icon>
              <div class="member-avatar" :style="{ backgroundColor: getAvatarColor(member.user.username) }">
                {{ getInitials(member.user.first_name || member.user.username) }}
              </div>
            </template>
            <template #header-badge>
              <span v-if="isCurrentUser(member)" class="badge you">Você</span>
              <span v-if="member.role === 'admin'" class="badge admin">Admin</span>
            </template>
            <template #actions>
              <button
                v-if="isAdmin && !isCurrentUser(member)"
                class="delete-btn"
                title="Expulsar"
                @click="confirmExpel(member)"
              >
                <i class="pi pi-trash"></i>
              </button>
            </template>
          </BaseCard>
        </div>
      </div>

      <!-- Ações Admin -->
      <div v-if="isAdmin" class="section actions">
        <button
          class="btn-danger-outlined"
          @click="confirmDeleteGroup"
        >
          Excluir Grupo
        </button>
      </div>

      <!-- Sair do Grupo -->
      <div class="section actions">
        <button
          class="btn-danger-outlined"
          @click="confirmLeave"
        >
          Sair do Grupo
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import BaseCard from './BaseCard.vue'
import {
  createFamily,
  joinFamily,
  leaveFamily,
  regenerateFamilyCode,
  removeFamilyMember,
  deleteFamily
} from '../config/api.js'

export default {
  name: 'FamilyView',
  components: {
    ConfirmDialog,
    Toast,
    BaseCard
  },
  props: {
    family: {
      type: Object,
      default: null
    },
    currentUser: {
      type: Object,
      default: null
    }
  },
  emits: ['family-action'],
  data() {
    return {
      pageState: 'no-group',
      newGroupName: '',
      joinCode: '',
      loading: false,
      actionLoading: false
    }
  },
  computed: {
    familyData() {
      return this.family || null
    },
    members() {
      return this.familyData?.members || []
    },
    isAdmin() {
      if (!this.familyData || !this.currentUser) return false
      const me = this.members.find(m => m.user.id === this.currentUser.id)
      return me?.role === 'admin'
    },
    codeExpiringSoon() {
      if (!this.familyData?.code_expires_at) return false
      const expires = new Date(this.familyData.code_expires_at)
      const now = new Date()
      const diffHours = (expires - now) / (1000 * 60 * 60)
      return diffHours < 24
    },
    expirationText() {
      if (!this.familyData?.code_expires_at) return ''
      const expires = new Date(this.familyData.code_expires_at)
      const now = new Date()
      if (now > expires) return 'Código expirado'
      const diffDays = Math.ceil((expires - now) / (1000 * 60 * 60 * 24))
      return diffDays <= 1 ? 'Expira em menos de 24h' : `Expira em ${diffDays} dias`
    }
  },
  watch: {
    family: {
      immediate: true,
      handler(newVal) {
        this.updateState(newVal)
      }
    }
  },
  methods: {
    updateState(family) {
      if (family) {
        this.pageState = 'has-group'
      } else {
        this.pageState = 'no-group'
      }
      this.newGroupName = ''
      this.joinCode = ''
    },
    isCurrentUser(member) {
      return member.user.id === this.currentUser?.id
    },
    getInitials(name) {
      return name.charAt(0).toUpperCase()
    },
    getAvatarColor(str) {
      const colors = ['#f59e0b', '#3b82f6', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899', '#10b981', '#f97316']
      let hash = 0
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash)
      }
      return colors[Math.abs(hash) % colors.length]
    },
    async handleCreate() {
      const name = this.newGroupName.trim()
      if (!name) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: 'Digite um nome para o grupo.', life: 3000 })
        return
      }
      this.actionLoading = true
      try {
        const data = await createFamily(name)
        this.$emit('family-action', { action: 'created', data })
        this.$toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Grupo criado!', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: error.message, life: 3000 })
      } finally {
        this.actionLoading = false
      }
    },
    async handleJoin() {
      const code = this.joinCode.trim().toUpperCase()
      if (code.length !== 6) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: 'O código deve ter 6 caracteres.', life: 3000 })
        return
      }
      this.actionLoading = true
      try {
        const data = await joinFamily(code)
        this.$emit('family-action', { action: 'joined', data })
        this.$toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Você entrou no grupo!', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: error.message, life: 3000 })
      } finally {
        this.actionLoading = false
      }
    },
    async handleRegenerateCode() {
      this.actionLoading = true
      try {
        const data = await regenerateFamilyCode()
        this.$emit('family-action', { action: 'code-regenerated', data })
        this.$toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Novo código gerado!', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: error.message, life: 3000 })
      } finally {
        this.actionLoading = false
      }
    },
    async handleLeave() {
      this.actionLoading = true
      try {
        await leaveFamily()
        this.$emit('family-action', { action: 'left' })
        this.$toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Você saiu do grupo.', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: error.message, life: 3000 })
      } finally {
        this.actionLoading = false
      }
    },
    async handleExpel(member) {
      this.actionLoading = true
      try {
        await removeFamilyMember(member.user.id)
        this.$emit('family-action', { action: 'member-removed', data: member })
        this.$toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Membro removido.', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: error.message, life: 3000 })
      } finally {
        this.actionLoading = false
      }
    },
    async handleDeleteGroup() {
      this.actionLoading = true
      try {
        await deleteFamily()
        this.$emit('family-action', { action: 'deleted' })
        this.$toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Grupo excluído.', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Erro', detail: error.message, life: 3000 })
      } finally {
        this.actionLoading = false
      }
    },
    copyCode() {
      navigator.clipboard.writeText(this.familyData.code)
      this.$toast.add({ severity: 'success', summary: 'Copiado!', detail: 'Código copiado.', life: 2000 })
    },
    confirmLeave() {
      this.$confirm.require({
        message: 'Tem certeza que deseja sair do grupo? Se for o único membro, o grupo será excluído.',
        header: 'Sair do Grupo',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Sair',
        rejectLabel: 'Cancelar',
        acceptClass: 'p-button-danger',
        accept: this.handleLeave
      })
    },
    confirmDeleteGroup() {
      this.$confirm.require({
        message: 'Todos os membros serão removidos e os gastos permanecerão vinculados apenas aos criadores.',
        header: 'Excluir Grupo?',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Excluir',
        rejectLabel: 'Cancelar',
        acceptClass: 'p-button-danger',
        accept: this.handleDeleteGroup
      })
    },
    confirmExpel(member) {
      this.$confirm.require({
        message: `Remover ${member.user.first_name || member.user.username} do grupo?`,
        header: 'Expulsar Membro',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Remover',
        rejectLabel: 'Cancelar',
        acceptClass: 'p-button-danger',
        accept: () => this.handleExpel(member)
      })
    }
  }
}
</script>

<style scoped>
.family-page {
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.family-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: #9ca3af;
}

.family-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.empty-icon {
  font-size: 3rem;
  color: #4b5563;
}

.empty-title {
  color: #e5e7eb;
  font-weight: 500;
  margin: 0;
  font-size: 24px;
}

.empty-sub {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.divider {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 300px;
  gap: 0.75rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #374151;
}

.family-form,
.family-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.family-title {
  color: #ffffff;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
}

.required {
  color: #ef4444;
}

.native-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  color: #ffffff;
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.2s;
}

.native-input:focus {
  border-color: #22c55e;
}

.native-input::placeholder {
  color: #6b7280;
}

.code-input {
  font-family: monospace;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-size: 1.125rem;
}

.cancel-link {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.5rem;
  align-self: center;
}

.cancel-link:hover {
  color: #d1d5db;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-label {
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
}

.code-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
}

.code-text {
  font-family: monospace;
  font-size: 1.25rem;
  letter-spacing: 0.15em;
  color: #22c55e;
  font-weight: 600;
}

.expiration-text {
  color: #6b7280;
  font-size: 0.75rem;
  margin: 0.25rem 0 0 0;
}

.expiration-text.expiring {
  color: #f59e0b;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.admin {
  background: #22c55e;
  color: #ffffff;
}

.badge.you {
  background: #374151;
  color: #9ca3af;
}

.actions {
  padding-top: 0.5rem;
  border-top: 1px solid #374151;
}

.mt-2 {
  margin-top: 0.5rem;
}

.w-full {
  width: 100%;
}

/* Primary buttons matching 'Adicionar Primeiro Gasto' pattern */
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
  align-self: center;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-primary-outlined {
  background: transparent;
  color: white;
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  align-self: center;
}

.btn-primary-outlined::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  padding: 2px;
  background: linear-gradient(90deg, #22c55e, #3b82f6);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.btn-primary-outlined:hover {
  background: rgba(34, 197, 94, 0.08);
  transform: translateY(-2px);
}

.btn-sm {
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 10px;
}

.btn-danger-outlined {
  background: transparent;
  color: #ef4444;
  border: 2px solid #ef4444;
  border-radius: 12px;
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: center;
}

.btn-danger-outlined:hover {
  background: rgba(239, 68, 68, 0.1);
  transform: translateY(-2px);
}

</style>
