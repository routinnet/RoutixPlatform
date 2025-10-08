export function Logo({ className = "w-12 h-12" }: { className?: string }) {
  return (
    <svg 
      className={className} 
      viewBox="0 0 100 100" 
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* RK Logo - Purple gradient */}
      <text 
        x="50%" 
        y="50%" 
        dominantBaseline="middle" 
        textAnchor="middle"
        className="font-bold fill-routix-purple"
        fontSize="48"
      >
        RK
      </text>
    </svg>
  )
}