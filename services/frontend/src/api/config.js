const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '')

export function buildApiUrl(path) {
  if (!path.startsWith('/')) {
    return `${API_BASE_URL}/${path}`
  }

  return `${API_BASE_URL}${path}`
}
