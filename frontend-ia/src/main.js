import { createApp } from 'vue'
import App from './App.vue'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

// 👇 NOVO JEITO (PrimeVue v4)
import Aura from '@primevue/themes/aura'

// ícones
import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
})

app.use(ToastService)
app.use(ConfirmationService)

app.mount('#app')