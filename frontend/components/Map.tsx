'use client'

import { useEffect, useRef } from 'react'
import L from 'leaflet'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { Alert } from '@/lib/types'

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom marker icons based on severity
const getMarkerIcon = (severity: string) => {
  const colors = {
    low: '#22c55e',
    medium: '#eab308',
    high: '#f97316',
    critical: '#ef4444',
  }
  
  const color = colors[severity as keyof typeof colors] || colors.medium
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  })
}

interface MapProps {
  alerts: Alert[]
}

function MapUpdater({ alerts }: { alerts: Alert[] }) {
  const map = useMap()
  
  useEffect(() => {
    if (alerts.length > 0) {
      const bounds = L.latLngBounds(
        alerts.map(alert => [alert.location.lat, alert.location.lon])
      )
      map.fitBounds(bounds, { padding: [50, 50] })
    }
  }, [alerts, map])
  
  return null
}

export default function Map({ alerts }: MapProps) {
  // Mumbai center coordinates
  const center: [number, number] = [19.0760, 72.8777]
  
  return (
    <MapContainer
      center={center}
      zoom={11}
      style={{ height: '100%', width: '100%' }}
      className="rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <MapUpdater alerts={alerts} />
      
      {alerts.map((alert) => (
        <Marker
          key={alert.alert_id}
          position={[alert.location.lat, alert.location.lon]}
          icon={getMarkerIcon(alert.severity)}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold text-lg mb-2">{alert.location.ward}</h3>
              <div className="space-y-1 text-sm">
                <p><strong>Severity:</strong> <span className="capitalize">{alert.severity}</span></p>
                <p><strong>Confidence:</strong> {(alert.confidence * 100).toFixed(1)}%</p>
                <p><strong>Status:</strong> <span className="capitalize">{alert.status}</span></p>
                <a
                  href={`/alert/${alert.alert_id}`}
                  className="text-blue-600 hover:underline block mt-2"
                >
                  View Details →
                </a>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
