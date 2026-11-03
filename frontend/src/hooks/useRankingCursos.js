import { useCallback, useEffect, useState } from 'react'
import { listarCursos } from '../services/cursosApi'

export function useRankingCursos(escolaId, habilitado = true) {
  const [cursos, setCursos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [reloadKey, setReloadKey] = useState(0)
  const recarregar = useCallback(() => setReloadKey((key) => key + 1), [])

  useEffect(() => {
    if (!habilitado) return undefined

    const controller = new AbortController()
    async function carregarCursos() {
      setLoading(true)
      setError(null)
      try {
        const dados = await listarCursos({ escolaId, signal: controller.signal })
        setCursos(dados)
      } catch (requestError) {
        if (requestError.name !== 'AbortError') setError(requestError.message || 'Ocorreu um erro inesperado ao buscar os cursos.')
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    carregarCursos()
    return () => controller.abort()
  }, [escolaId, habilitado, reloadKey])

  return { cursos, loading, error, recarregar }
}
