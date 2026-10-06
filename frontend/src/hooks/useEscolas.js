import { useEffect, useState } from 'react'
import { listarEscolas } from '../services/cursosApi'

export function useEscolas() {
  const [escolas, setEscolas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    async function carregarEscolas() {
      try {
        setError(null)
        const dados = await listarEscolas({ signal: controller.signal })
        setEscolas(dados)
      } catch (requestError) {
        if (requestError.name !== 'AbortError') setError(requestError.message || 'Não foi possível carregar as escolas.')
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }

    carregarEscolas()
    return () => controller.abort()
  }, [])

  return { escolas, loading, error }
}
