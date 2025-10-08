'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ProtectedRoute, useAuth } from '@/lib/auth'
import { GlassCard } from '@/components/ui/GlassCard'
import { Logo } from '@/components/ui/Logo'
import { 
  LayoutDashboard, 
  Users, 
  FileImage, 
  BarChart3, 
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const adminNavItems = [
  { href: '/admin', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/admin/templates', icon: FileImage, label: 'Templates' },
  { href: '/admin/users', icon: Users, label: 'Users' },
  { href: '/admin/analytics', icon: BarChart3, label: 'Analytics' },
  { href: '/admin/settings', icon: Settings, label: 'Settings' },
]

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, logout } = useAuth()
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Check if user is admin
  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin'

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gradient-main flex items-center justify-center p-4">
        <GlassCard className="p-8 text-center">
          <h1 className="text-2xl font-bold text-text-primary mb-4">
            Access Denied
          </h1>
          <p className="text-text-secondary">
            You don't have permission to access the admin panel.
          </p>
        </GlassCard>
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-main">
        {/* Animated gradient orbs */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute w-96 h-96 bg-purple-300/20 rounded-full blur-3xl"
            animate={{
              x: [0, 100, 0],
              y: [0, -100, 0],
            }}
            transition={{ duration: 20, repeat: Infinity }}
            style={{ top: '10%', left: '20%' }}
          />
          <motion.div
            className="absolute w-96 h-96 bg-blue-300/20 rounded-full blur-3xl"
            animate={{
              x: [0, -100, 0],
              y: [0, 100, 0],
            }}
            transition={{ duration: 25, repeat: Infinity }}
            style={{ bottom: '10%', right: '20%' }}
          />
        </div>

        <div className="flex h-screen">
          {/* Sidebar */}
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: sidebarOpen ? 0 : -300 }}
            className="fixed inset-y-0 left-0 z-50 w-64 lg:relative lg:translate-x-0 lg:block"
          >
            <GlassCard className="h-full rounded-none lg:rounded-r-3xl p-6">
              {/* Logo */}
              <div className="flex items-center gap-3 mb-8">
                <Logo className="w-8 h-8" />
                <div>
                  <h2 className="font-bold text-text-primary">Routix Admin</h2>
                  <p className="text-sm text-text-muted">Management Panel</p>
                </div>
              </div>

              {/* Navigation */}
              <nav className="space-y-2 mb-8">
                {adminNavItems.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link key={item.href} href={item.href}>
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`
                          flex items-center gap-3 px-4 py-3 rounded-2xl transition-all
                          ${isActive 
                            ? 'bg-gradient-purple text-white shadow-button' 
                            : 'hover:bg-white/20 text-text-primary'
                          }
                        `}
                      >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.label}</span>
                      </motion.div>
                    </Link>
                  )
                })}
              </nav>

              {/* User Profile */}
              <div className="mt-auto">
                <GlassCard className="p-4 bg-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-purple flex items-center justify-center text-white font-bold">
                      {user?.username?.[0]?.toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{user?.username}</p>
                      <p className="text-sm text-text-muted capitalize">{user?.role}</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={logout}
                    className="flex items-center gap-2 w-full px-3 py-2 rounded-xl hover:bg-white/20 transition-colors text-text-secondary hover:text-text-primary"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm">Logout</span>
                  </button>
                </GlassCard>
              </div>
            </GlassCard>
          </motion.div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* Header */}
            <header className="p-6 lg:p-8">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="lg:hidden p-2 rounded-xl hover:bg-white/20 transition-colors"
                >
                  {sidebarOpen ? (
                    <X className="w-6 h-6 text-text-primary" />
                  ) : (
                    <Menu className="w-6 h-6 text-text-primary" />
                  )}
                </button>

                <div className="flex items-center gap-4">
                  <GlassCard className="px-4 py-2">
                    <span className="text-sm text-text-secondary">
                      Welcome back, <span className="font-semibold text-text-primary">{user?.username}</span>
                    </span>
                  </GlassCard>
                </div>
              </div>
            </header>

            {/* Page Content */}
            <main className="flex-1 px-6 lg:px-8 pb-8 overflow-auto">
              {children}
            </main>
          </div>
        </div>

        {/* Sidebar Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </div>
    </ProtectedRoute>
  )
}