import { FormEvent, useState } from 'react'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { registerUser } from '../api/userService'

const Register = () => {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [role, setRole] = useState('CLIENT')
  const [message, setMessage] = useState<string | null>(null)

  const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setMessage(null)
    try {
      await registerUser({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        password_confirm: passwordConfirm,
        role,
      })
      setMessage('Compte créé. Vous pouvez vous connecter.')
    } catch {
      setMessage('Inscription échouée. Merci de réessayer.')
    }
  }

  return (
    <div className="page-grid">
      <Card title="Inscription">
        <form onSubmit={handleRegister} className="form-grid">
          <FormField label="Prénom" htmlFor="register-first-name">
            <input
              id="register-first-name"
              type="text"
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Nom" htmlFor="register-last-name">
            <input
              id="register-last-name"
              type="text"
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Email" htmlFor="register-email">
            <input
              id="register-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Mot de passe" htmlFor="register-password">
            <input
              id="register-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Confirmer le mot de passe" htmlFor="register-password-confirm">
            <input
              id="register-password-confirm"
              type="password"
              value={passwordConfirm}
              onChange={(event) => setPasswordConfirm(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Rôle" htmlFor="register-role">
            <select id="register-role" value={role} onChange={(event) => setRole(event.target.value)}>
              <option value="CLIENT">Client</option>
              <option value="PRESTATAIRE">Prestataire</option>
              <option value="ADMIN">Admin</option>
            </select>
          </FormField>
          {message ? <div className="alert">{message}</div> : null}
          <button className="button button-primary" type="submit">
            Créer mon compte
          </button>
        </form>
      </Card>
    </div>
  )
}

export default Register
