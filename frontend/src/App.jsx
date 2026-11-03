import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/useAuth'
import { RankingCursos } from './components/RankingCursos'
import { RotaProtegida } from './components/RotaProtegida'
import { TelaLogin } from './components/TelaLogin'

const PaginaAnaliseCurso = lazy(() => import('./components/PaginaAnaliseCurso').then((module) => ({ default: module.PaginaAnaliseCurso })))

function PaginaRanking() {
  const { usuario, perfil, sair } = useAuth()

  if (perfil?.papel === 'COORDENADOR_CURSO') {
    const cursoId = perfil.cursos_ids[0]
    if (cursoId) return <Navigate to={`/cursos/${cursoId}`} replace />

    return <main className="mx-auto grid min-h-[calc(100vh-4px)] w-[calc(100%-2rem)] max-w-md place-items-center text-center max-sm:w-[calc(100%-1.5rem)]"><section className="rounded-2xl border border-amber-200 bg-white p-7 shadow-sm"><h1 className="text-xl font-bold text-ink">Curso não vinculado</h1><p className="mt-2 text-sm leading-6 text-slate-600">Seu perfil de coordenador ainda não está associado a um curso.</p><button type="button" onClick={() => sair()} className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white hover:bg-brand-800">Sair</button></section></main>
  }

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
