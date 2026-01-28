import { createContext, ReactNode, useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchUserInfo, login as loginRequest, logout as logoutRequest } from '../api/userService'
import type { UserInfo, UserRole } from '../types/user'

interface AuthContextValue {
  user: UserInfo | null
  role: UserRole | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  displayName: string
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<UserInfo | null>
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const getDisplayName = (user: UserInfo | null) => {
  if (!user) {
    return ''
  }
  const name = [user.first_name, user.last_name].filter(Boolean).join(' ')
  return name || user.email || ''
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const role = user?.role ?? null
  const isAuthenticated = Boolean(localStorage.getItem('access_token'))

  const refreshUser = useCallback(async () => {
    setIsLoading(true)
    try {
      const info = await fetchUserInfo()
      setUser(info)
      setError(null)
      return info
    } catch (err) {
      setUser(null)
      setError('Impossible de charger le profil.')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      refreshUser().catch(() => undefined)
    } else {
      setIsLoading(false)
    }
  }, [isAuthenticated, refreshUser])

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true)
      try {
        const tokens = await loginRequest({ email, password })
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)
        const info = await refreshUser()
        if (info?.role === 'ADMIN') {
          navigate('/dashboard/admin', { replace: true })
        } else if (info?.role === 'PRESTATAIRE') {
          navigate('/dashboard/prestataire', { replace: true })
        } else {
          navigate('/dashboard/client', { replace: true })
        }
      } catch (err) {
        setError('Identifiants invalides. Merci de réessayer.')
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [navigate, refreshUser],
  )

  const logout = useCallback(async () => {
    try {
      await logoutRequest()
    } catch (err) {
      // ignore API errors on logout
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      navigate('/', { replace: true })
    }
  }, [navigate])

  const value = useMemo(
    () => ({
      user,
      role,
      isAuthenticated,
      isLoading,
      error,
      login,
      logout,
      refreshUser,
      displayName: getDisplayName(user),
    }),
    [user, role, isAuthenticated, isLoading, error, login, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
