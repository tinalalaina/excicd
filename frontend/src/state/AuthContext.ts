import { createContext } from 'react'
import type { UserInfo, UserRole } from '../types/user'

export interface AuthContextValue {
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
