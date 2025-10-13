import { useQuery } from '@tanstack/react-query'
import { 
  Shield, AlertTriangle, CheckCircle, Clock, 
  TrendingUp, Server, Activity, BarChart3 
} from 'lucide-react'
import { format } from 'date-fns'
import { api } from '../lib/api'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import ComplianceTrendChart from '../components/dashboard/ComplianceTrendChart'
import ControlCoverageWidget from '../components/dashboard/ControlCoverageWidget'
import TopRisksWidget from '../components/dashboard/TopRisksWidget'
import RecentActivityWidget from '../components/dashboard/RecentActivityWidget'
import RemediationProgressWidget from '../components/dashboard/RemediationProgressWidget'
import PriorityFindings from '../components/dashboard/PriorityFindings'

export default function Dashboard() {
  // Fetch dashboard data
  const { data: overview, isLoading } = useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: () => api.get('/dashboard/overview').then(res => res.data),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: trends } = useQuery({
    queryKey: ['dashboard', 'trends'],
    queryFn: () => api.get('/dashboard/trends?days=30').then(res => res.data),
  })

  const { data: controlCoverage } = useQuery({
    queryKey: ['dashboard', 'control-coverage'],
    queryFn: () => api.get('/dashboard/control-coverage').then(res => res.data),
  })

  const { data: topRisks } = useQuery({
    queryKey: ['dashboard', 'top-risks'],
    queryFn: () => api.get('/dashboard/top-risks?limit=5').then(res => res.data),
  })

  const { data: remediationProgress } = useQuery({
    queryKey: ['dashboard', 'remediation-progress'],
    queryFn: () => api.get('/dashboard/remediation-progress').then(res => res.data),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return 'text-severity-critical'
    if (score >= 50) return 'text-severity-high'
    if (score >= 20) return 'text-severity-medium'
    return 'text-severity-low'
  }

  const getRiskScoreLabel = (score: number) => {
    if (score >= 80) return 'HIGH RISK'
    if (score >= 50) return 'MEDIUM RISK'
    if (score >= 20) return 'LOW RISK'
    return 'MINIMAL RISK'
  }

  return (
    <div className="space-y-6">
      {/* Hero Section - Compliance Health Score */}
      <Card className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="text-center py-8">
          <h2 className="text-2xl font-semibold mb-4">Compliance Health Score</h2>
          <div className={`text-6xl font-bold mb-2 ${getRiskScoreColor(overview?.risk_score || 0)}`}>
            {overview?.risk_score || 0}/100
          </div>
          <div className="w-full max-w-2xl mx-auto bg-white/20 rounded-full h-4 mb-4">
            <div 
              className="bg-white rounded-full h-4 transition-all duration-500"
              style={{ width: `${overview?.risk_score || 0}%` }}
            />
          </div>
          <div className="flex justify-center gap-8 text-sm">
            <span className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-severity-critical" />
              {overview?.severity_breakdown?.CRITICAL || 0} Critical
            </span>
            <span className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-severity-high" />
              {overview?.severity_breakdown?.HIGH || 0} High
            </span>
            <span className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-severity-medium" />
              {overview?.severity_breakdown?.MEDIUM || 0} Medium
            </span>
          </div>
          <div className="mt-6">
            <Button variant="secondary" size="lg">
              Schedule Scan
            </Button>
            <span className="ml-4 text-sm opacity-90">
              Last scan: {overview?.last_scan ? format(new Date(overview.last_scan), 'PPp') : 'Never'}
            </span>
          </div>
        </div>
      </Card>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Risk Score</p>
              <p className={`text-3xl font-bold ${getRiskScoreColor(overview?.risk_score || 0)}`}>
                {overview?.risk_score || 0}/100
              </p>
              <p className="text-xs text-gray-500 mt-1">{getRiskScoreLabel(overview?.risk_score || 0)}</p>
            </div>
            <Shield className={`w-12 h-12 ${getRiskScoreColor(overview?.risk_score || 0)}`} />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Findings</p>
              <p className="text-3xl font-bold">{overview?.total_findings || 0}</p>
              <p className="text-xs text-green-600 mt-1">↑ 12 from last scan</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-aws-orange" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Compliance Rate</p>
              <p className="text-3xl font-bold">{overview?.compliance_rate || 0}%</p>
              <p className="text-xs text-green-600 mt-1">↑ 5% this week</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Last Scan</p>
              <p className="text-lg font-semibold">
                {overview?.last_scan ? format(new Date(overview.last_scan), 'PPp') : 'Never'}
              </p>
              <Button variant="primary" size="sm" className="mt-2">
                Scan Now
              </Button>
            </div>
            <Clock className="w-12 h-12 text-primary-600" />
          </div>
        </Card>
      </div>

      {/* Dashboard Widgets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Risks Widget */}
        <TopRisksWidget risks={topRisks?.risks || []} />

        {/* Compliance Trends Widget */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Compliance Trends</h3>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          <ComplianceTrendChart data={trends?.trends || []} />
          <div className="mt-4 text-center">
            <Button variant="ghost" size="sm">View Details →</Button>
          </div>
        </Card>

        {/* AWS Accounts Widget */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">AWS Accounts</h3>
            <Server className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Production (us-east-1)</p>
                <p className="text-sm text-gray-600">{overview?.total_findings || 0} findings</p>
              </div>
              <Button variant="primary" size="sm">Scan Now</Button>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-400">+ Add Account</p>
            </div>
          </div>
          <div className="mt-4 text-center">
            <Button variant="ghost" size="sm">Manage Accounts →</Button>
          </div>
        </Card>

        {/* Recent Activity Widget */}
        <RecentActivityWidget activities={overview?.recent_activity || []} />

        {/* Control Coverage Widget */}
        <ControlCoverageWidget coverage={controlCoverage} />

        {/* Remediation Progress Widget */}
        <RemediationProgressWidget progress={remediationProgress} />
      </div>

      {/* Priority Findings */}
      <PriorityFindings />
    </div>
  )
}
