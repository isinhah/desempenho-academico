import { useEffect, useState } from 'react'
import { obterCurso } from '../services/cursosApi'

export function useCurso(cursoId) {
  const [curso, setCurso] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  useEffect(() => {
    const controller = new AbortController()
    async function carregarCurso() {
      setLoading(true); setError(null)
      try { setCurso(await obterCurso(cursoId, { signal: controller.signal })) }
      catch (requestError) { if (requestError.name !== 'AbortError') setError(requestError.message || 'Não foi possível carregar o curso.') }
      finally { if (!controller.signal.aborted) setLoading(false) }
    }
    carregarCurso()
    return () => controller.abort()
  }, [cursoId])
  return { curso, loading, error }
}
