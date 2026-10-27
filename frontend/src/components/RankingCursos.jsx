import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ClassBadge } from './ClassBadge'
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
  const cards = [
    {
      label: 'Cursos analisados',
      value: cursos.length,
      description: 'na seleção atual',
      tone: 'border-slate-200 bg-linear-to-br from-white to-slate-100',
      labelTone: 'text-slate-600',
      valueTone: 'text-slate-900',
      descriptionTone: 'text-slate-600',
      bar: 'bg-slate-400',
    },
    {
      label: 'Score médio',
      value: formatarScore(resumo.scoreMedio),
      description: 'em uma escala de 0 a 100',
      tone: 'border-sky-200 bg-linear-to-br from-white to-sky-100',
      labelTone: 'text-sky-700',
      valueTone: 'text-sky-950',
      descriptionTone: 'text-sky-800',
      bar: 'bg-sky-500',
    },
    {
      label: 'Melhor desempenho',
      value: resumo.lider.nome,
      description: `${formatarScore(resumo.lider.score)} · Classe ${resumo.lider.classe}`,
      tone: 'border-emerald-200 bg-linear-to-br from-white to-emerald-100',
      labelTone: 'text-emerald-700',
      valueTone: 'text-emerald-950',
      descriptionTone: 'text-emerald-800',
      bar: 'bg-emerald-500',
      valueSize: 'text-base',
    },
    {
      label: 'Em atenção',
      value: resumo.cursosEmAtencao,
      description: 'cursos nas classes B ou D',
      tone: 'border-amber-200 bg-linear-to-br from-white to-amber-100',
      labelTone: 'text-amber-800',
      valueTone: 'text-amber-950',
      descriptionTone: 'text-amber-800',
      bar: 'bg-amber-500',
    },
  ]

  return <section className="mb-4 grid grid-cols-1 gap-3.5 sm:grid-cols-2 xl:grid-cols-4" aria-label="Resumo do ranking">{cards.map((card) => <article key={card.label} className={`relative grid min-h-36 overflow-hidden rounded-[14px] border p-4.5 shadow-[0_8px_22px_rgb(15_23_42_/_4%)] ${card.tone}`}><span className={`self-start text-[0.72rem] font-extrabold uppercase tracking-[0.07em] ${card.labelTone}`}>{card.label}</span><strong className={`self-center truncate text-[1.6rem] leading-tight font-bold ${card.valueTone} ${card.valueSize || ''}`}>{card.value}</strong><span className={`self-end text-[0.82rem] ${card.descriptionTone}`}>{card.description}</span><span className={`absolute inset-x-0 bottom-0 h-1 ${card.bar}`} aria-hidden="true" /></article>)}</section>
}

