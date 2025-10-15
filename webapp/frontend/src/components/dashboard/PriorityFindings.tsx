import { Card } from '../ui/Card'
import { Button } from '../ui/Button'

export default function PriorityFindings() {
  return (
    <Card>
      <h3 className="text-lg font-semibold mb-4">Priority Findings</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Resource</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Issue</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Severity</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b hover:bg-gray-50">
              <td className="py-3 px-4 text-sm" colSpan={4}>
                <p className="text-gray-500 text-center">No priority findings - Run a scan to get started</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-center">
        <Button variant="ghost" size="sm">View All Findings →</Button>
      </div>
    </Card>
  )
}
