import { Link, useParams } from 'react-router-dom'
import { useCurso } from '../hooks/useCurso'
import { useRankingCursos } from '../hooks/useRankingCursos'
import { HistoricoCurso } from './HistoricoCurso'

export function PaginaAnaliseCurso() {
  const { cursoId } = useParams()
  const { curso, loading, error } = useCurso(cursoId)
  const { cursos } = useRankingCursos()
  const posicao = cursos.findIndex((item) => String(item.id) === String(cursoId)) + 1
  return (
    <main className="mx-auto w-[calc(100%-2rem)] max-w-6xl py-8 pb-12 max-sm:w-[calc(100%-1.5rem)]">
      <Link className="mb-5 inline-flex min-h-10 items-center rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2" to="/">← Voltar ao ranking</Link>
      <header className="mb-4"><h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">Desempenho do curso</h1><p className="mt-1 text-sm text-slate-600">Acompanhe o score consolidado e a evolução mensal da evasão.</p></header>
      {loading && <div className="grid min-h-70 place-items-center text-center text-slate-500" role="status"><div><div className="mx-auto mb-3 size-8 animate-spin rounded-full border-[3px] border-indigo-100 border-t-indigo-600" aria-hidden="true" /><p>Carregando análise do curso...</p></div></div>}
      {error && !loading && <div className="grid min-h-70 place-items-center text-center text-rose-700" role="alert">{error}</div>}
      {curso && !loading && <HistoricoCurso curso={curso} posicao={posicao || undefined} totalCursos={cursos.length || undefined} />}
    </main>
  )
}
