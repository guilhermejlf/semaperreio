<template>
  <Sidebar
    v-model:visible="localVisible"
    position="right"
    class="family-drawer"
    :style="{ width: isMobile ? '100%' : '24rem' }"
  >
    <div class="drawer-content">
      <!-- Loading -->
      <div v-if="loading" class="drawer-loading">
        <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        <p>Carregando...</p>
      </div>

      <!-- Sem Grupo -->
      <div v-else-if="drawerState === 'no-group'" class="drawer-empty">
        <i class="pi pi-users empty-icon"></i>
        <p class="empty-text">Você não está em nenhum<br>grupo familiar.</p>
        <p class="empty-sub">Crie um grupo ou entre em um<br>existente para compartilhar<br>gastos com sua família.</p>

        <Button
          label="Criar Grupo Familiar"
          icon="pi pi-plus"
          severity="success"
          class="w-full"
          @click="drawerState = 'create-form'"
        />

        <div class="divider">
          <span>ou</span>
        </div>

        <Button
          label="Entrar com Código"
          severity="success"
          outlined
          class="w-full"
          @click="drawerState = 'join-form'"
        />
      </div>

      <!-- Form Criar Grupo -->
      <div v-else-if="drawerState === 'create-form'" class="drawer-form">
        <h3 class="drawer-title">Criar Grupo Familiar</h3>

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

        <Button
          label="Criar Grupo"
          severity="success"
          class="w-full"
          :loading="actionLoading"
          @click="handleCreate"
        />
        <button class="cancel-link" @click="drawerState = 'no-group'">
          Cancelar
        </button>
      </div>

      <!-- Form Entrar com Código -->
      <div v-else-if="drawerState === 'join-form'" class="drawer-form">
        <h3 class="drawer-title">Entrar em Grupo</h3>

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

        <Button
          label="Entrar no Grupo"
          severity="success"
          class="w-full"
          :loading="actionLoading"
          @click="handleJoin"
        />
        <button class="cancel-link" @click="drawerState = 'no-group'">
          Cancelar
        </button>
      </div>

      <!-- Com Grupo -->
      <div v-else-if="drawerState === 'has-group'" class="drawer-group">
        <h3 class="drawer-title">{{ familyData.name }}</h3>

        <!-- Código de Convite -->
        <div class="section">
          <label class="section-label">Código de Convite</label>
          <div class="code-box">
            <span class="code-text">{{ familyData.code }}</span>
            <Button
              icon="pi pi-copy"
              severity="success"
              text
              size="small"
              @click="copyCode"
              title="Copiar"
            />
          </div>
          <p class="expiration-text" :class="codeExpiringSoon ? 'expiring' : ''">
            {{ expirationText }}
          </p>
          <Button
            v-if="isAdmin"
            label="Gerar Novo Código"
            severity="success"
            outlined
            size="small"
            class="w-full mt-2"
            :loading="actionLoading"
            @click="handleRegenerateCode"
          />
        </div>

        <!-- Membros -->
        <div class="section">
          <label class="section-label">Membros ({{ members.length }})</label>
          <div class="members-list">
            <div
              v-for="member in members"
              :key="member.id"
              class="member-row"
            >
              <div class="member-avatar" :style="{ backgroundColor: getAvatarColor(member.user.username) }">
                {{ getInitials(member.user.first_name || member.user.username) }}
              </div>
              <div class="member-info">
                <span class="member-name">
                  {{ member.user.first_name || member.user.username }}
                  <span v-if="isCurrentUser(member)" class="badge you">Você</span>
                  <span v-if="member.role === 'admin'" class="badge admin">Admin</span>
                </span>
                <span class="member-username">@{{ member.user.username }}</span>
              </div>
              <Button
                v-if="isAdmin && !isCurrentUser(member)"
                icon="pi pi-trash"
                severity="danger"
                text
                size="small"
                title="Expulsar"
                @click="confirmExpel(member)"
              />
            </div>
          </div>
        </div>

        <!-- Ações Admin -->
        <div v-if="isAdmin" class="section actions">
          <Button
            label="Excluir Grupo"
            severity="danger"
            outlined
            class="w-full"
            @click="confirmDeleteGroup"
          />
        </div>

        <!-- Sair do Grupo -->
        <div class="section actions">
          <Button
            label="Sair do Grupo"
            severity="danger"
            outlined
            class="w-full"
            @click="confirmLeave"
          />
        </div>
      </div>
    </div>

  </Sidebar>
</template>

<script>
import Sidebar from 'primevue/sidebar'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import {
  createFamily,
  joinFamily,
  leaveFamily,
  regenerateFamilyCode,
  removeFamilyMember,
  deleteFamily
} from '../config/api.js'

export default {
  name: 'FamilyDrawer',
  components: {
    Sidebar,
    Button,
    ConfirmDialog,
    Toast
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    family: {
      type: Object,
      default: null
    },
    currentUser: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible', 'family-action'],
  data() {
    return {
      drawerState: 'no-group',
      newGroupName: '',
      joinCode: '',
      loading: false,
      actionLoading: false,
      isMobile: window.innerWidth < 640
    }
  },
  computed: {
    localVisible: {
      get() {
        return this.visible
      },
      set(val) {
        this.$emit('update:visible', val)
      }
    },
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
    },
    visible(newVal) {
      if (newVal) {
        this.updateState(this.family)
      }
    }
  },
  mounted() {
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    handleResize() {
      this.isMobile = window.innerWidth < 640
    },
    updateState(family) {
      if (family) {
        this.drawerState = 'has-group'
      } else {
        this.drawerState = 'no-group'
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
.drawer-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.drawer-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: #9ca3af;
}

.drawer-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
  padding: 1rem 0;
}

.empty-icon {
  font-size: 3rem;
  color: #4b5563;
}

.empty-text {
  color: #d1d5db;
  font-weight: 500;
  margin: 0;
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

.drawer-form,
.drawer-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.drawer-title {
  color: #ffffff;
  font-size: 1.125rem;
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
  gap: 0.5rem;
}

.member-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 0.5rem;
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

.member-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.member-name {
  color: #ffffff;
  font-size: 0.9375rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.member-username {
  color: #6b7280;
  font-size: 0.75rem;
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

:deep(.p-sidebar-content) {
  background: #111827;
  color: #d1d5db;
  padding: 0;
}

:deep(.p-sidebar-header) {
  background: #111827;
  border-bottom: 1px solid #1f2937;
  padding: 1rem;
}

:deep(.p-sidebar-header .p-sidebar-title) {
  color: #ffffff;
  font-weight: 600;
}

:deep(.p-sidebar-header .p-sidebar-close) {
  color: #9ca3af;
}

:deep(.p-sidebar-header .p-sidebar-close:hover) {
  color: #ffffff;
  background: #374151;
}
</style>
