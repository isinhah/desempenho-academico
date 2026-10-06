import { useEffect, useState } from 'react'
import { listarHistoricoCurso } from '../services/cursosApi'

export function useHistoricoCurso(cursoId) {
  const [historico, setHistorico] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    async function carregarHistorico() {
      setLoading(true)
      setError(null)
      try {
        const dados = await listarHistoricoCurso(cursoId, { signal: controller.signal })
        setHistorico(dados)
      } catch (requestError) {
        if (requestError.name !== 'AbortError') setError(requestError.message || 'Não foi possível carregar o histórico.')
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }

    carregarHistorico()
    return () => controller.abort()
  }, [cursoId])

  return { historico, loading, error }
}
