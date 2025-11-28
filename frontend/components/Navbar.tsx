import Link from 'next/link'
import { Activity, Settings, Home } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <Activity className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold">Silent Epidemic Detector</span>
          </Link>

          <div className="flex items-center gap-6">
            <Link
              href="/"
              className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors"
            >
              <Home className="w-5 h-5" />
              <span>Dashboard</span>
            </Link>
            <Link
              href="/settings"
              className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors"
            >
              <Settings className="w-5 h-5" />
              <span>Settings</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
