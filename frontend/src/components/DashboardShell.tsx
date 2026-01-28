import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

interface DashboardShellProps {
  title: string
  subtitle: string
  children: ReactNode
}

const DashboardShell = ({ title, subtitle, children }: DashboardShellProps) => {
  const { displayName, role, logout } = useAuth()

  const dashboardLink =
    role === 'ADMIN' ? '/dashboard/admin' : role === 'PRESTATAIRE' ? '/dashboard/prestataire' : '/dashboard/client'

  return (
    <section className="dashboard-shell">
      <aside className="dashboard-sidebar">
        <div className="avatar-circle" aria-hidden="true" />
        <div className="sidebar-profile">
          <strong>{displayName}</strong>
          <span>{role}</span>
        </div>
        <nav className="sidebar-links">
          <Link to={dashboardLink}>Tableau de bord</Link>
          <Link to="/settings">Paramètres</Link>
        </nav>
        <button className="button button-primary" onClick={() => void logout()}>
          Déconnexion
        </button>
      </aside>
      <div className="dashboard-main">
        <header className="dashboard-header">
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </header>
        <div className="dashboard-content">{children}</div>
      </div>
    </section>
  )
}

export default DashboardShell
