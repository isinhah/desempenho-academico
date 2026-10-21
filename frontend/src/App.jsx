import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { RankingCursos } from './components/RankingCursos'

const PaginaAnaliseCurso = lazy(() => import('./components/PaginaAnaliseCurso').then((module) => ({ default: module.PaginaAnaliseCurso })))

function PaginaRanking() {
  return (
    <main className="mx-auto w-[calc(100%-2rem)] max-w-[1180px] py-16 pb-20 max-sm:w-[calc(100%-1.5rem)] max-sm:py-10">
      <header className="mb-8 max-w-[700px]">
        <p className="mb-2 text-xs font-extrabold uppercase tracking-[0.11em] text-indigo-600">PUCPR</p>
        <h1 className="text-[clamp(2rem,5vw,3.35rem)] leading-[1.04] font-bold tracking-[-0.045em] text-slate-900">Análise de desempenho dos cursos</h1>
        <p className="mt-4 max-w-[620px] text-[1.03rem] leading-relaxed text-slate-500">Consulte o ranking, compare scores e acompanhe a evolução da evasão.</p>
      </header>
      <RankingCursos />
    </main>
  )
}

function App() {
  return <Routes><Route path="/" element={<PaginaRanking />} /><Route path="/cursos/:cursoId" element={<Suspense fallback={<main className="grid min-h-70 place-items-center text-center text-slate-500">Carregando análise do curso...</main>}><PaginaAnaliseCurso /></Suspense>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes>
}

export default App
