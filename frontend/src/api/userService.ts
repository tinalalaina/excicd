import api from './api'
import type { UserInfo, UserProfile } from '../types/user'

export interface LoginPayload {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
}

export interface RegisterPayload {
  first_name: string
  last_name: string
  email: string
  password: string
  password_confirm: string
  role: string
}

export interface RegisterResponse {
  message?: string
}

export const registerUser = async (payload: RegisterPayload) => {
  const { data } = await api.post<RegisterResponse>('/users/register/', payload)
  return data
}

export const login = async (payload: LoginPayload) => {
  const { data } = await api.post<LoginResponse>('/users/login/', payload)
  return data
}

export const logout = async () => {
  await api.post('/users/logout/')
}

export const fetchUserInfo = async () => {
  const { data } = await api.get<UserInfo>('/users/user-info/')
  return data
}

export const fetchProfile = async (userId: string) => {
  const { data } = await api.get<UserProfile>(`/users/profile/${userId}/`)
  return data
}

export const updateProfile = async (userId: string, payload: FormData) => {
  const { data } = await api.patch<UserProfile>(`/users/profile/${userId}/`, payload, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export const uploadProfilePhoto = async (userId: string, payload: FormData) => {
  const { data } = await api.post(`/users/profile/${userId}/photo/`, payload, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}
