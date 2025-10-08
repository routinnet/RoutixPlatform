'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { apiClient } from '@/lib/api'
import { 
  Users, 
  FileImage, 
  Zap, 
  TrendingUp,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface AdminStats {
  total_users: number
  total_templates: number
  total_generations: number
  active_generations: number
  revenue_today: number
  credits_consumed: number
}

interface RecentActivity {
  id: string
  type: 'user_registered' | 'template_uploaded' | 'generation_completed' | 'generation_failed'
  user: string
  timestamp: string
  details: string
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, activityRes] = await Promise.all([
          apiClient.getAdminStats(),
          apiClient.getRecentActivity()
        ])
        
        setStats(statsRes.data)
        setRecentActivity(activityRes.data)
      } catch (error) {
        console.error('Failed to fetch admin data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.total_users || 0,
      icon: Users,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/20'
    },
    {
      title: 'Templates',
      value: stats?.total_templates || 0,
      icon: FileImage,
      color: 'text-green-500',
      bgColor: 'bg-green-500/20'
    },
    {
      title: 'Generations',
      value: stats?.total_generations || 0,
      icon: Zap,
      color: 'text-routix-purple',
      bgColor: 'bg-routix-purple/20'
    },
    {
      title: 'Revenue Today',
      value: `$${stats?.revenue_today || 0}`,
      icon: TrendingUp,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-500/20'
    }
  ]

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'user_registered':
        return <Users className="w-4 h-4 text-blue-500" />
      case 'template_uploaded':
        return <FileImage className="w-4 h-4 text-green-500" />
      case 'generation_completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'generation_failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Activity className="w-4 h-4 text-text-muted" />
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'user_registered':
        return 'text-blue-600'
      case 'template_uploaded':
        return 'text-green-600'
      case 'generation_completed':
        return 'text-green-600'
      case 'generation_failed':
        return 'text-red-600'
      default:
        return 'text-text-secondary'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <GlassCard key={i} className="p-6 animate-pulse">
              <div className="h-20 bg-white/10 rounded-xl"></div>
            </GlassCard>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-text-primary mb-2">
          Admin Dashboard
        </h1>
        <p className="text-text-secondary">
          Overview of your Routix platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard className="p-6 hover:scale-105 transition-transform">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-text-secondary text-sm font-medium">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-text-primary mt-1">
                    {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                  </p>
                </div>
                <div className={`w-12 h-12 rounded-2xl ${stat.bgColor} flex items-center justify-center`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2"
        >
          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Activity className="w-6 h-6 text-routix-purple" />
              <h2 className="text-xl font-semibold text-text-primary">
                Recent Activity
              </h2>
            </div>

            <div className="space-y-4">
              {recentActivity.length > 0 ? (
                recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start gap-3 p-4 rounded-2xl bg-white/10 hover:bg-white/20 transition-colors"
                  >
                    <div className="mt-0.5">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-text-primary font-medium">
                        <span className={getActivityColor(activity.type)}>
                          {activity.user}
                        </span>{' '}
                        {activity.details}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="w-3 h-3 text-text-muted" />
                        <span className="text-sm text-text-muted">
                          {new Date(activity.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 text-text-muted mx-auto mb-3" />
                  <p className="text-text-secondary">No recent activity</p>
                </div>
              )}
            </div>
          </GlassCard>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <GlassCard className="p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              Quick Actions
            </h2>

            <div className="space-y-3">
              <motion.a
                href="/admin/templates"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-3 p-4 rounded-2xl bg-gradient-purple text-white hover:shadow-button-hover transition-all"
              >
                <FileImage className="w-5 h-5" />
                <span className="font-medium">Manage Templates</span>
              </motion.a>

              <motion.a
                href="/admin/users"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-3 p-4 rounded-2xl bg-white/20 text-text-primary hover:bg-white/30 transition-all"
              >
                <Users className="w-5 h-5" />
                <span className="font-medium">View Users</span>
              </motion.a>

              <motion.a
                href="/admin/analytics"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-3 p-4 rounded-2xl bg-white/20 text-text-primary hover:bg-white/30 transition-all"
              >
                <TrendingUp className="w-5 h-5" />
                <span className="font-medium">View Analytics</span>
              </motion.a>
            </div>
          </GlassCard>

          {/* System Status */}
          <GlassCard className="p-6 mt-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">
              System Status
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">API Status</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-green-600">Online</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Active Generations</span>
                <span className="text-text-primary font-medium">
                  {stats?.active_generations || 0}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Credits Consumed</span>
                <span className="text-text-primary font-medium">
                  {stats?.credits_consumed?.toLocaleString() || 0}
                </span>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  )
}