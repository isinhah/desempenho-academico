import { Link, useParams } from 'react-router-dom'
import { useCurso } from '../hooks/useCurso'
import { HistoricoCurso } from './HistoricoCurso'

export function PaginaAnaliseCurso() {
  const { cursoId } = useParams()
  const { curso, loading, error } = useCurso(cursoId)
  return (
    <main className="mx-auto w-[calc(100%-2rem)] max-w-[1180px] py-16 pb-20 max-sm:w-[calc(100%-1.5rem)] max-sm:py-10">
      <Link className="mb-6 inline-block text-sm font-bold text-indigo-700 hover:underline focus-visible:outline-3 focus-visible:outline-indigo-200 focus-visible:outline-offset-2" to="/">← Voltar ao ranking</Link>
      <header className="mb-7"><h1 className="text-[clamp(2rem,5vw,3.35rem)] leading-[1.04] font-bold tracking-[-0.045em] text-slate-900">Desempenho do curso</h1><p className="mt-4 max-w-[620px] text-[1.03rem] leading-relaxed text-slate-500">Acompanhe o score consolidado e a evolução mensal da evasão.</p></header>
      {loading && <div className="grid min-h-70 place-items-center text-center text-slate-500" role="status"><div><div className="mx-auto mb-3.5 size-7.5 animate-spin rounded-full border-3 border-indigo-100 border-t-indigo-600" aria-hidden="true" /><p>Carregando análise do curso...</p></div></div>}
      {error && !loading && <div className="grid min-h-70 place-items-center text-center text-rose-700" role="alert">{error}</div>}
      {curso && !loading && <HistoricoCurso curso={curso} />}
    </main>
  )
}
