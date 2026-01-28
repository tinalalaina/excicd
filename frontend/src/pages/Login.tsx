import { FormEvent, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import Card from '../components/Card'
import FormField from '../components/FormField'

const Login = () => {
  const { login, error, isLoading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState<string | null>(null)

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setMessage(null)
    try {
      await login(email, password)
    } catch (err) {
      setMessage('Connexion impossible. Vérifiez vos informations.')
    }
  }

  return (
    <div className="page-grid">
      <Card title="Connexion">
        <form onSubmit={handleLogin} className="form-grid">
          <FormField label="Email" htmlFor="login-email">
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Mot de passe" htmlFor="login-password">
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </FormField>
          {message || error ? <div className="alert">{message ?? error}</div> : null}
          <button className="button button-primary" type="submit" disabled={isLoading}>
            {isLoading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      </Card>
    </div>
  )
}

export default Login
