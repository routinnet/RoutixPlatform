import { Button } from "@/components/ui/button";
import { Sparkles, Zap, ArrowRight } from "lucide-react";

export default function WelcomePage() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-violet-950 via-purple-900 to-fuchsia-900">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItaDJWMzZoLTJ6bTAtNGgydjJoMnYtMmgtNHptMCAydjJoMnYtMmgtMnptLTIgMGgtMnYyaDJ2LTJ6bTIgMGgydjJoLTJ2LTJ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-20"></div>
      
      {/* Gradient Orbs */}
      <div className="absolute top-0 -left-4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
      <div className="absolute -bottom-8 right-0 w-96 h-96 bg-fuchsia-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-700"></div>
      
      {/* Content */}
      <div className="relative min-h-screen flex flex-col items-center justify-center p-6">
        <div className="max-w-4xl mx-auto text-center space-y-12">
          
          {/* Badge */}
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-white/80 text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              <span>AI-Powered Platform</span>
            </span>
          </div>

          {/* Hero Text */}
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-150">
            <h1 className="text-6xl md:text-8xl font-bold text-white tracking-tight">
              Routix
            </h1>
            <p className="text-xl md:text-2xl text-white/70 font-light max-w-2xl mx-auto leading-relaxed">
              Create stunning thumbnails with AI
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
            <Button 
              size="lg" 
              className="bg-white text-purple-900 hover:bg-white/90 font-semibold px-8 py-6 text-lg rounded-2xl shadow-2xl shadow-purple-500/20 transition-all hover:scale-105"
            >
              Get Started
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            
            <Button 
              size="lg" 
              variant="outline" 
              className="glass text-white border-white/20 hover:bg-white/10 font-semibold px-8 py-6 text-lg rounded-2xl backdrop-blur-xl"
            >
              <Zap className="w-5 h-5 mr-2" />
              View Demo
            </Button>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 animate-in fade-in slide-in-from-bottom-10 duration-700 delay-500">
            {[
              { icon: "⚡", text: "Lightning Fast" },
              { icon: "🎨", text: "Beautiful Design" },
              { icon: "🤖", text: "AI-Powered" }
            ].map((feature, i) => (
              <div 
                key={i}
                className="glass-light rounded-3xl p-8 hover:scale-105 transition-transform duration-300 cursor-pointer group"
              >
                <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">{feature.icon}</div>
                <p className="text-white/90 font-medium text-lg">{feature.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
