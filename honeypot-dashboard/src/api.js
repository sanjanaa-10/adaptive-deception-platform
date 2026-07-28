const BASE_URL = 'http://localhost:8000'

let token = localStorage.getItem('honeypot_token') || null

export function setToken(t) {
  token = t
  if (t) localStorage.setItem('honeypot_token', t)
  else localStorage.removeItem('honeypot_token')
}

export function getToken() {
  return token
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status}: ${body}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  decoys: () => request('/decoys/'),
  events: () => request('/events'),
  alerts: (resolved) => request(`/alerts/${resolved !== undefined ? `?resolved=${resolved}` : ''}`),
  resolveAlert: (id) =>
    request(`/alerts/${id}`, { method: 'PATCH', body: JSON.stringify({ resolved: true }) }),
  overview: () => request('/stats/overview'),
  timeseries: (days = 7) => request(`/stats/timeseries?days=${days}`),
}
