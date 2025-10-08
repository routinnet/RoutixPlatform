'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ProtectedRoute } from '@/lib/auth'
import { GlassCard } from '@/components/ui/GlassCard'
import { GalleryGrid } from '@/components/gallery/GalleryGrid'
import { FilterBar } from '@/components/gallery/FilterBar'
import { ShareModal } from '@/components/gallery/ShareModal'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'
import { History, Clock, TrendingUp } from 'lucide-react'

interface Generation {
  id: string
  prompt: string
  thumbnail_url?: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  created_at: string
  processing_time?: number
  is_favorite: boolean
  download_count: number
  share_count: number
}

export default function HistoryPage() {
  const [generations, setGenerations] = useState<Generation[]>([])
  const [loading, setLoading] = useState(true)
  const [hasMore, setHasMore] = useState(true)
  const [page, setPage] = useState(1)
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [dateRange, setDateRange] = useState<{ start?: string; end?: string }>({})
  const [showFavorites, setShowFavorites] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'masonry' | 'list'>('grid')
  const [sortBy, setSortBy] = useState('newest')
  
  // Modal states
  const [shareModalOpen, setShareModalOpen] = useState(false)
  const [selectedGeneration, setSelectedGeneration] = useState<Generation | null>(null)

  useEffect(() => {
    fetchGenerations(true)
  }, [searchQuery, statusFilter, dateRange, showFavorites, sortBy])

  const fetchGenerations = async (reset = false) => {
    try {
      setLoading(true)
      const params = {
        page: reset ? 1 : page,
        limit: 20,
        search: searchQuery || undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        start_date: dateRange.start || undefined,
        end_date: dateRange.end || undefined,
        favorites_only: showFavorites || undefined,
        sort_by: sortBy
      }

      const response = await apiClient.getHistory(params)
      const newGenerations = response.data.generations || []
      
      if (reset) {
        setGenerations(newGenerations)
        setPage(2)
      } else {
        setGenerations(prev => [...prev, ...newGenerations])
        setPage(prev => prev + 1)
      }
      
      setHasMore(newGenerations.length === 20)
    } catch (error) {
      toast.error('Failed to fetch generation history')
    } finally {
      setLoading(false)
    }
  }

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      fetchGenerations(false)
    }
  }

  const handleFavorite = async (id: string) => {
    try {
      const generation = generations.find(g => g.id === id)
      if (!generation) return

      if (generation.is_favorite) {
        await apiClient.unfavoriteGeneration(id)
      } else {
        await apiClient.favoriteGeneration(id)
      }

      setGenerations(prev => prev.map(g => 
        g.id === id ? { ...g, is_favorite: !g.is_favorite } : g
      ))
    } catch (error) {
      toast.error('Failed to update favorite status')
    }
  }

  const handleDownload = async (id: string, format = 'png') => {
    try {
      const response = await apiClient.downloadGeneration(id)
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `thumbnail-${id}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      // Update download count
      setGenerations(prev => prev.map(g => 
        g.id === id ? { ...g, download_count: g.download_count + 1 } : g
      ))
    } catch (error) {
      toast.error('Download failed. Please try again.')
    }
  }

  const handleShare = async (id: string) => {
    const generation = generations.find(g => g.id === id)
    if (generation) {
      setSelectedGeneration(generation)
      setShareModalOpen(true)
    }
  }

  const handleRegenerate = async (id: string) => {
    try {
      const generation = generations.find(g => g.id === id)
      if (!generation) return

      const response = await apiClient.createGeneration({ prompt: generation.prompt })
      toast.success('Regeneration started! Check your chat for progress.')
      
      // Redirect to chat
      window.location.href = '/chat'
    } catch (error) {
      toast.error('Failed to start regeneration')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this thumbnail?')) return

    try {
      await apiClient.deleteGeneration(id)
      setGenerations(prev => prev.filter(g => g.id !== id))
      toast.success('Thumbnail deleted successfully')
    } catch (error) {
      toast.error('Failed to delete thumbnail')
    }
  }

  const handlePreview = (generation: Generation) => {
    setSelectedGeneration(generation)
    setShareModalOpen(true)
  }

  const stats = {
    total: generations.length,
    completed: generations.filter(g => g.status === 'completed').length,
    favorites: generations.filter(g => g.is_favorite).length,
    avgProcessingTime: generations
      .filter(g => g.processing_time)
      .reduce((acc, g) => acc + (g.processing_time || 0), 0) / 
      generations.filter(g => g.processing_time).length || 0
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-main">
        {/* Animated gradient orbs */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute w-96 h-96 bg-purple-300/20 rounded-full blur-3xl"
            animate={{
              x: [0, 100, 0],
              y: [0, -100, 0],
            }}
            transition={{ duration: 20, repeat: Infinity }}
            style={{ top: '10%', left: '20%' }}
          />
          <motion.div
            className="absolute w-96 h-96 bg-blue-300/20 rounded-full blur-3xl"
            animate={{
              x: [0, -100, 0],
              y: [0, 100, 0],
            }}
            transition={{ duration: 25, repeat: Infinity }}
            style={{ bottom: '10%', right: '20%' }}
          />
        </div>

        <div className="container max-w-7xl mx-auto px-4 py-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-purple flex items-center justify-center">
                <History className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-text-primary">
                  Your Gallery
                </h1>
                <p className="text-text-secondary">
                  Manage and share your AI-generated thumbnails
                </p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <GlassCard className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
                    <History className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-text-primary">
                      {stats.total}
                    </p>
                    <p className="text-sm text-text-secondary">Total Created</p>
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-text-primary">
                      {stats.completed}
                    </p>
                    <p className="text-sm text-text-secondary">Completed</p>
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                    <History className="w-5 h-5 text-red-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-text-primary">
                      {stats.favorites}
                    </p>
                    <p className="text-sm text-text-secondary">Favorites</p>
                  </div>
                </div>
              </GlassCard>

              <GlassCard className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-purple-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-text-primary">
                      {stats.avgProcessingTime.toFixed(1)}s
                    </p>
                    <p className="text-sm text-text-secondary">Avg Time</p>
                  </div>
                </div>
              </GlassCard>
            </div>
          </motion.div>

          {/* Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <FilterBar
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              statusFilter={statusFilter}
              onStatusFilterChange={setStatusFilter}
              dateRange={dateRange}
              onDateRangeChange={setDateRange}
              showFavorites={showFavorites}
              onShowFavoritesChange={setShowFavorites}
              viewMode={viewMode}
              onViewModeChange={setViewMode}
              sortBy={sortBy}
              onSortByChange={setSortBy}
              totalCount={stats.total}
            />
          </motion.div>

          {/* Gallery */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <GalleryGrid
              generations={generations}
              loading={loading}
              hasMore={hasMore}
              onLoadMore={handleLoadMore}
              onFavorite={handleFavorite}
              onDownload={handleDownload}
              onShare={handleShare}
              onRegenerate={handleRegenerate}
              onDelete={handleDelete}
              onPreview={handlePreview}
              viewMode={viewMode}
            />
          </motion.div>
        </div>

        {/* Share Modal */}
        <ShareModal
          generation={selectedGeneration}
          isOpen={shareModalOpen}
          onClose={() => {
            setShareModalOpen(false)
            setSelectedGeneration(null)
          }}
          onDownload={handleDownload}
        />
      </div>
    </ProtectedRoute>
  )
}