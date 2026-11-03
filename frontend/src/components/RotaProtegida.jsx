import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'

export function RotaProtegida({ children }) {
  const { usuario, carregando, erroPerfil, sair } = useAuth()
  const location = useLocation()

  if (carregando) {
    return <main className="grid min-h-[calc(100vh-4px)] place-items-center" aria-label="Verificando sessão" role="status"><span className="size-8 animate-spin rounded-full border-[3px] border-brand-100 border-t-brand-700" aria-hidden="true" /></main>
  }

  if (!usuario) return <Navigate to="/login" replace state={{ from: location }} />
  if (erroPerfil) {
    return (
      <main className="mx-auto grid min-h-[calc(100vh-4px)] w-[calc(100%-2rem)] max-w-md place-items-center text-center max-sm:w-[calc(100%-1.5rem)]">
        <section className="rounded-2xl border border-amber-200 bg-white p-7 shadow-sm">
          <h1 className="text-xl font-bold text-ink">Acesso ainda não configurado</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">{erroPerfil}</p>
          <button type="button" onClick={() => sair()} className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white hover:bg-brand-800">Sair</button>
        </section>
      </main>
    )
  }
  return children
}
