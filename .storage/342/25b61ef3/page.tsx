'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { UploadZone } from '@/components/admin/UploadZone'
import { apiClient } from '@/lib/api'
import { 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye,
  Plus,
  Grid,
  List
} from 'lucide-react'
import { toast } from 'sonner'

interface Template {
  id: string
  name: string
  category: string
  tags: string[]
  thumbnail_url: string
  created_at: string
  usage_count: number
  status: 'active' | 'inactive'
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showUpload, setShowUpload] = useState(false)

  const categories = ['all', 'gaming', 'tutorial', 'tech', 'lifestyle', 'business']

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      const response = await apiClient.getTemplates()
      setTemplates(response.data)
    } catch (error) {
      toast.error('Failed to fetch templates')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (files: File[]) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    await apiClient.uploadTemplate(formData)
    await fetchTemplates()
    setShowUpload(false)
  }

  const handleDelete = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return

    try {
      await apiClient.deleteTemplate(templateId)
      setTemplates(prev => prev.filter(t => t.id !== templateId))
      toast.success('Template deleted successfully')
    } catch (error) {
      toast.error('Failed to delete template')
    }
  }

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <GlassCard key={i} className="p-4 animate-pulse">
              <div className="aspect-video bg-white/10 rounded-xl mb-4"></div>
              <div className="h-4 bg-white/10 rounded mb-2"></div>
              <div className="h-3 bg-white/10 rounded w-2/3"></div>
            </GlassCard>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Template Management
          </h1>
          <p className="text-text-secondary">
            Manage your thumbnail templates and upload new ones
          </p>
        </div>

        <GradientButton
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Upload Templates
        </GradientButton>
      </div>

      {/* Upload Zone */}
      {showUpload && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <UploadZone
            onUpload={handleUpload}
            acceptedTypes={['image/*']}
            maxFiles={20}
          />
        </motion.div>
      )}

      {/* Filters */}
      <GlassCard className="p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary placeholder:text-text-muted bg-white/20 backdrop-blur-xl"
            />
          </div>

          <div className="flex items-center gap-4">
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary bg-white/20 backdrop-blur-xl"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>

            {/* View Mode */}
            <div className="flex items-center gap-1 p-1 rounded-xl bg-white/20">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-routix-purple text-white' 
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-routix-purple text-white' 
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Templates Grid/List */}
      {filteredTemplates.length > 0 ? (
        <div className={
          viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
        }>
          {filteredTemplates.map((template, index) => (
            <motion.div
              key={template.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              {viewMode === 'grid' ? (
                <GlassCard className="p-4 hover:scale-105 transition-transform">
                  {/* Template Preview */}
                  <div className="aspect-video bg-white/10 rounded-xl mb-4 overflow-hidden">
                    <img
                      src={template.thumbnail_url}
                      alt={template.name}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* Template Info */}
                  <div className="space-y-3">
                    <div>
                      <h3 className="font-semibold text-text-primary truncate">
                        {template.name}
                      </h3>
                      <p className="text-sm text-text-secondary capitalize">
                        {template.category}
                      </p>
                    </div>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1">
                      {template.tags.slice(0, 3).map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-1 text-xs rounded-lg bg-routix-purple/20 text-routix-purple"
                        >
                          {tag}
                        </span>
                      ))}
                      {template.tags.length > 3 && (
                        <span className="px-2 py-1 text-xs rounded-lg bg-white/20 text-text-muted">
                          +{template.tags.length - 3}
                        </span>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center justify-between text-sm text-text-muted">
                      <span>{template.usage_count} uses</span>
                      <span className={`px-2 py-1 rounded-lg ${
                        template.status === 'active' 
                          ? 'bg-green-500/20 text-green-600' 
                          : 'bg-red-500/20 text-red-600'
                      }`}>
                        {template.status}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary">
                        <Eye className="w-4 h-4" />
                        <span className="text-sm">Preview</span>
                      </button>
                      <button className="p-2 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDelete(template.id)}
                        className="p-2 rounded-xl bg-red-500/20 hover:bg-red-500/30 transition-colors text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </GlassCard>
              ) : (
                <GlassCard className="p-6">
                  <div className="flex items-center gap-6">
                    {/* Thumbnail */}
                    <div className="w-24 h-16 bg-white/10 rounded-xl overflow-hidden flex-shrink-0">
                      <img
                        src={template.thumbnail_url}
                        alt={template.name}
                        className="w-full h-full object-cover"
                      />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-text-primary mb-1">
                        {template.name}
                      </h3>
                      <p className="text-sm text-text-secondary mb-2 capitalize">
                        {template.category} • {template.usage_count} uses
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {template.tags.map(tag => (
                          <span
                            key={tag}
                            className="px-2 py-1 text-xs rounded-lg bg-routix-purple/20 text-routix-purple"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <button className="p-2 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDelete(template.id)}
                        className="p-2 rounded-xl bg-red-500/20 hover:bg-red-500/30 transition-colors text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </GlassCard>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <GlassCard className="p-12 text-center">
          <FileImage className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No templates found
          </h3>
          <p className="text-text-secondary mb-6">
            {searchQuery || selectedCategory !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Upload your first template to get started'
            }
          </p>
          {!searchQuery && selectedCategory === 'all' && (
            <GradientButton
              onClick={() => setShowUpload(true)}
              className="mx-auto"
            >
              Upload Templates
            </GradientButton>
          )}
        </GlassCard>
      )}
    </div>
  )
}