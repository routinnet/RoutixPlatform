import { cn } from '@/lib/utils'
import { motion, HTMLMotionProps } from 'framer-motion'

interface GlassCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode
  hover?: boolean
}

export function GlassCard({ 
  children, 
  className, 
  hover = false,
  ...props 
}: GlassCardProps) {
  return (
    <motion.div
      className={cn(
        'glass rounded-3xl shadow-glass',
        hover && 'hover:shadow-glass-hover hover:scale-[1.01] cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
}