'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { 
  Download, 
  Share, 
  Heart, 
  MoreVertical, 
  Eye, 
  RefreshCw, 
  Trash2,
  Calendar,
  Clock
} from 'lucide-react'
import { toast } from 'sonner'

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

interface ThumbnailCardProps {
  generation: Generation
  onFavorite: (id: string) => void
  onDownload: (id: string) => void
  onShare: (id: string) => void
  onRegenerate: (id: string) => void
  onDelete: (id: string) => void
  onPreview: (generation: Generation) => void
}

export function ThumbnailCard({
  generation,
  onFavorite,
  onDownload,
  onShare,
  onRegenerate,
  onDelete,
  onPreview
}: ThumbnailCardProps) {
  const [showActions, setShowActions] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const handleDownload = async () => {
    try {
      await onDownload(generation.id)
      toast.success('Download started!')
    } catch (error) {
      toast.error('Download failed. Please try again.')
    }
  }

  const handleShare = async () => {
    try {
      await onShare(generation.id)
      toast.success('Sharing options opened!')
    } catch (error) {
      toast.error('Share failed. Please try again.')
    }
  }

  const handleFavorite = async () => {
    try {
      await onFavorite(generation.id)
      toast.success(generation.is_favorite ? 'Removed from favorites' : 'Added to favorites')
    } catch (error) {
      toast.error('Failed to update favorite status')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="group relative"
    >
      <GlassCard className="p-4 overflow-hidden">
        {/* Thumbnail Image */}
        <div className="relative aspect-video bg-white/10 rounded-xl mb-4 overflow-hidden">
          {generation.thumbnail_url ? (
            <>
              <img
                src={generation.thumbnail_url}
                alt={generation.prompt}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                loading="lazy"
              />
              
              {/* Overlay Actions */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: isHovered ? 1 : 0 }}
                className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center gap-2"
              >
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => onPreview(generation)}
                  className="p-3 rounded-full bg-white/20 backdrop-blur-xl text-white hover:bg-white/30 transition-colors"
                >
                  <Eye className="w-5 h-5" />
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleDownload}
                  className="p-3 rounded-full bg-white/20 backdrop-blur-xl text-white hover:bg-white/30 transition-colors"
                >
                  <Download className="w-5 h-5" />
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleShare}
                  className="p-3 rounded-full bg-white/20 backdrop-blur-xl text-white hover:bg-white/30 transition-colors"
                >
                  <Share className="w-5 h-5" />
                </motion.button>
              </motion.div>
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center mx-auto mb-2">
                  {generation.status === 'processing' && (
                    <RefreshCw className="w-6 h-6 text-text-muted animate-spin" />
                  )}
                  {generation.status === 'failed' && (
                    <Trash2 className="w-6 h-6 text-red-500" />
                  )}
                  {generation.status === 'queued' && (
                    <Clock className="w-6 h-6 text-blue-500" />
                  )}
                </div>
                <p className="text-sm text-text-muted">
                  {generation.status === 'processing' && 'Generating...'}
                  {generation.status === 'failed' && 'Generation Failed'}
                  {generation.status === 'queued' && 'In Queue'}
                </p>
              </div>
            </div>
          )}
          
          {/* Status Badge */}
          <div className="absolute top-3 left-3">
            <StatusBadge status={generation.status} />
          </div>
          
          {/* Favorite Button */}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleFavorite}
            className={`absolute top-3 right-3 p-2 rounded-full backdrop-blur-xl transition-colors ${
              generation.is_favorite 
                ? 'bg-red-500/80 text-white' 
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            <Heart className={`w-4 h-4 ${generation.is_favorite ? 'fill-current' : ''}`} />
          </motion.button>
        </div>

        {/* Content */}
        <div className="space-y-3">
          {/* Prompt */}
          <div>
            <p className="text-text-primary font-medium line-clamp-2 text-sm leading-relaxed">
              {generation.prompt}
            </p>
          </div>

          {/* Metadata */}
          <div className="flex items-center justify-between text-xs text-text-muted">
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(generation.created_at)}</span>
            </div>
            {generation.processing_time && (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>{generation.processing_time}s</span>
              </div>
            )}
          </div>

          {/* Stats */}
          <div className="flex items-center justify-between text-xs text-text-muted">
            <span>{generation.download_count} downloads</span>
            <span>{generation.share_count} shares</span>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleDownload}
              disabled={generation.status !== 'completed'}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-gradient-purple text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-button-hover transition-all"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Download</span>
            </motion.button>

            <div className="relative">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setShowActions(!showActions)}
                className="p-2 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary"
              >
                <MoreVertical className="w-4 h-4" />
              </motion.button>

              {/* Dropdown Menu */}
              {showActions && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: -10 }}
                  className="absolute right-0 top-full mt-2 w-48 z-50"
                >
                  <GlassCard className="p-2">
                    <button
                      onClick={() => {
                        handleShare()
                        setShowActions(false)
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/20 transition-colors text-text-primary"
                    >
                      <Share className="w-4 h-4" />
                      <span className="text-sm">Share</span>
                    </button>
                    
                    <button
                      onClick={() => {
                        onRegenerate(generation.id)
                        setShowActions(false)
                      }}
                      disabled={generation.status === 'processing'}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/20 transition-colors text-text-primary disabled:opacity-50"
                    >
                      <RefreshCw className="w-4 h-4" />
                      <span className="text-sm">Regenerate</span>
                    </button>
                    
                    <button
                      onClick={() => {
                        onDelete(generation.id)
                        setShowActions(false)
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/20 transition-colors text-red-600"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span className="text-sm">Delete</span>
                    </button>
                  </GlassCard>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Click outside to close dropdown */}
      {showActions && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowActions(false)}
        />
      )}
    </motion.div>
  )
}