import { supabase } from './supabase'

const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

export async function requisicaoAutenticada(caminho, options = {}) {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token

  if (!token) throw new Error('Sua sessão expirou. Entre novamente para continuar.')

  return fetch(`${API_BASE_URL}${caminho}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  })
}
