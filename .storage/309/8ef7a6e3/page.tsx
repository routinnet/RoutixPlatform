'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Logo } from '@/components/ui/Logo'
import { useAuth } from '@/lib/auth'
import { Eye, EyeOff } from 'lucide-react'
import Link from 'next/link'

export default function LoginPage() {
  const { login } = useAuth()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.username || !formData.password) return

    setLoading(true)
    try {
      await login(formData.username, formData.password)
    } catch (error) {
      // Error handled in auth context
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-main p-4">
      {/* Animated gradient orbs */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 bg-purple-300/30 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          style={{ top: '10%', left: '20%' }}
        />
        <motion.div
          className="absolute w-96 h-96 bg-blue-300/30 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          style={{ bottom: '10%', right: '20%' }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1 }}
            className="w-20 h-20 rounded-3xl bg-white/80 backdrop-blur-xl shadow-lg flex items-center justify-center"
          >
            <Logo />
          </motion.div>
        </div>

        {/* Login Card */}
        <GlassCard className="p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h1 className="text-3xl font-bold text-text-primary mb-2 text-center">
              Welcome Back
            </h1>
            <p className="text-text-secondary text-center mb-8">
              Sign in to continue to Routix
            </p>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary placeholder:text-text-muted bg-white/20 backdrop-blur-xl"
                  placeholder="Enter your username"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-4 py-3 pr-12 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary placeholder:text-text-muted bg-white/20 backdrop-blur-xl"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5 text-text-muted" />
                    ) : (
                      <Eye className="w-5 h-5 text-text-muted" />
                    )}
                  </button>
                </div>
              </div>

              <GradientButton
                type="submit"
                loading={loading}
                className="w-full"
                disabled={!formData.username || !formData.password}
              >
                Sign In
              </GradientButton>
            </form>

            <p className="text-center text-text-secondary mt-6">
              Don't have an account?{' '}
              <Link 
                href="/register" 
                className="text-routix-purple hover:text-routix-purple-light font-semibold transition-colors"
              >
                Sign up
              </Link>
            </p>
          </motion.div>
        </GlassCard>
      </motion.div>
    </div>
  )
}