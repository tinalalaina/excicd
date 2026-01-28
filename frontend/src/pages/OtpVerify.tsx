import { FormEvent, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { verifyOtp } from '../api/userService'
import { useAuth } from '../hooks/useAuth'

interface LocationState {
  email?: string
}

const OtpVerify = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const state = location.state as LocationState | null
  const [email, setEmail] = useState(state?.email ?? '')
  const [otp, setOtp] = useState('')
  const [message, setMessage] = useState<string | null>(null)

  const handleVerify = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setMessage(null)
    try {
      const tokens = await verifyOtp({ email, code: otp, purpose: 'email_verification' })
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
      setMessage('Code OTP invalide ou expiré.')
    }
  }

  return (
    <div className="page-grid">
      <Card title="Validation du code OTP">
        <form onSubmit={handleVerify} className="form-grid">
          <FormField label="Email" htmlFor="otp-email">
            <input
              id="otp-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </FormField>
          <FormField label="Code OTP" htmlFor="otp-code">
            <input id="otp-code" type="text" value={otp} onChange={(event) => setOtp(event.target.value)} required />
          </FormField>
          {message ? <div className="alert">{message}</div> : null}
          <button className="button button-primary" type="submit">
            Valider et activer mon compte
          </button>
        </form>
      </Card>
    </div>
  )
}

export default OtpVerify
