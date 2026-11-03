import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/useAuth'
import { RankingCursos } from './components/RankingCursos'
import { RotaProtegida } from './components/RotaProtegida'
import { TelaLogin } from './components/TelaLogin'

const PaginaAnaliseCurso = lazy(() => import('./components/PaginaAnaliseCurso').then((module) => ({ default: module.PaginaAnaliseCurso })))

function PaginaRanking() {
  const { usuario, sair } = useAuth()

  return (
    <main className="mx-auto w-[calc(100%-2rem)] max-w-6xl py-12 pb-16 max-sm:w-[calc(100%-1.5rem)] max-sm:py-8">
      <header className="mb-4">
        <div className="flex items-start justify-between gap-4">
          <p className="text-xs font-bold text-accent-700">PUCPR</p>
          <button type="button" onClick={() => sair()} className="text-sm font-semibold text-brand-700 hover:text-brand-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2">
            Sair
          </button>
        </div>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">Análise de desempenho dos cursos</h1>
        <p className="mt-1 text-sm text-slate-600">Consulte o ranking, compare scores e acompanhe a evolução da evasão. <span className="sr-only">Usuário autenticado: </span>{usuario.email}</p>
      </header>
      <RankingCursos />
    </main>
  )
}

function App() {
  return <div className="min-h-screen bg-canvas text-ink"><div className="h-1 bg-accent-600" aria-hidden="true" /><Routes><Route path="/login" element={<TelaLogin />} /><Route path="/" element={<RotaProtegida><PaginaRanking /></RotaProtegida>} /><Route path="/cursos/:cursoId" element={<RotaProtegida><Suspense fallback={<main className="grid min-h-70 place-items-center text-center text-slate-500">Carregando análise do curso...</main>}><PaginaAnaliseCurso /></Suspense></RotaProtegida>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></div>
}

export default App
