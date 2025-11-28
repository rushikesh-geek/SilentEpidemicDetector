export interface Location {
  lat: number
  lon: number
  ward: string
  area?: string
}

export interface RecommendedAction {
  category: string
  action: string
  priority: string
  target: string
  details?: string
}

export interface Evidence {
  hospital: {
    total_events?: number
    has_data?: boolean
    unique_symptoms?: number
    top_symptoms?: Record<string, number>
  }
  social: {
    total_mentions?: number
    has_data?: boolean
    unique_keywords?: number
    top_keywords?: Record<string, number>
  }
  environment: {
    risk_score?: number
    has_data?: boolean
    risk_assessment?: any
  }
  model_scores: {
    z_score?: number
    cusum?: number
    ewma?: number
    lstm_autoencoder?: number
    isolation_forest?: number
    prophet_residual?: number
  }
}

export interface Alert {
  alert_id: string
  timestamp: string
  location: Location
  confidence: number
  anomaly_score: number
  severity: 'low' | 'medium' | 'high' | 'critical'
  evidence: Evidence
  recommended_actions: RecommendedAction[]
  status: 'active' | 'acknowledged' | 'resolved'
  notified: boolean
  metadata?: any
}

export interface AlertResponse {
  alerts: Alert[]
  total: number
  page: number
  page_size: number
}

export interface AlertStats {
  total_alerts: number
  by_severity: Record<string, number>
  by_status: Record<string, number>
  top_wards: Array<{ ward: string; count: number }>
  recent_alerts: any[]
}

export interface SystemStats {
  data_ingestion: {
    hospital_events: number
    social_posts: number
    environment_data: number
  }
  processing: {
    daily_aggregates: number
    anomaly_results: number
  }
  alerts: {
    total: number
    active: number
    high_priority: number
  }
}
