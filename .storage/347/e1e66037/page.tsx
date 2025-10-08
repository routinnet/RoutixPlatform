'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Upload, Search, Filter, Edit, Trash2, Eye, Plus, Image } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { UploadZone } from '@/components/admin/UploadZone'
import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'

interface Template {
  id: string
  name: string
  category: string
  preview_url: string
  created_at: string
  usage_count: number
  status: 'active' | 'inactive'
}

const mockTemplates: Template[] = [
  {
    id: '1',
    name: 'Gaming Thumbnail',
    category: 'Gaming',
    preview_url: '/api/placeholder/300/200',
    created_at: '2024-01-15',
    usage_count: 245,
    status: 'active'
  },
  {
    id: '2',
    name: 'Tutorial Template',
    category: 'Education',
    preview_url: '/api/placeholder/300/200',
    created_at: '2024-01-12',
    usage_count: 189,
    status: 'active'
  },
  {
    id: '3',
    name: 'Music Video',
    category: 'Music',
    preview_url: '/api/placeholder/300/200',
    created_at: '2024-01-10',
    usage_count: 156,
    status: 'inactive'
  }
]

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>(mockTemplates)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showUpload, setShowUpload] = useState(false)

  const categories = ['all', 'Gaming', 'Education', 'Music', 'Business', 'Tech']

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleUpload = useCallback(async (files: File[]) => {
    for (const file of files) {
      // Simulate upload process
      toast.success(`Uploading ${file.name}...`)
      
      // Add to templates list (mock)
      const newTemplate: Template = {
        id: Date.now().toString(),
        name: file.name.replace(/\.[^/.]+$/, ""),
        category: 'Uncategorized',
        preview_url: URL.createObjectURL(file),
        created_at: new Date().toISOString().split('T')[0],
        usage_count: 0,
        status: 'active'
      }
      
      setTemplates(prev => [newTemplate, ...prev])
    }
    
    setShowUpload(false)
  }, [])

  const handleDelete = (id: string) => {
    setTemplates(prev => prev.filter(t => t.id !== id))
    toast.success('Template deleted successfully')
  }

  const handleStatusToggle = (id: string) => {
    setTemplates(prev => prev.map(t => 
      t.id === id 
        ? { ...t, status: t.status === 'active' ? 'inactive' : 'active' }
        : t
    ))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Template Management</h1>
          <p className="text-text-secondary mt-1">Manage and organize your thumbnail templates</p>
        </div>
        
        <GradientButton
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Upload Template
        </GradientButton>
      </div>

      {/* Search and Filters */}
      <GlassCard className="p-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-muted" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-routix-purple/50 text-text-primary placeholder:text-text-muted"
            />
          </div>

          {/* Category Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-muted" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="pl-10 pr-8 py-3 bg-white/10 border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-routix-purple/50 text-text-primary appearance-none cursor-pointer"
            >
              {categories.map(category => (
                <option key={category} value={category} className="bg-routix-dark text-text-primary">
                  {category === 'all' ? 'All Categories' : category}
                </option>
              ))}
            </select>
          </div>
        </div>
      </GlassCard>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredTemplates.map((template, index) => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard className="overflow-hidden group hover:scale-105 transition-transform duration-300">
              {/* Template Preview */}
              <div className="relative aspect-video bg-gradient-to-br from-routix-purple/20 to-routix-blue/20">
                <img
                  src={template.preview_url}
                  alt={template.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.style.display = 'none'
                  }}
                />
                
                {/* Overlay Actions */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2">
                  <button
                    className="p-2 bg-white/20 backdrop-blur-sm rounded-lg hover:bg-white/30 transition-colors"
                    title="Preview"
                  >
                    <Eye className="w-4 h-4 text-white" />
                  </button>
                  <button
                    className="p-2 bg-white/20 backdrop-blur-sm rounded-lg hover:bg-white/30 transition-colors"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4 text-white" />
                  </button>
                  <button
                    onClick={() => handleDelete(template.id)}
                    className="p-2 bg-red-500/20 backdrop-blur-sm rounded-lg hover:bg-red-500/30 transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4 text-white" />
                  </button>
                </div>

                {/* Status Badge */}
                <div className="absolute top-2 right-2">
                  <button
                    onClick={() => handleStatusToggle(template.id)}
                    className={`px-2 py-1 rounded-full text-xs font-medium backdrop-blur-sm ${
                      template.status === 'active'
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                        : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                    }`}
                  >
                    {template.status}
                  </button>
                </div>
              </div>

              {/* Template Info */}
              <div className="p-4">
                <h3 className="font-semibold text-text-primary mb-1 truncate">
                  {template.name}
                </h3>
                <div className="flex items-center justify-between text-sm text-text-secondary">
                  <span className="bg-routix-purple/20 px-2 py-1 rounded-full">
                    {template.category}
                  </span>
                  <span>{template.usage_count} uses</span>
                </div>
                <div className="text-xs text-text-muted mt-2">
                  Created: {new Date(template.created_at).toLocaleDateString()}
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredTemplates.length === 0 && (
        <GlassCard className="p-12 text-center">
          <Image className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No templates found
          </h3>
          <p className="text-text-secondary mb-4">
            {searchTerm || selectedCategory !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Upload your first template to get started'
            }
          </p>
          {!searchTerm && selectedCategory === 'all' && (
            <GradientButton onClick={() => setShowUpload(true)}>
              Upload Template
            </GradientButton>
          )}
        </GlassCard>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-2xl"
          >
            <GlassCard className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-text-primary">Upload Templates</h2>
                <button
                  onClick={() => setShowUpload(false)}
                  className="text-text-muted hover:text-text-primary transition-colors"
                >
                  ✕
                </button>
              </div>
              
              <UploadZone
                onUpload={handleUpload}
                acceptedTypes={{
                  'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
                }}
                maxSize={10 * 1024 * 1024} // 10MB
                multiple
              />
            </GlassCard>
          </motion.div>
        </div>
      )}
    </div>
  )
}