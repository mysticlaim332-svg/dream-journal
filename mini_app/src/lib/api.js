/**
 * API client — calls our FastAPI backend.
 * Attaches Telegram initData as X-Init-Data header for auth.
 */
import { getInitData, getUserToken } from './telegram'

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

async function request(path, options = {}) {
  const initData = getInitData()
  const userToken = getUserToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (initData) headers['X-Init-Data'] = initData
  if (userToken) headers['X-User-Token'] = userToken

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'API error')
  }
  return res.json()
}

/** Fetch entries for a month. Returns { entries, by_date } */
export async function fetchMonthEntries(month) {
  const qs = month ? `?month=${month}` : ''
  return request(`/entries${qs}`)
}

/** Fetch single entry with full analysis + connections */
export async function fetchEntry(id) {
  return request(`/entries/${id}`)
}

/** Fetch stats */
export async function fetchStats() {
  return request('/stats')
}

/** Fetch patterns: recurring themes + AI connections */
export async function fetchPatterns() {
  return request('/patterns')
}
