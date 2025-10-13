import { Card } from '../ui/Card'
import { Activity } from 'lucide-react'
import { format } from 'date-fns'

interface ActivityItem {
  type: string
  description: string
  timestamp: string
  scan_id: number
}

interface RecentActivityWidgetProps {
  activities: ActivityItem[]
}

export default function RecentActivityWidget({ activities }: RecentActivityWidgetProps) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Recent Activity</h3>
        <Activity className="w-5 h-5 text-gray-400" />
      </div>
      <div className="space-y-3">
        {activities.length === 0 ? (
          <p className="text-gray-500 text-sm">No recent activity</p>
        ) : (
          activities.map((activity, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="text-sm font-medium">{activity.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {format(new Date(activity.timestamp), 'PPp')}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
