import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'

export function RotaProtegida({ children }) {
  const { usuario, carregando } = useAuth()
  const location = useLocation()

  if (carregando) {
    return <main className="grid min-h-[calc(100vh-4px)] place-items-center text-sm text-slate-600">Verificando sessão...</main>
  }

  if (!usuario) return <Navigate to="/login" replace state={{ from: location }} />
  return children
}
