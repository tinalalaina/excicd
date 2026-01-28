import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import type { UserRole } from '../types/user'

interface RoleRouteProps {
  allowedRole: UserRole
  children: ReactNode
}

const RoleRoute = ({ allowedRole, children }: RoleRouteProps) => {
  const { role } = useAuth()

  if (role && role !== allowedRole) {
    if (role === 'ADMIN') {
      return <Navigate to="/dashboard/admin" replace />
    }
    if (role === 'PRESTATAIRE') {
      return <Navigate to="/dashboard/prestataire" replace />
    }
    return <Navigate to="/dashboard/client" replace />
  }

  return <>{children}</>
}

export default RoleRoute
