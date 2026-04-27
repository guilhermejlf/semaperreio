// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
export { API_BASE_URL }

export const API_ENDPOINTS = {
  // Auth
  AUTH_LOGIN: `${API_BASE_URL}/api/auth/login/`,
  AUTH_REGISTER: `${API_BASE_URL}/api/auth/register/`,
  AUTH_REFRESH: `${API_BASE_URL}/api/auth/refresh/`,
  AUTH_USER: `${API_BASE_URL}/api/auth/user/`,
  
  // Gastos
  GASTOS_LIST: `${API_BASE_URL}/api/gastos/`,
  GASTO_DETAIL: (id) => `${API_BASE_URL}/api/gastos/${id}/`,
  
  // Previsão
  PREVER_GASTO: `${API_BASE_URL}/api/prever/`,

  // Family
  FAMILY: `${API_BASE_URL}/api/family/`,
  FAMILY_JOIN: `${API_BASE_URL}/api/family/join/`,
  FAMILY_LEAVE: `${API_BASE_URL}/api/family/leave/`,
  FAMILY_REGENERATE_CODE: `${API_BASE_URL}/api/family/regenerate-code/`,
}

// Token storage keys
const TOKEN_KEY = 'sa_access_token'
const REFRESH_KEY = 'sa_refresh_token'

export function setTokens(access, refresh) {
  localStorage.setItem(TOKEN_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export function isAuthenticated() {
  return !!getAccessToken()
}

// Headers padrão
export const API_HEADERS = {
  'Content-Type': 'application/json',
}

// Função helper para requests (sem refresh automático — o executor decide)
export async function apiRequest(url, options = {}) {
  const token = getAccessToken()
  const headers = { ...API_HEADERS, ...options.headers }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config = {
    headers,
    ...options,
  }

  try {
    let response = await fetch(url, config)
    
    // Se 401 e tem refresh token, tenta refresh
    if (response.status === 401 && getRefreshToken()) {
      const refreshed = await tryRefreshToken()
      if (refreshed) {
        // Refaz o request original com novo token
        headers['Authorization'] = `Bearer ${getAccessToken()}`
        response = await fetch(url, { ...config, headers })
      }
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.erro || errorData.detail || `HTTP ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

export async function getFamily() {
  try {
    return await apiRequest(API_ENDPOINTS.FAMILY)
  } catch (error) {
    if (error.message && error.message.includes('404')) {
      return null
    }
    throw error
  }
}

export async function createFamily(name) {
  return await apiRequest(API_ENDPOINTS.FAMILY, {
    method: 'POST',
    body: JSON.stringify({ name })
  })
}

export async function joinFamily(code) {
  return await apiRequest(API_ENDPOINTS.FAMILY_JOIN, {
    method: 'POST',
    body: JSON.stringify({ code: code.toUpperCase() })
  })
}

export async function leaveFamily() {
  return await apiRequest(API_ENDPOINTS.FAMILY_LEAVE, {
    method: 'POST'
  })
}

export async function regenerateFamilyCode() {
  return await apiRequest(API_ENDPOINTS.FAMILY_REGENERATE_CODE, {
    method: 'POST'
  })
}

export async function removeFamilyMember(userId) {
  return await apiRequest(`${API_BASE_URL}/api/family/members/${userId}/`, {
    method: 'DELETE'
  })
}

export async function deleteFamily() {
  return await apiRequest(API_ENDPOINTS.FAMILY, {
    method: 'DELETE'
  })
}

async function tryRefreshToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false
  
  try {
    const response = await fetch(API_ENDPOINTS.AUTH_REFRESH, {
      method: 'POST',
      headers: API_HEADERS,
      body: JSON.stringify({ refresh: refreshToken })
    })
    
    if (!response.ok) {
      clearTokens()
      return false
    }
    
    const data = await response.json()
    if (data.access) {
      setTokens(data.access, data.refresh || refreshToken)
      return true
    }
    return false
  } catch (error) {
    console.error('Refresh token failed:', error)
    clearTokens()
    return false
  }
}
