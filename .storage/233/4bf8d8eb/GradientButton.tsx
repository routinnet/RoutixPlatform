import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface GradientButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

export function GradientButton({
  children,
  className,
  variant = 'primary',
  ...props 
}: GradientButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        'relative px-6 py-3 rounded-2xl',
        'font-semibold text-white',
        'shadow-[0_4px_15px_rgba(107,93,211,0.3)]',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        
        // Gradient background
        variant === 'primary' && 'bg-gradient-to-r from-[#6B5DD3] to-[#8B7AFF]',
        variant === 'secondary' && 'bg-gradient-to-r from-[#7AA3FF] to-[#A8C5FF]',
        
        // Hover effect
        'hover:shadow-[0_6px_20px_rgba(107,93,211,0.4)]',
        
        className
      )}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center">
        {children}
      </span>
    </motion.button>
  )
}