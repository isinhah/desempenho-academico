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
  const kpis = [
    { label: 'Score atual', value: Number(curso.score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }), detail: <ClassBadge classe={curso.classe} /> },
    { label: 'Alunos ativos', value: Number(curso.alunos_ativos).toLocaleString('pt-BR'), detail: 'no período mais recente' },
    { label: 'Alunos evadidos', value: Number(curso.alunos_evadidos).toLocaleString('pt-BR'), detail: 'no período mais recente' },
    { label: 'Evasão mais recente', value: atual ? formatarPercentual(atual.pct_evasao) : '—', detail: atual ? formatarMes(atual.mes_referencia) : 'Sem histórico' },
    { label: 'Variação da evasão', value: variacao === null ? '—' : formatarPontosPercentuais(variacao), detail: variacao === null ? 'São necessários dois meses' : evasaoReduziu ? 'Reduziu desde o mês anterior' : evasaoAumentou ? 'Aumentou desde o mês anterior' : 'Sem variação no último mês', valueClass: corVariacao },
  ]

  return (
    <section className="mt-4.5 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_12px_30px_rgb(15_23_42_/_7%)]" aria-labelledby="history-title">
      <header className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5.5 max-sm:px-4.5"><div><p className="mb-1.5 text-[0.67rem] font-extrabold uppercase tracking-[0.11em] text-indigo-600">Análise do curso</p><h2 id="history-title" className="m-0 text-xl font-bold text-slate-800">{curso.nome}</h2><p className="mt-1 text-sm text-slate-500">{curso.escola}</p></div></header>
      <div className="grid grid-cols-1 border-b border-slate-200 md:grid-cols-3 xl:grid-cols-5">{kpis.map((kpi, index) => <div key={kpi.label} className={`grid gap-1.75 px-5 py-4.5 ${index < kpis.length - 1 ? 'border-b border-slate-200 xl:border-r xl:border-b-0' : ''} ${index < 3 ? 'md:border-b md:border-slate-200' : ''} ${index === 2 ? 'md:border-r-0' : ''}`}><span className="text-[0.73rem] font-extrabold uppercase tracking-[0.06em] text-slate-500">{kpi.label}</span><strong className={`text-[1.35rem] font-bold ${kpi.valueClass || 'text-slate-800'}`}>{kpi.value}</strong>{typeof kpi.detail === 'string' ? <small className="text-slate-500">{kpi.detail}</small> : kpi.detail}</div>)}</div>
      {loading && <div className="grid min-h-[230px] place-items-center p-6 text-center text-slate-500" role="status">Carregando histórico...</div>}
      {error && !loading && <div className="grid min-h-[230px] place-items-center p-6 text-center text-rose-700" role="alert">{error}</div>}
      {!loading && !error && dadosGrafico.length === 0 && <div className="grid min-h-[230px] place-items-center p-6 text-center text-slate-500">Não há indicadores para este curso.</div>}
      {!loading && !error && dadosGrafico.length > 0 && <div className="px-1 pb-3 pt-5"><div className="flex items-baseline justify-between px-5 pb-2 max-sm:px-4"><h3 className="m-0 text-[0.95rem] font-bold text-slate-700">Evolução da evasão</h3><span className="text-[0.8rem] text-slate-500">Percentual por mês</span></div><ResponsiveContainer width="100%" height={300}><LineChart data={dadosGrafico} margin={{ top: 12, right: 24, bottom: 6, left: 0 }}><CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" vertical={false} /><XAxis dataKey="mes" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} /><YAxis unit="%" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} width={48} /><Tooltip formatter={(value) => [formatarPercentual(value), '% de evasão']} labelFormatter={(label) => `Referência: ${label}`} /><Line type="monotone" dataKey="pct_evasao" name="% de evasão" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4, fill: '#4f46e5' }} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer></div>}
    </section>
  )
}
