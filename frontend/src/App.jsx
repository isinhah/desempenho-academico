import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/useAuth'
import { CabecalhoAplicacao } from './components/CabecalhoAplicacao'
import { RankingCursos } from './components/RankingCursos'
import { RotaProtegida } from './components/RotaProtegida'
import { TelaLogin } from './components/TelaLogin'

const PaginaAnaliseCurso = lazy(() => import('./components/PaginaAnaliseCurso').then((module) => ({ default: module.PaginaAnaliseCurso })))

function PaginaRanking() {
  const { perfil } = useAuth()

  if (perfil?.papel === 'COORDENADOR_CURSO') {
    const cursoId = perfil.cursos_ids[0]
    if (cursoId) return <Navigate to={`/cursos/${cursoId}`} replace />

    return <main className="mx-auto grid min-h-[calc(100vh-4px)] w-[calc(100%-2rem)] max-w-md place-items-center text-center max-sm:w-[calc(100%-1.5rem)]"><section className="rounded-2xl border border-amber-200 bg-white p-7 shadow-sm"><h1 className="text-xl font-bold text-ink">Curso não vinculado</h1><p className="mt-2 text-sm leading-6 text-slate-600">Seu perfil de coordenador ainda não está associado a um curso.</p></section></main>
  }

  return (
    <main className="mx-auto w-[calc(100%-2rem)] max-w-6xl py-12 pb-16 max-sm:w-[calc(100%-1.5rem)] max-sm:py-8">
      <header className="mb-4">
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">Análise de desempenho dos cursos</h1>
        <p className="mt-1 text-sm text-slate-600">Consulte o ranking, compare scores e acompanhe a evolução da evasão.</p>
      </header>
      <RankingCursos />
    </main>
  )
}

function AreaAutenticada({ children }) {
  return <RotaProtegida><CabecalhoAplicacao />{children}</RotaProtegida>
}

function App() {
  return <div className="min-h-screen bg-canvas text-ink"><div className="h-1 bg-accent-600" aria-hidden="true" /><Routes><Route path="/login" element={<TelaLogin />} /><Route path="/" element={<AreaAutenticada><PaginaRanking /></AreaAutenticada>} /><Route path="/cursos/:cursoId" element={<AreaAutenticada><Suspense fallback={<main className="grid min-h-70 place-items-center text-center text-slate-500">Carregando análise do curso...</main>}><PaginaAnaliseCurso /></Suspense></AreaAutenticada>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></div>
}

export default App
