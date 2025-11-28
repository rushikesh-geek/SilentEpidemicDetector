'use client'

import { Alert } from '@/lib/types'
import { format } from 'date-fns'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

interface TimeSeriesChartProps {
  alerts: Alert[]
}

export default function TimeSeriesChart({ alerts }: TimeSeriesChartProps) {
  // Group alerts by date
  const alertsByDate = alerts.reduce((acc, alert) => {
    const date = format(new Date(alert.timestamp), 'MMM dd')
    if (!acc[date]) {
      acc[date] = { date, count: 0, avgConfidence: 0, avgScore: 0 }
    }
    acc[date].count++
    acc[date].avgConfidence += alert.confidence
    acc[date].avgScore += alert.anomaly_score
    return acc
  }, {} as Record<string, any>)

  // Calculate averages and format for chart
  const data = Object.values(alertsByDate).map((day: any) => ({
    date: day.date,
    'Alert Count': day.count,
    'Avg Confidence': (day.avgConfidence / day.count),
    'Avg Anomaly Score': (day.avgScore / day.count),
  })).reverse()

  if (data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-gray-500">
        No data available for chart
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <ReferenceLine y={0.7} yAxisId="right" stroke="red" strokeDasharray="3 3" label="Threshold" />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="Alert Count"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 4 }}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="Avg Anomaly Score"
          stroke="#ef4444"
          strokeWidth={2}
          dot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
