import { FormEvent, useEffect, useState } from 'react'
import Card from '../components/Card'
import FormField from '../components/FormField'
import Skeleton from '../components/Skeleton'
import { fetchProfile, updateProfile, uploadProfilePhoto } from '../api/userService'
import { useAuth } from '../hooks/useAuth'
import type { UserProfile } from '../types/user'

const Settings = () => {
  const { user, refreshUser } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [image, setImage] = useState<File | null>(null)
  const [cinRecto, setCinRecto] = useState<File | null>(null)
  const [cinVerso, setCinVerso] = useState<File | null>(null)

  useEffect(() => {
    const loadProfile = async () => {
      if (!user) {
        return
      }
      setLoading(true)
      try {
        const data = await fetchProfile(user.id)
        setProfile(data)
      } catch (err) {
        setMessage('Impossible de charger le profil.')
      } finally {
        setLoading(false)
      }
    }
    void loadProfile()
  }, [user])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!user) {
      return
    }
    setMessage(null)
    const formData = new FormData()
    if (profile?.first_name) {
      formData.append('first_name', profile.first_name)
    }
    if (profile?.last_name) {
      formData.append('last_name', profile.last_name)
    }
    if (profile?.phone) {
      formData.append('phone', profile.phone)
    }
    if (profile?.profession) {
      formData.append('profession', profile.profession)
    }
    if (profile?.residence) {
      formData.append('residence', profile.residence)
    }
    if (profile?.cin_number) {
      formData.append('cin_number', profile.cin_number)
    }
    if (profile?.address) {
      formData.append('address', profile.address)
    }
    if (profile?.date_of_birth) {
      formData.append('date_of_birth', profile.date_of_birth)
    }
    if (cinRecto) {
      formData.append('cin_photo_recto', cinRecto)
    }
    if (cinVerso) {
      formData.append('cin_photo_verso', cinVerso)
    }

    try {
      const updated = await updateProfile(user.id, formData)
      if (image) {
        const imageData = new FormData()
        imageData.append('photo', image)
        await uploadProfilePhoto(user.id, imageData)
      }
      setProfile(updated)
      await refreshUser()
      setMessage('Profil mis à jour.')
    } catch (err) {
      setMessage('Mise à jour échouée.')
    }
  }

  if (loading) {
    return (
      <div className="page-grid">
        <Card title="Chargement du profil">
          <Skeleton lines={4} />
        </Card>
      </div>
    )
  }

  return (
    <div className="page-grid">
      <Card title="Paramètres du compte">
        <form onSubmit={handleSubmit} className="form-grid">
          <FormField label="Profession" htmlFor="profession">
            <input
              id="profession"
              type="text"
              value={profile?.profession ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  profession: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Prénom" htmlFor="first-name">
            <input
              id="first-name"
              type="text"
              value={profile?.first_name ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  first_name: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Nom" htmlFor="last-name">
            <input
              id="last-name"
              type="text"
              value={profile?.last_name ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  last_name: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Téléphone" htmlFor="phone">
            <input
              id="phone"
              type="tel"
              value={profile?.phone ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  phone: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Résidence" htmlFor="residence">
            <input
              id="residence"
              type="text"
              value={profile?.residence ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  residence: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Numéro CIN" htmlFor="cin-number">
            <input
              id="cin-number"
              type="text"
              value={profile?.cin_number ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  cin_number: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Adresse" htmlFor="address">
            <input
              id="address"
              type="text"
              value={profile?.address ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  address: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Date de naissance" htmlFor="date-of-birth">
            <input
              id="date-of-birth"
              type="date"
              value={profile?.date_of_birth ?? ''}
              onChange={(event) =>
                setProfile((prev) => ({
                  ...(prev ?? { id: user?.id ?? '' }),
                  date_of_birth: event.target.value,
                }))
              }
            />
          </FormField>
          <FormField label="Photo de profil" htmlFor="profile-photo" hint="Formats acceptés : jpg, png">
            <input id="profile-photo" type="file" onChange={(event) => setImage(event.target.files?.[0] ?? null)} />
          </FormField>
          <FormField label="CIN recto" htmlFor="cin-recto">
            <input id="cin-recto" type="file" onChange={(event) => setCinRecto(event.target.files?.[0] ?? null)} />
          </FormField>
          <FormField label="CIN verso" htmlFor="cin-verso">
            <input id="cin-verso" type="file" onChange={(event) => setCinVerso(event.target.files?.[0] ?? null)} />
          </FormField>
          {message ? <div className="alert">{message}</div> : null}
          <button className="button button-primary" type="submit">
            Enregistrer
          </button>
        </form>
      </Card>
    </div>
  )
}

export default Settings
