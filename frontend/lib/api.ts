import axios from 'axios'
import { Alert, AlertResponse, AlertStats, SystemStats } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Alerts
  async getAlerts(params: {
    page?: number
    page_size?: number
    ward?: string
    severity?: string
    status?: string
    min_confidence?: number
  }): Promise<AlertResponse> {
    const response = await apiClient.get('/alerts/', { params })
    return response.data
  },

  async getAlertById(alertId: string): Promise<Alert> {
    const response = await apiClient.get(`/alerts/${alertId}`)
    return response.data
  },

  async updateAlertStatus(alertId: string, status: string): Promise<Alert> {
    const response = await apiClient.patch(`/alerts/${alertId}/status`, null, {
      params: { status }
    })
    return response.data
  },

  async getAlertStats(): Promise<AlertStats> {
    const response = await apiClient.get('/alerts/stats/summary')
    return response.data
  },

  // System
  async getSystemHealth(): Promise<any> {
    const response = await apiClient.get('/system/health')
    return response.data
  },

  async getSystemStats(): Promise<SystemStats> {
    const response = await apiClient.get('/system/stats')
    return response.data
  },

  async triggerAggregation(): Promise<any> {
    const response = await apiClient.post('/system/run-aggregation')
    return response.data
  },

  async triggerDetection(): Promise<any> {
    const response = await apiClient.post('/system/run-detection')
    return response.data
  },
}
