import Link from 'next/link'
import { Alert } from '@/lib/types'
import { formatRelativeTime, getSeverityColor, getStatusColor } from '@/lib/utils'
import { MapPin, AlertTriangle } from 'lucide-react'

interface AlertCardProps {
  alert: Alert
}

export default function AlertCard({ alert }: AlertCardProps) {
  return (
    <Link href={`/alert/${alert.alert_id}`}>
      <div className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer bg-white">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className={`w-5 h-5 ${
              alert.severity === 'critical' ? 'text-red-600' :
              alert.severity === 'high' ? 'text-orange-600' :
              alert.severity === 'medium' ? 'text-yellow-600' :
              'text-green-600'
            }`} />
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
              {alert.severity.toUpperCase()}
            </span>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(alert.status)}`}>
            {alert.status}
          </span>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
          <MapPin className="w-4 h-4" />
          <span className="font-medium">{alert.location.ward}</span>
        </div>

        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Confidence:</span>
            <span className="font-medium">{(alert.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Anomaly Score:</span>
            <span className="font-medium">{alert.anomaly_score.toFixed(3)}</span>
          </div>
        </div>

        <div className="mt-3 text-xs text-gray-500">
          {formatRelativeTime(alert.timestamp)}
        </div>
      </div>
    </Link>
  )
}
