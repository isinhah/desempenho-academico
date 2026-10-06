const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

export async function listarCursos({ signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/cursos`, { signal })
  if (!response.ok) throw new Error(`Não foi possível carregar os cursos (HTTP ${response.status}).`)

  const cursos = await response.json()
  if (!Array.isArray(cursos)) throw new Error('A API retornou uma lista de cursos inválida.')
  return cursos
}

export async function obterCurso(id, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/cursos/${id}`, { signal })
  if (!response.ok) throw new Error(`Não foi possível carregar o curso (HTTP ${response.status}).`)
  return response.json()
}
