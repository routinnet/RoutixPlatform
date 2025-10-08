import { motion, HTMLMotionProps } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface GradientButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode
  loading?: boolean
  variant?: 'primary' | 'secondary'
}

export function GradientButton({
  children,
  className,
  loading = false,
  variant = 'primary',
  disabled,
  ...props
}: GradientButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        'relative px-6 py-3 rounded-2xl font-semibold text-white',
        'shadow-button transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variant === 'primary' && 'bg-gradient-purple hover:shadow-button-hover',
        variant === 'secondary' && 'bg-gradient-blue hover:shadow-button-hover',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          Loading...
        </span>
      ) : (
        children
      )}
    </motion.button>
  )
}