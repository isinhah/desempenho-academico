import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, ClassBadge, FilterTabs, ScoreBar, StatCard } from '../ui'
import { useEscolas } from '../hooks/useEscolas'
import { useRankingCursos } from '../hooks/useRankingCursos'

function formatarScore(score) {
  return Number(score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function normalizarTexto(valor) {
  return String(valor).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR')
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
    <StatCard label="Melhor desempenho" value={resumo.lider.nome} caption={`${formatarScore(resumo.lider.score)} · Classe ${resumo.lider.classe}`} tone="good" wrapValue />
    <StatCard label="Em atenção" value={resumo.cursosEmAtencao} caption="cursos nas classes B ou D" tone="warn" />
  </section>
}

export function RankingCursos() {
  const [escolaId, setEscolaId] = useState('')
  const [classeSelecionada, setClasseSelecionada] = useState('')
  const [busca, setBusca] = useState('')
  const navigate = useNavigate()
  const { escolas, loading: escolasLoading, error: escolasError } = useEscolas()
  const { cursos, loading, error, recarregar } = useRankingCursos(escolaId)
  const pronto = !loading && !error
  const termoBusca = normalizarTexto(busca.trim())
  const cursosPorClasse = classeSelecionada ? cursos.filter((curso) => curso.classe === classeSelecionada) : cursos
  const cursosVisiveis = termoBusca
    ? cursosPorClasse.filter((curso) => normalizarTexto(curso.nome).includes(termoBusca))
    : cursosPorClasse
  const classesDisponiveis = ['A', 'B', 'D'].filter((classe) => cursos.some((curso) => curso.classe === classe))
  const filtros = [
    { value: '', label: 'Todos', count: cursos.length },
    ...classesDisponiveis.map((classe) => ({ value: classe, label: `Classe ${classe}`, count: cursos.filter((curso) => curso.classe === classe).length })),
  ]

  return <>
    {pronto && cursosVisiveis.length > 0 && <ResumoRanking cursos={cursosVisiveis} />}
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" aria-labelledby="ranking-title">
      <div className="border-b border-slate-200 px-5 py-5">
        <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
          <div><h2 id="ranking-title" className="text-xl font-bold tracking-tight text-slate-900">Ranking de cursos</h2>{pronto && <p className="mt-0.5 text-sm text-slate-600">{cursosVisiveis.length} curso(s) encontrado(s)</p>}</div>
          <label className="relative block w-full lg:w-64 lg:justify-self-end"><span className="sr-only">Buscar curso</span><svg className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><circle cx="11" cy="11" r="6" /><path d="m16 16 4 4" /></svg><input type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Buscar curso" className="h-10 w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-600/30" /></label>
          <div><FilterTabs options={filtros} value={classeSelecionada} onChange={setClasseSelecionada} /></div>
          <label className="flex items-center gap-2 text-xs font-semibold text-slate-600 lg:justify-self-end"><span>Escola</span><select className="h-10 min-w-48 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/30 disabled:cursor-not-allowed disabled:bg-slate-50" value={escolaId} onChange={(event) => setEscolaId(event.target.value)} disabled={escolasLoading || Boolean(escolasError)}><option value="">Todas as escolas</option>{escolas.map((escola) => <option key={escola.id} value={escola.id}>{escola.nome}</option>)}</select></label>
        </div>
      </div>
      {escolasError && <p className="m-0 bg-rose-50 px-5 py-3 text-sm text-rose-800" role="alert">O filtro de escolas não pôde ser carregado.</p>}
      {loading && <div className="grid min-h-57.5 place-items-center p-6 text-center text-slate-500" role="status"><div><div className="mx-auto mb-3 size-8 animate-spin rounded-full border-[3px] border-brand-100 border-t-brand-600" aria-hidden="true" /><p>Carregando ranking de cursos...</p></div></div>}
      {error && !loading && <div className="grid min-h-57.5 place-items-center p-6 text-center" role="alert"><div><p className="text-rose-700">{error}</p><Button variant="primary" className="mt-2" onClick={recarregar}>Tentar novamente</Button></div></div>}
      {pronto && <div className="overflow-x-auto"><table className="w-full min-w-210 border-collapse text-left"><thead className="bg-slate-50"><tr><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Posição</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Curso</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Escola</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Score</th><th scope="col" className="px-5 py-3 text-xs font-semibold text-slate-600">Classe</th><th scope="col" className="px-5 py-3"><span className="sr-only">Ações</span></th></tr></thead><tbody>{cursosVisiveis.map((curso) => {
        const posicao = cursos.findIndex((item) => item.id === curso.id) + 1
        return <tr key={curso.id} className="border-t border-slate-100 hover:bg-slate-50"><td className="px-5 py-3"><span className={`flex size-9 items-center justify-center rounded-full text-sm font-bold ${posicao <= 3 ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-700'}`}>{posicao}</span></td><td className="px-5 py-3 font-semibold text-slate-900">{curso.nome}</td><td className="px-5 py-3 text-sm text-slate-600">{curso.escola}</td><td className="px-5 py-3"><ScoreBar score={curso.score} classe={curso.classe} /></td><td className="px-5 py-3"><ClassBadge classe={curso.classe} /></td><td className="px-5 py-3 text-right"><Button style={{ cursor: 'pointer' }} variant="primary" onClick={() => navigate(`/cursos/${curso.id}`)}>Analisar</Button></td></tr>
      })}{cursosVisiveis.length === 0 && <tr><td colSpan="6" className="px-5 py-12 text-center text-slate-500">Nenhum curso foi encontrado para estes filtros.</td></tr>}</tbody></table></div>}
    </section>
  </>
}
