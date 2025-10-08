import { motion } from 'framer-motion'
import { Clock, Loader2, CheckCircle, AlertCircle } from 'lucide-react'

interface StatusBadgeProps {
  status: 'queued' | 'processing' | 'completed' | 'failed'
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'queued':
        return {
          icon: Clock,
          text: 'Queued',
          bgColor: 'bg-blue-500/20',
          textColor: 'text-blue-600',
          borderColor: 'border-blue-500/30'
        }
      case 'processing':
        return {
          icon: Loader2,
          text: 'Processing',
          bgColor: 'bg-routix-purple/20',
          textColor: 'text-routix-purple',
          borderColor: 'border-routix-purple/30',
          animate: true
        }
      case 'completed':
        return {
          icon: CheckCircle,
          text: 'Completed',
          bgColor: 'bg-green-500/20',
          textColor: 'text-green-600',
          borderColor: 'border-green-500/30'
        }
      case 'failed':
        return {
          icon: AlertCircle,
          text: 'Failed',
          bgColor: 'bg-red-500/20',
          textColor: 'text-red-600',
          borderColor: 'border-red-500/30'
        }
      default:
        return {
          icon: Clock,
          text: 'Unknown',
          bgColor: 'bg-gray-500/20',
          textColor: 'text-gray-600',
          borderColor: 'border-gray-500/30'
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full border
        ${config.bgColor} ${config.textColor} ${config.borderColor}
        ${className}
      `}
    >
      <Icon 
        className={`w-4 h-4 ${config.animate ? 'animate-spin' : ''}`} 
      />
      <span className="text-sm font-medium">
        {config.text}
      </span>
    </motion.div>
  )
}