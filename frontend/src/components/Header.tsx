import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const Header = () => {
  const { isAuthenticated, displayName, role, logout } = useAuth()

  return (
    <header className="app-header">
      <div className="header-left">
        <Link className="logo" to="/">
          AgroConnect
        </Link>
        {!isAuthenticated ? (
          <nav className="auth-links">
            <Link to="/login" className="button">
              Connexion
            </Link>
            <Link to="/register" className="button button-primary">
              Inscription
            </Link>
          </nav>
        ) : (
          <div className="profile-summary">
            <div>
              <strong>{displayName}</strong>
              <span>{role}</span>
            </div>
            <button className="button" onClick={() => void logout()}>
              Déconnexion
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
