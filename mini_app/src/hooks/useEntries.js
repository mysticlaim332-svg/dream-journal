import { useState, useEffect, useCallback } from 'react'
import { fetchMonthEntries, fetchStats } from '../lib/api'

/** Hook for calendar month data */
export function useMonthEntries(month) {
  const [data, setData] = useState({ entries: [], by_date: {} })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchMonthEntries(month)
      setData(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [month])

  useEffect(() => { load() }, [load])
  return { ...data, loading, error, reload: load }
}

/** Hook for insights / stats */
export function useStats() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { stats, loading, error }
}
