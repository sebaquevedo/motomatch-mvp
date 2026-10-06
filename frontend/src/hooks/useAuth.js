import { useState } from 'react'
import { login as loginRequest } from '../services/auth'

export function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  const login = async (email, password) => {
    try {
      const accessToken = await loginRequest(email, password)
      if (accessToken) {
        localStorage.setItem('token', accessToken)
        setToken(accessToken)
        return true
      }
    } catch (err) {
      console.error('Login error:', err)
    }
    return false
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  return { token, login, logout, isAuthenticated: !!token }
}
