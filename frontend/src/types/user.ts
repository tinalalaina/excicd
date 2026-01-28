export type UserRole = 'CLIENT' | 'PRESTATAIRE' | 'ADMIN'

export interface UserInfo {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role: UserRole
}

export interface UserProfile {
  id: string
  first_name?: string
  last_name?: string
  phone?: string
  profession?: string
  residence?: string
  cin_number?: string
  address?: string
  date_of_birth?: string
  image?: string
  cin_photo_recto?: string
  cin_photo_verso?: string
}