export function RankingCursos() {
  const [escolaId, setEscolaId] = useState('')
  const navigate = useNavigate()
  const { escolas, loading: escolasLoading, error: escolasError } = useEscolas()
  const { cursos, loading, error, recarregar } = useRankingCursos(escolaId)
  const pronto = !loading && !error

  return <>{pronto && cursos.length > 0 && <ResumoRanking cursos={cursos} />}<section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_12px_30px_rgb(15_23_42_/_7%)]" aria-labelledby="ranking-title"><div className="flex items-center justify-between gap-4 border-b border-slate-200 px-6 py-5.5 max-sm:flex-col max-sm:items-stretch max-sm:px-4.5"><div><p className="mb-1.5 text-[0.67rem] font-extrabold uppercase tracking-[0.11em] text-indigo-600">Visão geral</p><h2 id="ranking-title" className="m-0 text-xl font-bold text-slate-800">Ranking de cursos</h2>{pronto && <p className="mt-1 text-sm text-slate-500">{cursos.length} curso(s) encontrado(s)</p>}</div><label className="grid gap-1.5 text-[0.72rem] font-extrabold uppercase tracking-[0.05em] text-slate-600"><span>Filtrar por escola</span><select className="min-w-55 rounded-lg border border-slate-300 bg-white px-2.5 py-2.25 text-sm font-medium normal-case tracking-normal text-slate-800 focus-visible:outline-[3px] focus-visible:outline-indigo-200 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400 max-sm:w-full" value={escolaId} onChange={(event) => setEscolaId(event.target.value)} disabled={escolasLoading || Boolean(escolasError)}><option value="">Todas as escolas</option>{escolas.map((escola) => <option key={escola.id} value={escola.id}>{escola.nome}</option>)}</select></label></div>{escolasError && <p className="m-0 bg-rose-50 px-6 py-2.5 text-sm text-rose-700" role="alert">O filtro de escolas não pôde ser carregado.</p>}{loading && <div className="grid min-h-[230px] place-items-center p-6 text-center text-slate-500" role="status"><div><div className="mx-auto mb-3.5 size-8 animate-spin rounded-full border-[3px] border-indigo-100 border-t-indigo-600" aria-hidden="true" /><p className="m-0">Carregando ranking de cursos...</p></div></div>}{error && !loading && <div className="grid min-h-[230px] place-items-center p-6 text-center" role="alert"><div className="max-w-[410px]"><p className="m-0 text-rose-700">{error}</p><button className="mt-4 cursor-pointer rounded-lg border-0 bg-indigo-600 px-3 py-2 text-[0.82rem] font-bold text-white hover:bg-indigo-700 focus-visible:outline-[3px] focus-visible:outline-indigo-200 focus-visible:outline-offset-2" type="button" onClick={recarregar}>Tentar novamente</button></div></div>}{pronto && <div className="overflow-x-auto"><table className="w-full min-w-200 border-collapse text-left"><thead><tr className="bg-slate-50"><th scope="col" className="px-5.5 py-4 text-[0.7rem] font-extrabold uppercase tracking-[0.07em] text-slate-500">Posição</th><th scope="col" className="px-5.5 py-4 text-[0.7rem] font-extrabold uppercase tracking-[0.07em] text-slate-500">Curso</th><th scope="col" className="px-5.5 py-4 text-[0.7rem] font-extrabold uppercase tracking-[0.07em] text-slate-500">Escola</th><th scope="col" className="px-5.5 py-4 text-[0.7rem] font-extrabold uppercase tracking-[0.07em] text-slate-500">Score</th><th scope="col" className="px-5.5 py-4 text-[0.7rem] font-extrabold uppercase tracking-[0.07em] text-slate-500">Classe</th><th scope="col" className="px-5.5 py-4"><span className="sr-only">Ações</span></th></tr></thead><tbody>{cursos.map((curso, index) => <tr key={curso.id} className="border-b border-slate-200 last:border-b-0 hover:bg-indigo-50/50"><td className="px-5.5 py-4"><span className={`inline-grid size-8 place-items-center rounded-full text-xs font-extrabold ${index < 3 ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>{String(index + 1).padStart(2, '0')}</span></td><td className="px-5.5 py-4 font-bold text-slate-800">{curso.nome}</td><td className="max-w-47.5 px-5.5 py-4 text-sm text-slate-600">{curso.escola}</td><td className="px-5.5 py-4"><div className="grid min-w-29 gap-1.75 tabular-nums text-indigo-950"><strong>{formatarScore(curso.score)}</strong><span className="block h-1.25 overflow-hidden rounded-full bg-indigo-100" aria-hidden="true"><span className="block h-full rounded-full bg-indigo-500" style={{ width: `${curso.score}%` }} /></span></div></td><td className="px-5.5 py-4"><ClassBadge classe={curso.classe} /></td><td className="px-5.5 py-4"><button className="cursor-pointer rounded-md border-0 bg-indigo-50 px-3 py-2 text-[0.82rem] font-bold text-indigo-700 hover:bg-indigo-600 hover:text-white focus-visible:outline-[3px] focus-visible:outline-indigo-200 focus-visible:outline-offset-2" type="button" onClick={() => navigate(`/cursos/${curso.id}`)}>Analisar</button></td></tr>)}{cursos.length === 0 && <tr><td colSpan="6" className="px-5.5 py-8.5 text-center text-slate-500">Nenhum curso foi encontrado para esta escola.</td></tr>}</tbody></table></div>}</section></>
}
