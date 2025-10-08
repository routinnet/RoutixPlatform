import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}

export function GlassCard({ children, className, hover = false }: GlassCardProps) {
  return (
    <div
      className={cn(
        // Base glass effect
        'relative',
        'bg-white/40',
        'backdrop-blur-xl',
        'backdrop-saturate-150',
        'border border-white/50',
        'rounded-3xl',
        'shadow-[0_8px_32px_rgba(31,38,135,0.08)]',
        
        // Inner glow
        'before:absolute before:inset-0',
        'before:rounded-3xl',
        'before:p-[1px]',
        'before:bg-gradient-to-b before:from-white/80 before:to-transparent',
        'before:-z-10',
        
        // Hover effect
        hover && 'transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_12px_40px_rgba(31,38,135,0.12)]',
        
        className
      )}
    >
      {children}
    </div>
  )
}