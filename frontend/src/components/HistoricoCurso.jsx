import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useHistoricoCurso } from '../hooks/useHistoricoCurso'

function formatarMes(data) {
  return new Intl.DateTimeFormat('pt-BR', { month: 'short', year: '2-digit' })
    .format(new Date(`${data}T12:00:00`))
    .replace('.', '')
}

export function HistoricoCurso({ curso }) {
  const { historico, loading, error } = useHistoricoCurso(curso.id)
  const dadosGrafico = historico.map((indicador) => ({
    ...indicador,
    mes: formatarMes(indicador.mes_referencia),
  }))

  return (
    <section className="history-card" aria-labelledby="history-title">
      <div className="history-card__header">
        <div>
          <p className="eyebrow">Evolução do indicador</p>
          <h2 id="history-title">% de evasão — {curso.nome}</h2>
        </div>
      </div>

      {loading && <div className="history-feedback" role="status">Carregando histórico...</div>}
      {error && !loading && <div className="history-feedback history-feedback--error" role="alert">{error}</div>}
      {!loading && !error && dadosGrafico.length === 0 && <div className="history-feedback">Não há indicadores para este curso.</div>}
      {!loading && !error && dadosGrafico.length > 0 && (
        <div className="history-chart">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={dadosGrafico} margin={{ top: 12, right: 24, bottom: 6, left: 0 }}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" />
              <XAxis dataKey="mes" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} />
              <YAxis unit="%" tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false} width={45} />
              <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}%`, '% de evasão']} />
              <Line type="monotone" dataKey="pct_evasao" name="% de evasão" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4, fill: '#4f46e5' }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
