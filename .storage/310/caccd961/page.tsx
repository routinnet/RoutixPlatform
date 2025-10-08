'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Logo } from '@/components/ui/Logo'
import { useAuth } from '@/lib/auth'
import { Eye, EyeOff, Check, X } from 'lucide-react'
import Link from 'next/link'

export default function RegisterPage() {
  const { register } = useAuth()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  // Password validation
  const passwordValidation = {
    length: formData.password.length >= 8,
    uppercase: /[A-Z]/.test(formData.password),
    lowercase: /[a-z]/.test(formData.password),
    number: /\d/.test(formData.password),
  }

  const isPasswordValid = Object.values(passwordValidation).every(Boolean)
  const passwordsMatch = formData.password === formData.confirmPassword && formData.confirmPassword.length > 0

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isPasswordValid || !passwordsMatch) return

    setLoading(true)
    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      })
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

        {/* Register Card */}
        <GlassCard className="p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h1 className="text-3xl font-bold text-text-primary mb-2 text-center">
              Join Routix
            </h1>
            <p className="text-text-secondary text-center mb-8">
              Create your account to start generating thumbnails
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
                  placeholder="Choose a username"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary placeholder:text-text-muted bg-white/20 backdrop-blur-xl"
                  placeholder="Enter your email"
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
                    placeholder="Create a password"
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

                {/* Password Requirements */}
                {formData.password && (
                  <div className="mt-3 space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      {passwordValidation.length ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <X className="w-4 h-4 text-red-500" />
                      )}
                      <span className={passwordValidation.length ? 'text-green-600' : 'text-text-muted'}>
                        At least 8 characters
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {passwordValidation.uppercase ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <X className="w-4 h-4 text-red-500" />
                      )}
                      <span className={passwordValidation.uppercase ? 'text-green-600' : 'text-text-muted'}>
                        One uppercase letter
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {passwordValidation.number ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <X className="w-4 h-4 text-red-500" />
                      )}
                      <span className={passwordValidation.number ? 'text-green-600' : 'text-text-muted'}>
                        One number
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className="w-full px-4 py-3 pr-12 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary placeholder:text-text-muted bg-white/20 backdrop-blur-xl"
                    placeholder="Confirm your password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5 text-text-muted" />
                    ) : (
                      <Eye className="w-5 h-5 text-text-muted" />
                    )}
                  </button>
                </div>

                {formData.confirmPassword && (
                  <div className="mt-2 flex items-center gap-2 text-sm">
                    {passwordsMatch ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <X className="w-4 h-4 text-red-500" />
                    )}
                    <span className={passwordsMatch ? 'text-green-600' : 'text-red-500'}>
                      {passwordsMatch ? 'Passwords match' : 'Passwords do not match'}
                    </span>
                  </div>
                )}
              </div>

              <GradientButton
                type="submit"
                loading={loading}
                className="w-full"
                disabled={!formData.username || !formData.email || !isPasswordValid || !passwordsMatch}
              >
                Create Account
              </GradientButton>
            </form>

            <p className="text-center text-text-secondary mt-6">
              Already have an account?{' '}
              <Link 
                href="/login" 
                className="text-routix-purple hover:text-routix-purple-light font-semibold transition-colors"
              >
                Sign in
              </Link>
            </p>
          </motion.div>
        </GlassCard>
      </motion.div>
    </div>
  )
}