import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ClassBadge } from './ClassBadge'
import { useHistoricoCurso } from '../hooks/useHistoricoCurso'

function formatarMes(data) { return new Intl.DateTimeFormat('pt-BR', { month: 'short', year: '2-digit' }).format(new Date(`${data}T12:00:00`)).replace('.', '') }
function formatarPercentual(valor) { return `${Number(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%` }
function formatarPontosPercentuais(valor) { return `${valor > 0 ? '+' : ''}${Number(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} p.p.` }

export function HistoricoCurso({ curso }) {
  const { historico, loading, error } = useHistoricoCurso(curso.id)
  const dadosGrafico = historico.map((indicador) => ({ ...indicador, mes: formatarMes(indicador.mes_referencia) }))
  const atual = historico.at(-1)
  const anterior = historico.at(-2)
  const variacao = atual && anterior ? Number(atual.pct_evasao) - Number(anterior.pct_evasao) : null
  const evasaoReduziu = variacao !== null && variacao < 0
  const evasaoAumentou = variacao !== null && variacao > 0
  const corVariacao = evasaoReduziu ? 'text-green-700' : evasaoAumentou ? 'text-red-600' : 'text-slate-800'
  const estiloVariacao = evasaoReduziu
    ? { tone: 'border-emerald-200 bg-linear-to-br from-white to-emerald-100', labelTone: 'text-emerald-700', valueTone: 'text-emerald-950', descriptionTone: 'text-emerald-800', bar: 'bg-emerald-500' }
    : evasaoAumentou
      ? { tone: 'border-rose-200 bg-linear-to-br from-white to-rose-100', labelTone: 'text-rose-700', valueTone: 'text-rose-950', descriptionTone: 'text-rose-800', bar: 'bg-rose-500' }
      : { tone: 'border-slate-200 bg-linear-to-br from-white to-slate-100', labelTone: 'text-slate-600', valueTone: 'text-slate-900', descriptionTone: 'text-slate-600', bar: 'bg-slate-400' }
  const kpis = [
    { label: 'Score atual', value: Number(curso.score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }), detail: <ClassBadge classe={curso.classe} />, tone: 'border-sky-200 bg-linear-to-br from-white to-sky-100', labelTone: 'text-sky-700', valueTone: 'text-sky-950', descriptionTone: 'text-sky-800', bar: 'bg-sky-500' },
    { label: 'Alunos ativos', value: Number(curso.alunos_ativos).toLocaleString('pt-BR'), detail: 'no período mais recente', tone: 'border-slate-200 bg-linear-to-br from-white to-slate-100', labelTone: 'text-slate-600', valueTone: 'text-slate-900', descriptionTone: 'text-slate-600', bar: 'bg-slate-400' },
    { label: 'Alunos evadidos', value: Number(curso.alunos_evadidos).toLocaleString('pt-BR'), detail: 'no período mais recente', tone: 'border-amber-200 bg-linear-to-br from-white to-amber-100', labelTone: 'text-amber-800', valueTone: 'text-amber-950', descriptionTone: 'text-amber-800', bar: 'bg-amber-500' },
    { label: 'Evasão mais recente', value: atual ? formatarPercentual(atual.pct_evasao) : '—', detail: atual ? formatarMes(atual.mes_referencia) : 'Sem histórico', tone: 'border-rose-200 bg-linear-to-br from-white to-rose-100', labelTone: 'text-rose-700', valueTone: 'text-rose-950', descriptionTone: 'text-rose-800', bar: 'bg-rose-500' },
    { label: 'Variação da evasão', value: variacao === null ? '—' : formatarPontosPercentuais(variacao), detail: variacao === null ? 'São necessários dois meses' : evasaoReduziu ? 'Reduziu desde o mês anterior' : evasaoAumentou ? 'Aumentou desde o mês anterior' : 'Sem variação no último mês', valueClass: corVariacao, ...estiloVariacao },
  ]

  return (
    <section className="mt-4.5 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_12px_30px_rgb(15_23_42_/_7%)]" aria-labelledby="history-title">
      <header className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5.5 max-sm:px-4.5"><div><h2 id="history-title" className="m-0 text-xl font-bold text-slate-800">{curso.nome}</h2><p className="mt-1 text-sm text-slate-500">{curso.escola}</p></div></header>
      <div className="grid grid-cols-1 gap-3 border-b border-slate-200 bg-slate-50 p-4 md:grid-cols-3 xl:grid-cols-5">{kpis.map((kpi) => <article key={kpi.label} className={`relative grid min-h-35 overflow-hidden rounded-xl border p-4 shadow-[0_6px_16px_rgb(15_23_42_/_4%)] ${kpi.tone}`}><span className={`self-start text-[0.7rem] font-extrabold uppercase tracking-[0.06em] ${kpi.labelTone}`}>{kpi.label}</span><strong className={`self-center text-[1.35rem] leading-tight font-bold ${kpi.valueClass || kpi.valueTone}`}>{kpi.value}</strong>{typeof kpi.detail === 'string' ? <small className={`self-end ${kpi.descriptionTone}`}>{kpi.detail}</small> : <span className="self-end">{kpi.detail}</span>}<span className={`absolute inset-x-0 bottom-0 h-1 ${kpi.bar}`} aria-hidden="true" /></article>)}</div>
      {loading && <div className="grid min-h-[230px] place-items-center p-6 text-center text-slate-500" role="status">Carregando histórico...</div>}
      {error && !loading && <div className="grid min-h-[230px] place-items-center p-6 text-center text-rose-700" role="alert">{error}</div>}
      {!loading && !error && dadosGrafico.length === 0 && <div className="grid min-h-[230px] place-items-center p-6 text-center text-slate-500">Não há indicadores para este curso.</div>}
      {!loading && !error && dadosGrafico.length > 0 && <div className="px-1 pb-3 pt-5"><div className="flex items-baseline justify-between px-5 pb-2 max-sm:px-4"><h3 className="m-0 text-[0.95rem] font-bold text-slate-700">Evolução da evasão</h3><span className="text-[0.8rem] text-slate-500">Percentual por mês</span></div><ResponsiveContainer width="100%" height={300}><LineChart data={dadosGrafico} margin={{ top: 12, right: 24, bottom: 6, left: 0 }}><CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" vertical={false} /><XAxis dataKey="mes" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} /><YAxis unit="%" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} width={48} /><Tooltip formatter={(value) => [formatarPercentual(value), '% de evasão']} labelFormatter={(label) => `Referência: ${label}`} /><Line type="monotone" dataKey="pct_evasao" name="% de evasão" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4, fill: '#4f46e5' }} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer></div>}
    </section>
  )
}
