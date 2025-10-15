import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Home, Upload, Image, MessageSquare, Settings, 
  TrendingUp, Users, Zap, Database 
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalTemplates: 0,
    totalGenerations: 0,
    activeUsers: 0,
    successRate: 0
  });

  useEffect(() => {
    // Load stats from API
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStats({
          totalTemplates: data.data?.generation_stats?.total_credits_consumed || 0,
          totalGenerations: data.data?.overview?.total_generations || 0,
          activeUsers: data.data?.overview?.active_users_today || 0,
          successRate: data.data?.generation_stats?.success_rate || 0
        });
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const features = [
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: 'رابط چت هوشمند',
      description: 'تعامل طبیعی با AI برای ساخت تامبنیل',
      status: 'فعال',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <Database className="w-8 h-8" />,
      title: 'بانک تامبنیل مخفی',
      description: 'استفاده از تامبنیل‌های طراحی شده توسط 90 طراح',
      status: 'فعال',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: 'تولید سریع',
      description: 'ساخت تامبنیل در کمتر از 60 ثانیه',
      status: 'فعال',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'الگوریتم‌های متعدد',
      description: 'Routix V1, V2, V3 با قابلیت‌های مختلف',
      status: 'فعال',
      color: 'from-green-500 to-emerald-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-950 via-purple-900 to-fuchsia-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">
            🎨 Routix Platform
          </h1>
          <p className="text-xl text-white/70">
            پلتفرم هوش مصنوعی تولید تامبنیل برای یوتیوبرها
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="glass p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/60 text-sm mb-1">تامبنیل‌ها</p>
                <p className="text-3xl font-bold text-white">{stats.totalTemplates.toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Image className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </Card>

          <Card className="glass p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/60 text-sm mb-1">تولیدها</p>
                <p className="text-3xl font-bold text-white">{stats.totalGenerations.toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Zap className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </Card>

          <Card className="glass p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/60 text-sm mb-1">کاربران فعال</p>
                <p className="text-3xl font-bold text-white">{stats.activeUsers.toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
                <Users className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </Card>

          <Card className="glass p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/60 text-sm mb-1">نرخ موفقیت</p>
                <p className="text-3xl font-bold text-white">{stats.successRate.toFixed(1)}%</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-yellow-500/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-yellow-400" />
              </div>
            </div>
          </Card>
        </div>

        {/* Features */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">ویژگی‌های کلیدی</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="glass p-6 hover:scale-105 transition-transform">
                <div className="flex items-start gap-4">
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-white`}>
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                      <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-medium">
                        {feature.status}
                      </span>
                    </div>
                    <p className="text-white/60">{feature.description}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <Card className="glass p-6">
          <h2 className="text-2xl font-bold text-white mb-4">دسترسی سریع</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button
              onClick={() => window.location.href = '/chat'}
              className="h-24 flex-col bg-white/10 hover:bg-white/20 text-white border border-white/20"
            >
              <MessageSquare className="w-6 h-6 mb-2" />
              <span>رابط چت</span>
            </Button>
            <Button
              onClick={() => window.location.href = '/admin/templates'}
              className="h-24 flex-col bg-white/10 hover:bg-white/20 text-white border border-white/20"
            >
              <Upload className="w-6 h-6 mb-2" />
              <span>بانک تامبنیل</span>
            </Button>
            <Button
              onClick={() => window.location.href = '/history'}
              className="h-24 flex-col bg-white/10 hover:bg-white/20 text-white border border-white/20"
            >
              <Image className="w-6 h-6 mb-2" />
              <span>تاریخچه</span>
            </Button>
            <Button
              onClick={() => window.location.href = '/admin'}
              className="h-24 flex-col bg-white/10 hover:bg-white/20 text-white border border-white/20"
            >
              <Settings className="w-6 h-6 mb-2" />
              <span>تنظیمات</span>
            </Button>
          </div>
        </Card>

        {/* Tech Stack */}
        <Card className="glass p-6 mt-8">
          <h2 className="text-2xl font-bold text-white mb-4">فناوری‌های استفاده شده</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: 'FastAPI', desc: 'Backend' },
              { name: 'React', desc: 'Frontend' },
              { name: 'PostgreSQL', desc: 'Database' },
              { name: 'Redis', desc: 'Cache' },
              { name: 'Celery', desc: 'Workers' },
              { name: 'WebSocket', desc: 'Real-time' }
            ].map((tech, i) => (
              <div key={i} className="text-center">
                <div className="w-full aspect-square rounded-lg bg-white/5 flex items-center justify-center mb-2">
                  <span className="text-3xl">⚡</span>
                </div>
                <p className="text-white font-medium">{tech.name}</p>
                <p className="text-white/60 text-sm">{tech.desc}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Footer Info */}
        <div className="mt-8 text-center text-white/60">
          <p className="mb-2">ساخته شده با ❤️ توسط تیم Routix</p>
          <p className="text-sm">نسخه 1.0.0 - Backend: 90% | Frontend: 75% | کل پروژه: 75%</p>
        </div>
      </div>
    </div>
  );
}
