'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'

interface User {
  user_id: string
  email: string
  role: string
}

interface Client {
  client_id: string
  client_name: string
  logo_url?: string
}

interface ClientContextType {
  user: User | null
  client: Client | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setClientData: (user: User, client: Client, token: string) => void
}

const ClientContext = createContext<ClientContextType | undefined>(undefined)

export function ClientProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [client, setClient] = useState<Client | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for stored token on mount - synchronously
    try {
      const storedToken = localStorage.getItem('token')
      const storedUser = localStorage.getItem('user')
      const storedClient = localStorage.getItem('client')

      if (storedToken && storedUser && storedClient) {
        const userData = JSON.parse(storedUser)
        const clientData = JSON.parse(storedClient)

        setToken(storedToken)
        setUser(userData)
        setClient(clientData)
        setIsAuthenticated(true)
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      }
    } catch (error) {
      // Clear invalid data
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('client')
      setIsAuthenticated(false)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { token, user, client_id, client_name, client_logo } = response.data

      const userData: User = {
        user_id: user.user_id,
        email: user.email,
        role: user.role,
      }

      const clientData: Client = {
        client_id,
        client_name,
        logo_url: client_logo,
      }

      // Store in state
      setToken(token)
      setUser(userData)
      setClient(clientData)
      setIsAuthenticated(true)

      // Store in localStorage
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('client', JSON.stringify(clientData))

      // Set axios default header
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Login failed')
    }
  }

  const logout = () => {
    // Clear state
    setToken(null)
    setUser(null)
    setClient(null)
    setIsAuthenticated(false)

    // Clear localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('client')

    // Clear axios header
    delete api.defaults.headers.common['Authorization']

    // Redirect to login
    router.push('/auth/login')
  }

  const setClientData = (userData: User, clientData: Client, tokenData: string) => {
    setUser(userData)
    setClient(clientData)
    setToken(tokenData)
    setIsAuthenticated(true)

    localStorage.setItem('token', tokenData)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('client', JSON.stringify(clientData))

    api.defaults.headers.common['Authorization'] = `Bearer ${tokenData}`
  }

  return (
    <ClientContext.Provider
      value={{
        user,
        client,
        token,
        isAuthenticated,
        isLoading,
        login,
        logout,
        setClientData,
      }}
    >
      {children}
    </ClientContext.Provider>
  )
}

export function useClient() {
  const context = useContext(ClientContext)
  if (context === undefined) {
    throw new Error('useClient must be used within a ClientProvider')
  }
  return context
}
