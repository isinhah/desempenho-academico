import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatarPercentual } from '../utils/formatters'

const BRAND = '#4A1E6B'
const BRAND_LIGHT = '#D7BCE8'

export function EvasionChart({ data, height = 300 }) {
  const maiorValor = Math.max(...data.map((item) => Number(item.evasao)), 0)
  const maximo = Math.max(4, Math.ceil(maiorValor / 4) * 4 + 4)

  return <ResponsiveContainer width="100%" height={height}><LineChart data={data} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}><CartesianGrid stroke="#e2e8f0" vertical={false} /><XAxis dataKey="mes" tick={{ fontSize: 12, fill: '#475569' }} tickLine={false} axisLine={false} /><YAxis domain={[0, maximo]} tick={{ fontSize: 12, fill: '#475569' }} tickLine={false} axisLine={false} width={48} tickFormatter={(valor) => `${valor}%`} /><Tooltip cursor={{ stroke: BRAND_LIGHT }} formatter={(valor) => [formatarPercentual(valor), 'Evasão']} contentStyle={{ borderRadius: 8, border: '1px solid #cbd5e1' }} /><Line type="monotone" dataKey="evasao" stroke={BRAND} strokeWidth={3} dot={{ r: 4, fill: BRAND }} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer>
}
