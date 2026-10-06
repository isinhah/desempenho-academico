const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

export async function listarCursos({ escolaId, signal } = {}) {
  const query = escolaId ? `?${new URLSearchParams({ escola_id: escolaId })}` : ''
  const response = await fetch(`${API_BASE_URL}/cursos${query}`, { signal })
  if (!response.ok) throw new Error(`Não foi possível carregar os cursos (HTTP ${response.status}).`)

  const cursos = await response.json()
  if (!Array.isArray(cursos)) throw new Error('A API retornou uma lista de cursos inválida.')
  return cursos
}

export async function listarEscolas({ signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/escolas`, { signal })
  if (!response.ok) throw new Error(`Não foi possível carregar as escolas (HTTP ${response.status}).`)

  const escolas = await response.json()
  if (!Array.isArray(escolas)) throw new Error('A API retornou uma lista de escolas inválida.')
  return escolas
}

export async function obterCurso(id, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/cursos/${id}`, { signal })
  if (!response.ok) throw new Error(`Não foi possível carregar o curso (HTTP ${response.status}).`)
  return response.json()
}
