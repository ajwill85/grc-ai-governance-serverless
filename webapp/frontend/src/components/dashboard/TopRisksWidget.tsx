import { Card } from '../ui/Card'
import { AlertTriangle } from 'lucide-react'

interface Risk {
  issue: string
  severity: string
  count: number
}

interface TopRisksWidgetProps {
  risks: Risk[]
}

export default function TopRisksWidget({ risks }: TopRisksWidgetProps) {
  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      CRITICAL: 'text-severity-critical',
      HIGH: 'text-severity-high',
      MEDIUM: 'text-severity-medium',
      LOW: 'text-severity-low'
    }
    return colors[severity] || 'text-gray-600'
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Top Risks</h3>
        <AlertTriangle className="w-5 h-5 text-gray-400" />
      </div>
      <div className="space-y-3">
        {risks.length === 0 ? (
          <p className="text-gray-500 text-sm">No risks found</p>
        ) : (
          risks.map((risk, index) => (
            <div key={index} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-sm">{risk.issue}</p>
                <p className={`text-xs font-semibold mt-1 ${getSeverityColor(risk.severity)}`}>
                  {risk.severity}
                </p>
              </div>
              <span className="ml-4 px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-semibold">
                {risk.count}
              </span>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
