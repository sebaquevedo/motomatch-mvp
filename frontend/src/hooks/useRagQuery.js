import { useState } from 'react'
import api from '../services/api'

export function useRagQuery() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const query = async (question) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/query', { question })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return { query, loading, result, error }
}
