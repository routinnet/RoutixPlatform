import { motion } from 'framer-motion'
import { GlassCard } from './GlassCard'
import { Clock, CheckCircle, AlertCircle, Loader2, Users } from 'lucide-react'
import { GenerationProgress } from '@/lib/websocket'

interface ProgressIndicatorProps {
  progress: GenerationProgress
  className?: string
}

export function ProgressIndicator({ progress, className }: ProgressIndicatorProps) {
  const getStatusIcon = () => {
    switch (progress.status) {
      case 'queued':
        return <Clock className="w-5 h-5 text-blue-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-routix-purple animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
    }
  }

  const getStatusText = () => {
    switch (progress.status) {
      case 'queued':
        return 'In Queue'
      case 'processing':
        return 'Generating...'
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      default:
        return 'Unknown'
    }
  }

  const getStatusColor = () => {
    switch (progress.status) {
      case 'queued':
        return 'text-blue-600'
      case 'processing':
        return 'text-routix-purple'
      case 'completed':
        return 'text-green-600'
      case 'failed':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatTime = (seconds?: number) => {
    if (!seconds) return '--'
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <GlassCard className={`p-4 ${className}`}>
      <div className="space-y-3">
        {/* Status Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className={`font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </span>
          </div>
          
          {progress.processing_time && (
            <span className="text-sm text-text-muted">
              {formatTime(progress.processing_time)}
            </span>
          )}
        </div>

        {/* Progress Bar */}
        {(progress.status === 'processing' || progress.status === 'queued') && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Progress</span>
              <span className="text-text-primary font-medium">
                {progress.progress}%
              </span>
            </div>
            
            <div className="w-full bg-white/30 rounded-full h-2 overflow-hidden">
              <motion.div
                className="h-2 bg-gradient-to-r from-routix-purple to-routix-purple-light rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress.progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </div>
          </div>
        )}

        {/* Queue Position */}
        {progress.status === 'queued' && progress.queue_position && (
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Users className="w-4 h-4" />
            <span>Position {progress.queue_position} in queue</span>
          </div>
        )}

        {/* Estimated Time */}
        {progress.estimated_time && progress.status !== 'completed' && (
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Clock className="w-4 h-4" />
            <span>Est. {formatTime(progress.estimated_time)} remaining</span>
          </div>
        )}

        {/* Error Message */}
        {progress.status === 'failed' && progress.error_message && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <p className="text-sm text-red-600">
              {progress.error_message}
            </p>
          </div>
        )}

        {/* Completion Info */}
        {progress.status === 'completed' && (
          <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20">
            <p className="text-sm text-green-600">
              ✨ Thumbnail generated successfully!
            </p>
          </div>
        )}
      </div>
    </GlassCard>
  )
}