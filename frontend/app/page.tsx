'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import { AlertTriangle, Activity, MapPin, TrendingUp } from 'lucide-react'
import { api } from '@/lib/api'
import { Alert, AlertStats } from '@/lib/types'
import AlertCard from '@/components/AlertCard'
import StatCard from '@/components/StatCard'
import Loader from '@/components/Loader'

// Dynamically import map to avoid SSR issues
const Map = dynamic(() => import('@/components/Map'), { ssr: false })
const TimeSeriesChart = dynamic(() => import('@/components/TimeSeriesChart'), { ssr: false })

export default function Dashboard() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [stats, setStats] = useState<AlertStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [alertsRes, statsRes] = await Promise.all([
        api.getAlerts({ page: 1, page_size: 50 }),
        api.getAlertStats()
      ])
      setAlerts(alertsRes.alerts)
      setStats(statsRes)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Error Loading Data</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={loadData}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const activeAlerts = alerts.filter(a => a.status === 'active')
  const highPriorityAlerts = alerts.filter(a => 
    a.severity === 'high' || a.severity === 'critical'
  )

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Outbreak Dashboard</h1>
        <p className="text-gray-600">Real-time disease outbreak monitoring for Mumbai</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Alerts"
          value={stats?.total_alerts || 0}
          icon={<AlertTriangle className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          title="Active Alerts"
          value={activeAlerts.length}
          icon={<Activity className="w-6 h-6" />}
          color="orange"
        />
        <StatCard
          title="High Priority"
          value={highPriorityAlerts.length}
          icon={<TrendingUp className="w-6 h-6" />}
          color="red"
        />
        <StatCard
          title="Locations Monitored"
          value={stats?.top_wards?.length || 0}
          icon={<MapPin className="w-6 h-6" />}
          color="green"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Section - 2 columns */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-6 h-[600px]">
            <h2 className="text-2xl font-bold mb-4">Outbreak Hotspots</h2>
            <div className="h-[520px]">
              <Map alerts={alerts} />
            </div>
          </div>
        </div>

        {/* Alerts Sidebar - 1 column */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-lg p-6 h-[600px] flex flex-col">
            <h2 className="text-2xl font-bold mb-4">Recent Alerts</h2>
            <div className="flex-1 overflow-y-auto space-y-4">
              {alerts.slice(0, 10).map((alert) => (
                <AlertCard key={alert.alert_id} alert={alert} />
              ))}
              {alerts.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  No alerts at this time
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Time Series Chart */}
      <div className="mt-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Alert Timeline</h2>
          <TimeSeriesChart alerts={alerts} />
        </div>
      </div>

      {/* Top Wards Table */}
      {stats?.top_wards && stats.top_wards.length > 0 && (
        <div className="mt-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Most Affected Areas</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ward
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Alert Count
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.top_wards.map((ward, idx) => (
                    <tr key={idx}>
                      <td className="px-6 py-4 whitespace-nowrap font-medium">
                        {ward.ward}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {ward.count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          ward.count >= 5 ? 'bg-red-100 text-red-800' :
                          ward.count >= 3 ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {ward.count >= 5 ? 'High' : ward.count >= 3 ? 'Medium' : 'Low'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
