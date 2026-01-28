import { FormEvent, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { requestPasswordReset, resetPassword } from '../api/userService'

const Login = () => {
  const { login, error, isLoading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [resetEmail, setResetEmail] = useState('')
  const [resetOtp, setResetOtp] = useState('')
  const [resetPasswordValue, setResetPasswordValue] = useState('')
  const [resetPasswordConfirm, setResetPasswordConfirm] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [resetMessage, setResetMessage] = useState<string | null>(null)

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setMessage(null)
    try {
      await login(email, password)
    } catch (err) {
      setMessage('Connexion impossible. Vérifiez vos informations.')
    }
  }

  const handleResetRequest = async () => {
    setResetMessage(null)
    try {
      await requestPasswordReset(resetEmail)
      setResetMessage('Un code OTP a été envoyé.')
    } catch (err) {
      setResetMessage('Impossible d’envoyer le code OTP.')
    }
  }

  const handleResetPassword = async () => {
    setResetMessage(null)
    try {
      await resetPassword({
        email: resetEmail,
        code: resetOtp,
        new_password: resetPasswordValue,
        new_password_confirm: resetPasswordConfirm,
      })
      setResetMessage('Mot de passe mis à jour. Vous pouvez vous connecter.')
    } catch (err) {
      setResetMessage('Réinitialisation échouée.')
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

      <Card title="Mot de passe oublié (OTP)">
        <div className="form-grid">
          <FormField label="Email" htmlFor="reset-email">
            <input
              id="reset-email"
              type="email"
              value={resetEmail}
              onChange={(event) => setResetEmail(event.target.value)}
            />
          </FormField>
          <button className="button" type="button" onClick={() => void handleResetRequest()}>
            Envoyer le code OTP
          </button>
          <FormField label="Code OTP" htmlFor="reset-otp">
            <input id="reset-otp" type="text" value={resetOtp} onChange={(event) => setResetOtp(event.target.value)} />
          </FormField>
          <FormField label="Nouveau mot de passe" htmlFor="reset-password">
            <input
              id="reset-password"
              type="password"
              value={resetPasswordValue}
              onChange={(event) => setResetPasswordValue(event.target.value)}
            />
          </FormField>
          <FormField label="Confirmer le mot de passe" htmlFor="reset-password-confirm">
            <input
              id="reset-password-confirm"
              type="password"
              value={resetPasswordConfirm}
              onChange={(event) => setResetPasswordConfirm(event.target.value)}
            />
          </FormField>
          {resetMessage ? <div className="alert">{resetMessage}</div> : null}
          <button className="button button-primary" type="button" onClick={() => void handleResetPassword()}>
            Réinitialiser le mot de passe
          </button>
        </div>
      </Card>
    </div>
  )
}

export default Login
