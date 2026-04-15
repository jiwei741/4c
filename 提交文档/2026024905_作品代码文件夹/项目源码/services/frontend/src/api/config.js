const envBaseUrl = import.meta.env.VITE_API_BASE_URL
const rawBaseUrl = typeof envBaseUrl === 'string' ? envBaseUrl.trim() : ''

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '')

export function buildApiUrl(path) {
  if (!path.startsWith('/')) {
    return `${API_BASE_URL}/${path}`
  }

  return `${API_BASE_URL}${path}`
}
