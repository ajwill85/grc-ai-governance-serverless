import { Card } from '../ui/Card'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { BarChart3 } from 'lucide-react'

interface Coverage {
  iso_27001: { total: number; compliant: number; percentage: number }
  iso_27701: { total: number; compliant: number; percentage: number }
  iso_42001: { total: number; compliant: number; percentage: number }
}

interface ControlCoverageWidgetProps {
  coverage: Coverage | undefined
}

export default function ControlCoverageWidget({ coverage }: ControlCoverageWidgetProps) {
  if (!coverage) {
    return (
      <Card>
        <h3 className="text-lg font-semibold mb-4">Control Coverage</h3>
        <p className="text-gray-500">Loading...</p>
      </Card>
    )
  }

  const data = [
    { name: 'ISO 27001', value: coverage.iso_27001.percentage, color: '#0ea5e9' },
    { name: 'ISO 27701', value: coverage.iso_27701.percentage, color: '#10b981' },
    { name: 'ISO 42001', value: coverage.iso_42001.percentage, color: '#f59e0b' },
  ]

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Control Coverage</h3>
        <BarChart3 className="w-5 h-5 text-gray-400" />
      </div>
      
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value}%`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span>ISO 27001</span>
          <span className="font-semibold">{coverage.iso_27001.compliant}/{coverage.iso_27001.total}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>ISO 27701</span>
          <span className="font-semibold">{coverage.iso_27701.compliant}/{coverage.iso_27701.total}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>ISO 42001</span>
          <span className="font-semibold">{coverage.iso_42001.compliant}/{coverage.iso_42001.total}</span>
        </div>
      </div>
    </Card>
  )
}
