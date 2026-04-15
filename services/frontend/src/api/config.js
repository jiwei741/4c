const envBaseUrl = import.meta.env.VITE_API_BASE_URL
const rawBaseUrl = typeof envBaseUrl === 'string' ? envBaseUrl.trim() : ''

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '')

export function buildApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  if (!API_BASE_URL) {
    return normalizedPath
  }

  // Guard against release builds that proxy `/api/*` while callers already
  // request `/api/v1/*`. This keeps production and local dev aligned.
  if (API_BASE_URL.endsWith('/api') && normalizedPath.startsWith('/api/')) {
    return `${API_BASE_URL}${normalizedPath.slice(4)}`
  }

  return `${API_BASE_URL}${normalizedPath}`
}
