import { useState } from 'react';
import { Upload, Search, Filter, Trash2, Edit, Eye, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';

interface Template {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  file_path: string;
  thumbnail_url: string;
  created_at: string;
  view_count: number;
  download_count: number;
}

export default function TemplateBank() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [uploadMode, setUploadMode] = useState(false);
  const { toast } = useToast();

  const categories = [
    'all',
    'gaming',
    'tech',
    'cooking',
    'vlog',
    'education',
    'entertainment',
    'other'
  ];

  const handleFileUpload = async (files: FileList) => {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    try {
      // Upload to backend
      const response = await fetch('/api/v1/templates/batch-upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast({
          title: "موفق!",
          description: `${files.length} تامبنیل با موفقیت آپلود شد`,
        });
        // Refresh templates
        loadTemplates();
      }
    } catch (error) {
      toast({
        title: "خطا",
        description: "آپلود با مشکل مواجه شد",
        variant: "destructive"
      });
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/v1/templates/search', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setTemplates(data.results || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleDelete = async (templateId: string) => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این تامبنیل را حذف کنید؟')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/templates/${templateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast({
          title: "حذف شد",
          description: "تامبنیل با موفقیت حذف شد",
        });
        loadTemplates();
      }
    } catch (error) {
      toast({
        title: "خطا",
        description: "حذف با مشکل مواجه شد",
        variant: "destructive"
      });
    }
  };

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-950 via-purple-900 to-fuchsia-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">بانک تامبنیل‌های مخفی</h1>
            <p className="text-white/60">مدیریت تامبنیل‌های طراحی شده توسط تیم طراحان</p>
          </div>
          <Button
            onClick={() => setUploadMode(!uploadMode)}
            className="bg-white text-purple-900 hover:bg-white/90"
          >
            <Upload className="w-4 h-4 mr-2" />
            آپلود تامبنیل جدید
          </Button>
        </div>

        {/* Upload Zone */}
        {uploadMode && (
          <Card className="glass mb-6 p-8">
            <div
              className="border-2 border-dashed border-white/30 rounded-lg p-12 text-center hover:border-white/60 transition-colors cursor-pointer"
              onDrop={(e) => {
                e.preventDefault();
                handleFileUpload(e.dataTransfer.files);
              }}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <Upload className="w-16 h-16 mx-auto mb-4 text-white/60" />
              <h3 className="text-xl font-semibold text-white mb-2">
                تامبنیل‌های خود را اینجا رها کنید
              </h3>
              <p className="text-white/60 mb-4">
                یا کلیک کنید تا فایل‌ها را انتخاب کنید
              </p>
              <p className="text-sm text-white/40">
                فرمت‌های پشتیبانی شده: JPG, PNG (حداکثر 10MB)
              </p>
              <input
                id="file-input"
                type="file"
                multiple
                accept="image/jpeg,image/png,image/jpg"
                className="hidden"
                onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
              />
            </div>
          </Card>
        )}

        {/* Filters */}
        <div className="glass rounded-2xl p-6 mb-6">
          <div className="flex gap-4 flex-wrap">
            {/* Search */}
            <div className="flex-1 min-w-[300px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="جستجو در تامبنیل‌ها..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/40"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="flex gap-2">
              <Filter className="text-white/60 w-5 h-5 mt-2" />
              {categories.map((category) => (
                <Button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  className={selectedCategory === category 
                    ? "bg-white text-purple-900" 
                    : "bg-white/10 text-white border-white/20 hover:bg-white/20"
                  }
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'کل تامبنیل‌ها', value: templates.length, icon: '🎨' },
            { label: 'دسته‌بندی‌ها', value: new Set(templates.map(t => t.category)).size, icon: '📁' },
            { label: 'بازدید کل', value: templates.reduce((sum, t) => sum + t.view_count, 0), icon: '👁️' },
            { label: 'دانلود کل', value: templates.reduce((sum, t) => sum + t.download_count, 0), icon: '⬇️' },
          ].map((stat, i) => (
            <Card key={i} className="glass p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/60 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold text-white">{stat.value.toLocaleString()}</p>
                </div>
                <span className="text-4xl">{stat.icon}</span>
              </div>
            </Card>
          ))}
        </div>

        {/* Templates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="glass overflow-hidden group hover:scale-105 transition-transform">
              {/* Thumbnail Image */}
              <div className="relative aspect-video bg-white/5">
                <img
                  src={template.thumbnail_url || '/placeholder.jpg'}
                  alt={template.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="absolute bottom-4 left-4 right-4 flex gap-2">
                    <Button size="sm" variant="secondary" className="flex-1">
                      <Eye className="w-4 h-4 mr-1" />
                      پیش‌نمایش
                    </Button>
                    <Button size="sm" variant="secondary">
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="secondary">
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="destructive"
                      onClick={() => handleDelete(template.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Template Info */}
              <div className="p-4">
                <h3 className="font-semibold text-white mb-1 truncate">{template.title}</h3>
                <p className="text-sm text-white/60 mb-3 line-clamp-2">{template.description}</p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-3">
                  {template.tags.slice(0, 3).map((tag, i) => (
                    <span
                      key={i}
                      className="text-xs px-2 py-1 rounded-full bg-white/10 text-white/80"
                    >
                      {tag}
                    </span>
                  ))}
                  {template.tags.length > 3 && (
                    <span className="text-xs px-2 py-1 text-white/60">
                      +{template.tags.length - 3}
                    </span>
                  )}
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-sm text-white/60">
                  <span className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    {template.view_count}
                  </span>
                  <span className="flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    {template.download_count}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-xs">
                    {template.category}
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {filteredTemplates.length === 0 && (
          <Card className="glass p-12 text-center">
            <div className="text-6xl mb-4">🎨</div>
            <h3 className="text-2xl font-semibold text-white mb-2">
              تامبنیلی پیدا نشد
            </h3>
            <p className="text-white/60 mb-6">
              {searchQuery || selectedCategory !== 'all' 
                ? 'فیلترها را تغییر دهید یا جستجوی دیگری انجام دهید'
                : 'تامبنیل اول خود را آپلود کنید'
              }
            </p>
            {!uploadMode && (
              <Button
                onClick={() => setUploadMode(true)}
                className="bg-white text-purple-900 hover:bg-white/90"
              >
                <Upload className="w-4 h-4 mr-2" />
                شروع آپلود
              </Button>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}
