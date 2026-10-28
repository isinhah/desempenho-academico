import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { RankingCursos } from './components/RankingCursos'

const PaginaAnaliseCurso = lazy(() => import('./components/PaginaAnaliseCurso').then((module) => ({ default: module.PaginaAnaliseCurso })))

function PaginaRanking() {
  return (
    <main className="mx-auto w-[calc(100%-2rem)] max-w-6xl py-12 pb-16 max-sm:w-[calc(100%-1.5rem)] max-sm:py-8">
      <header className="mb-4">
        <p className="text-xs font-bold text-accent-700">PUCPR</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">Análise de desempenho dos cursos</h1>
        <p className="mt-1 text-sm text-slate-600">Consulte o ranking, compare scores e acompanhe a evolução da evasão.</p>
      </header>
      <RankingCursos />
    </main>
  )
}

function App() {
  return <div className="min-h-screen bg-canvas text-ink"><div className="h-1 bg-accent-600" aria-hidden="true" /><Routes><Route path="/" element={<PaginaRanking />} /><Route path="/cursos/:cursoId" element={<Suspense fallback={<main className="grid min-h-70 place-items-center text-center text-slate-500">Carregando análise do curso...</main>}><PaginaAnaliseCurso /></Suspense>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></div>
}

export default App
