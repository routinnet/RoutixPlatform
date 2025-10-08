'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ThumbnailCard } from './ThumbnailCard'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Loader2, Grid, List, ImageIcon } from 'lucide-react'

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

interface GalleryGridProps {
  generations: Generation[]
  loading: boolean
  hasMore: boolean
  onLoadMore: () => void
  onFavorite: (id: string) => void
  onDownload: (id: string) => void
  onShare: (id: string) => void
  onRegenerate: (id: string) => void
  onDelete: (id: string) => void
  onPreview: (generation: Generation) => void
  viewMode?: 'grid' | 'masonry' | 'list'
}

export function GalleryGrid({
  generations,
  loading,
  hasMore,
  onLoadMore,
  onFavorite,
  onDownload,
  onShare,
  onRegenerate,
  onDelete,
  onPreview,
  viewMode = 'grid'
}: GalleryGridProps) {
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [isSelectionMode, setIsSelectionMode] = useState(false)
  const loadMoreRef = useRef<HTMLDivElement>(null)

  // Intersection Observer for infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          onLoadMore()
        }
      },
      { threshold: 0.1 }
    )

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current)
    }

    return () => observer.disconnect()
  }, [hasMore, loading, onLoadMore])

  const toggleSelection = (id: string) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedItems(newSelected)
  }

  const selectAll = () => {
    setSelectedItems(new Set(generations.map(g => g.id)))
  }

  const clearSelection = () => {
    setSelectedItems(new Set())
    setIsSelectionMode(false)
  }

  const handleBulkDownload = async () => {
    const selectedGenerations = generations.filter(g => selectedItems.has(g.id))
    for (const generation of selectedGenerations) {
      await onDownload(generation.id)
    }
    clearSelection()
  }

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedItems.size} selected items?`)) return
    
    const selectedIds = Array.from(selectedItems)
    for (const id of selectedIds) {
      await onDelete(id)
    }
    clearSelection()
  }

  const getGridClassName = () => {
    switch (viewMode) {
      case 'masonry':
        return 'columns-1 md:columns-2 lg:columns-3 xl:columns-4 gap-6 space-y-6'
      case 'list':
        return 'space-y-4'
      default:
        return 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
    }
  }

  if (generations.length === 0 && !loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <GlassCard className="p-12 text-center">
          <ImageIcon className="w-16 h-16 text-text-muted mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No thumbnails yet
          </h3>
          <p className="text-text-secondary mb-6">
            Start creating amazing thumbnails with AI
          </p>
          <GradientButton
            onClick={() => window.location.href = '/chat'}
            className="mx-auto"
          >
            Create Your First Thumbnail
          </GradientButton>
        </GlassCard>
      </motion.div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Selection Controls */}
      <AnimatePresence>
        {isSelectionMode && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <GlassCard className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-text-primary font-medium">
                    {selectedItems.size} selected
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={selectAll}
                      className="px-3 py-1 text-sm rounded-lg bg-white/20 hover:bg-white/30 transition-colors text-text-primary"
                    >
                      Select All
                    </button>
                    <button
                      onClick={clearSelection}
                      className="px-3 py-1 text-sm rounded-lg bg-white/20 hover:bg-white/30 transition-colors text-text-primary"
                    >
                      Clear
                    </button>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <GradientButton
                    onClick={handleBulkDownload}
                    disabled={selectedItems.size === 0}
                    className="px-4 py-2"
                  >
                    Download Selected
                  </GradientButton>
                  <button
                    onClick={handleBulkDelete}
                    disabled={selectedItems.size === 0}
                    className="px-4 py-2 rounded-xl bg-red-500/20 hover:bg-red-500/30 transition-colors text-red-600 disabled:opacity-50"
                  >
                    Delete Selected
                  </button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Gallery Grid */}
      <div className={getGridClassName()}>
        <AnimatePresence>
          {generations.map((generation, index) => (
            <motion.div
              key={generation.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ delay: index * 0.05 }}
              className={`relative ${viewMode === 'masonry' ? 'break-inside-avoid mb-6' : ''}`}
            >
              {/* Selection Overlay */}
              {isSelectionMode && (
                <div
                  className="absolute inset-0 z-10 cursor-pointer"
                  onClick={() => toggleSelection(generation.id)}
                >
                  <div className={`
                    absolute inset-0 rounded-2xl border-2 transition-all
                    ${selectedItems.has(generation.id)
                      ? 'border-routix-purple bg-routix-purple/20'
                      : 'border-transparent hover:border-routix-purple/50'
                    }
                  `}>
                    {selectedItems.has(generation.id) && (
                      <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-routix-purple flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <ThumbnailCard
                generation={generation}
                onFavorite={onFavorite}
                onDownload={onDownload}
                onShare={onShare}
                onRegenerate={onRegenerate}
                onDelete={onDelete}
                onPreview={onPreview}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Loading More */}
      {loading && (
        <div className="flex justify-center py-8">
          <GlassCard className="px-6 py-4">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-routix-purple" />
              <span className="text-text-primary">Loading more thumbnails...</span>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Load More Button */}
      {hasMore && !loading && (
        <div ref={loadMoreRef} className="flex justify-center py-8">
          <GradientButton onClick={onLoadMore}>
            Load More Thumbnails
          </GradientButton>
        </div>
      )}

      {/* Selection Mode Toggle */}
      {generations.length > 0 && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsSelectionMode(!isSelectionMode)}
          className="fixed bottom-6 right-6 p-4 rounded-full bg-gradient-purple text-white shadow-button-hover z-50"
        >
          {isSelectionMode ? (
            <Grid className="w-6 h-6" />
          ) : (
            <List className="w-6 h-6" />
          )}
        </motion.button>
      )}
    </div>
  )
}