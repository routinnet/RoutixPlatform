'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { 
  X, 
  Download, 
  Share, 
  Heart, 
  RefreshCw,
  Calendar,
  Clock,
  Zap,
  Eye,
  Copy
} from 'lucide-react'

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

interface PreviewModalProps {
  generation: Generation | null
  isOpen: boolean
  onClose: () => void
  onFavorite: (id: string) => void
  onDownload: (id: string) => void
  onShare: (id: string) => void
  onRegenerate: (id: string) => void
}

export function PreviewModal({
  generation,
  isOpen,
  onClose,
  onFavorite,
  onDownload,
  onShare,
  onRegenerate
}: PreviewModalProps) {
  if (!generation || !isOpen) return null

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const copyPrompt = async () => {
    try {
      await navigator.clipboard.writeText(generation.prompt)
    } catch (error) {
      console.error('Failed to copy prompt')
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-4xl max-h-[90vh] overflow-y-auto"
            >
              <GlassCard className="p-0 overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-white/20">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <StatusBadge status={generation.status} />
                      <h2 className="text-xl font-bold text-text-primary">
                        Thumbnail Preview
                      </h2>
                    </div>
                    <button
                      onClick={onClose}
                      className="p-2 rounded-xl hover:bg-white/20 transition-colors text-text-muted hover:text-text-primary"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
                  {/* Image Preview */}
                  <div className="lg:col-span-2">
                    <div className="aspect-video bg-white/10 rounded-2xl overflow-hidden mb-4">
                      {generation.thumbnail_url ? (
                        <img
                          src={generation.thumbnail_url}
                          alt={generation.prompt}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <div className="text-center">
                            <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center mx-auto mb-4">
                              {generation.status === 'processing' && (
                                <RefreshCw className="w-8 h-8 text-text-muted animate-spin" />
                              )}
                              {generation.status === 'failed' && (
                                <X className="w-8 h-8 text-red-500" />
                              )}
                              {generation.status === 'queued' && (
                                <Clock className="w-8 h-8 text-blue-500" />
                              )}
                            </div>
                            <p className="text-text-secondary">
                              {generation.status === 'processing' && 'Generating...'}
                              {generation.status === 'failed' && 'Generation Failed'}
                              {generation.status === 'queued' && 'In Queue'}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onDownload(generation.id)}
                        disabled={generation.status !== 'completed'}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-purple text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-button-hover transition-all"
                      >
                        <Download className="w-5 h-5" />
                        <span>Download</span>
                      </motion.button>

                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onShare(generation.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary"
                      >
                        <Share className="w-5 h-5" />
                        <span>Share</span>
                      </motion.button>

                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => onFavorite(generation.id)}
                        className={`p-3 rounded-xl transition-colors ${
                          generation.is_favorite 
                            ? 'bg-red-500/20 text-red-600' 
                            : 'bg-white/20 hover:bg-white/30 text-text-primary'
                        }`}
                      >
                        <Heart className={`w-5 h-5 ${generation.is_favorite ? 'fill-current' : ''}`} />
                      </motion.button>
                    </div>
                  </div>

                  {/* Details Panel */}
                  <div className="space-y-6">
                    {/* Prompt */}
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold text-text-primary">
                          Prompt
                        </h3>
                        <button
                          onClick={copyPrompt}
                          className="p-2 rounded-lg hover:bg-white/20 transition-colors text-text-muted hover:text-text-primary"
                          title="Copy prompt"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      <GlassCard className="p-4 bg-white/10">
                        <p className="text-text-primary leading-relaxed text-sm">
                          {generation.prompt}
                        </p>
                      </GlassCard>
                    </div>

                    {/* Metadata */}
                    <div>
                      <h3 className="text-lg font-semibold text-text-primary mb-3">
                        Details
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center gap-3 text-sm">
                          <Calendar className="w-4 h-4 text-text-muted" />
                          <span className="text-text-secondary">Created:</span>
                          <span className="text-text-primary font-medium">
                            {formatDate(generation.created_at)}
                          </span>
                        </div>

                        {generation.processing_time && (
                          <div className="flex items-center gap-3 text-sm">
                            <Zap className="w-4 h-4 text-text-muted" />
                            <span className="text-text-secondary">Processing Time:</span>
                            <span className="text-text-primary font-medium">
                              {generation.processing_time}s
                            </span>
                          </div>
                        )}

                        <div className="flex items-center gap-3 text-sm">
                          <Download className="w-4 h-4 text-text-muted" />
                          <span className="text-text-secondary">Downloads:</span>
                          <span className="text-text-primary font-medium">
                            {generation.download_count}
                          </span>
                        </div>

                        <div className="flex items-center gap-3 text-sm">
                          <Share className="w-4 h-4 text-text-muted" />
                          <span className="text-text-secondary">Shares:</span>
                          <span className="text-text-primary font-medium">
                            {generation.share_count}
                          </span>
                        </div>

                        <div className="flex items-center gap-3 text-sm">
                          <Eye className="w-4 h-4 text-text-muted" />
                          <span className="text-text-secondary">Status:</span>
                          <StatusBadge status={generation.status} />
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div>
                      <h3 className="text-lg font-semibold text-text-primary mb-3">
                        Actions
                      </h3>
                      <div className="space-y-2">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => onRegenerate(generation.id)}
                          disabled={generation.status === 'processing'}
                          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/20 hover:bg-white/30 transition-colors text-text-primary disabled:opacity-50"
                        >
                          <RefreshCw className="w-5 h-5" />
                          <span>Regenerate with Same Prompt</span>
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}