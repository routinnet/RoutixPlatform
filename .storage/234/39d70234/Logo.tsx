import { cn } from '@/lib/utils'

interface LogoProps {
  className?: string
}

export function Logo({ className }: LogoProps) {
  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div className="relative">
        {/* RX Logo Design */}
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#6B5DD3] to-[#8B7AFF] flex items-center justify-center shadow-lg">
          <span className="text-white font-bold text-xl">RX</span>
        </div>
        
        {/* Glow effect */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#6B5DD3] to-[#8B7AFF] blur-md opacity-30 -z-10" />
      </div>
    </div>
  )
}