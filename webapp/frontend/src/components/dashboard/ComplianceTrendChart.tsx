import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format } from 'date-fns'

interface TrendData {
  date: string
  risk_score: number
  total_findings: number
  critical: number
  high: number
  medium: number
  low: number
}

interface ComplianceTrendChartProps {
  data: TrendData[]
}

export default function ComplianceTrendChart({ data }: ComplianceTrendChartProps) {
  const formattedData = data.map(item => ({
    ...item,
    date: format(new Date(item.date), 'MMM dd')
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={formattedData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="risk_score" stroke="#0ea5e9" name="Risk Score" />
        <Line type="monotone" dataKey="total_findings" stroke="#ff9900" name="Total Findings" />
      </LineChart>
    </ResponsiveContainer>
  )
}
