import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, ClassBadge, FilterTabs, RankBadge, ScoreBar, StatCard } from '../ui'
import { useEscolas } from '../hooks/useEscolas'
import { useRankingCursos } from '../hooks/useRankingCursos'

function formatarScore(score) {
  return Number(score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function ResumoRanking({ cursos }) {
  const resumo = useMemo(() => ({
    scoreMedio: cursos.reduce((total, curso) => total + Number(curso.score), 0) / cursos.length,
    lider: cursos[0],
    cursosEmAtencao: cursos.filter((curso) => curso.classe === 'B' || curso.classe === 'D').length,
  }), [cursos])

  return <section className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Resumo do ranking">
    <StatCard label="Cursos analisados" value={cursos.length} caption="na seleção atual" />
    <StatCard label="Score médio" value={formatarScore(resumo.scoreMedio)} caption="em uma escala de 0 a 100" tone="brand" />
    <StatCard label="Melhor desempenho" value={resumo.lider.nome} caption={`${formatarScore(resumo.lider.score)} · Classe ${resumo.lider.classe}`} tone="good" />
    <StatCard label="Em atenção" value={resumo.cursosEmAtencao} caption="cursos nas classes B ou D" tone="warn" />
  </section>
}

export function RankingCursos() {
  const [escolaId, setEscolaId] = useState('')
  const [classeSelecionada, setClasseSelecionada] = useState('')
  const navigate = useNavigate()
  const { escolas, loading: escolasLoading, error: escolasError } = useEscolas()
  const { cursos, loading, error, recarregar } = useRankingCursos(escolaId)
  const pronto = !loading && !error
  const cursosVisiveis = classeSelecionada ? cursos.filter((curso) => curso.classe === classeSelecionada) : cursos
  const classesDisponiveis = ['A', 'B', 'D'].filter((classe) => cursos.some((curso) => curso.classe === classe))
  const filtros = [
    { value: '', label: 'Todos', count: cursos.length },
    ...classesDisponiveis.map((classe) => ({ value: classe, label: `Classe ${classe}`, count: cursos.filter((curso) => curso.classe === classe).length })),
  ]

  return <>
    {pronto && cursosVisiveis.length > 0 && <ResumoRanking cursos={cursosVisiveis} />}
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" aria-labelledby="ranking-title">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-5 lg:flex-row lg:items-end lg:justify-between">
        <div><h2 id="ranking-title" className="text-xl font-bold tracking-tight text-slate-900">Ranking de cursos</h2>{pronto && <p className="mt-0.5 text-sm text-slate-600">{cursosVisiveis.length} curso(s) encontrado(s)</p>}</div>
        <div className="flex flex-col gap-3 lg:items-end"><FilterTabs options={filtros} value={classeSelecionada} onChange={setClasseSelecionada} /><label className="grid gap-1 text-xs font-semibold text-slate-600"><span>Escola</span><select className="h-10 min-w-48 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-600/30 disabled:cursor-not-allowed disabled:bg-slate-50" value={escolaId} onChange={(event) => setEscolaId(event.target.value)} disabled={escolasLoading || Boolean(escolasError)}><option value="">Todas as escolas</option>{escolas.map((escola) => <option key={escola.id} value={escola.id}>{escola.nome}</option>)}</select></label></div>
      </div>
      {escolasError && <p className="m-0 bg-rose-50 px-5 py-3 text-sm text-rose-800" role="alert">O filtro de escolas não pôde ser carregado.</p>}
      {loading && <div className="grid min-h-57.5 place-items-center p-6 text-center text-slate-500" role="status"><div><div className="mx-auto mb-3 size-8 animate-spin rounded-full border-[3px] border-indigo-100 border-t-indigo-600" aria-hidden="true" /><p>Carregando ranking de cursos...</p></div></div>}
      {error && !loading && <div className="grid min-h-57.5 place-items-center p-6 text-center" role="alert"><div><p className="text-rose-700">{error}</p><Button variant="primary" className="mt-2" onClick={recarregar}>Tentar novamente</Button></div></div>}
      {pronto && <div className="overflow-x-auto"><table className="w-full min-w-210 border-collapse text-left"><thead className="bg-slate-50"><tr><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Posição</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Curso</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Escola</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Score</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Classe</th><th scope="col" className="px-5 py-3"><span className="sr-only">Ações</span></th></tr></thead><tbody>{cursosVisiveis.map((curso) => {
        const posicao = cursos.findIndex((item) => item.id === curso.id) + 1
        return <tr key={curso.id} className="border-t border-slate-100 hover:bg-slate-50"><td className="px-5 py-3"><RankBadge position={posicao} /></td><td className="px-5 py-3 font-semibold text-slate-900">{curso.nome}</td><td className="px-5 py-3 text-sm text-slate-600">{curso.escola}</td><td className="px-5 py-3"><ScoreBar score={curso.score} classe={curso.classe} /></td><td className="px-5 py-3"><ClassBadge classe={curso.classe} /></td><td className="px-5 py-3 text-right"><Button variant="primary" onClick={() => navigate(`/cursos/${curso.id}`)}>Analisar →</Button></td></tr>
      })}{cursosVisiveis.length === 0 && <tr><td colSpan="6" className="px-5 py-10 text-center text-slate-500">Nenhum curso foi encontrado para estes filtros.</td></tr>}</tbody></table></div>}
    </section>
  </>
}
