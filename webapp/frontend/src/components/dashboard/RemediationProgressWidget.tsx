import { Card } from '../ui/Card'
import { CheckCircle } from 'lucide-react'

interface RemediationProgressWidgetProps {
  progress: any
}

export default function RemediationProgressWidget({ progress }: RemediationProgressWidgetProps) {
  if (!progress) {
    return (
      <Card>
        <h3 className="text-lg font-semibold mb-4">Remediation Progress</h3>
        <p className="text-gray-500">Loading...</p>
      </Card>
    )
  }

  const total = Object.values(progress).reduce((sum: number, val: any) => sum + val, 0)

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Remediation Progress</h3>
        <CheckCircle className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm">Open</span>
          <span className="font-semibold text-red-600">{progress.open || 0}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm">Assigned</span>
          <span className="font-semibold text-yellow-600">{progress.assigned || 0}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm">In Progress</span>
          <span className="font-semibold text-blue-600">{progress.in_progress || 0}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm">Resolved</span>
          <span className="font-semibold text-green-600">{progress.resolved || 0}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm">Accepted Risk</span>
          <span className="font-semibold text-gray-600">{progress.accepted_risk || 0}</span>
        </div>
      </div>

      {total > 0 && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex justify-between text-sm font-semibold">
            <span>Total</span>
            <span>{total}</span>
          </div>
        </div>
      )}
    </Card>
  )
}
