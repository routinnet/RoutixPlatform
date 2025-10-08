'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { 
  X, 
  Download, 
  Link, 
  Twitter, 
  Instagram, 
  Linkedin,
  Facebook,
  Copy,
  Check,
  Mail,
  MessageCircle
} from 'lucide-react'
import { toast } from 'sonner'

interface Generation {
  id: string
  prompt: string
  thumbnail_url?: string
  created_at: string
}

interface ShareModalProps {
  generation: Generation | null
  isOpen: boolean
  onClose: () => void
  onDownload: (id: string, format: string) => void
}

export function ShareModal({ generation, isOpen, onClose, onDownload }: ShareModalProps) {
  const [copied, setCopied] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState('png')

  if (!generation || !isOpen) return null

  const shareUrl = `${window.location.origin}/gallery/${generation.id}`
  const shareText = `Check out this amazing thumbnail I created with Routix AI: "${generation.prompt}"`

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl)
      setCopied(true)
      toast.success('Link copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast.error('Failed to copy link')
    }
  }

  const handleSocialShare = (platform: string) => {
    const encodedText = encodeURIComponent(shareText)
    const encodedUrl = encodeURIComponent(shareUrl)
    
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      instagram: `https://www.instagram.com/`, // Instagram doesn't support direct URL sharing
      email: `mailto:?subject=Amazing AI Thumbnail&body=${encodedText}%0A%0A${encodedUrl}`,
      whatsapp: `https://wa.me/?text=${encodedText}%20${encodedUrl}`
    }

    if (platform === 'instagram') {
      toast.info('Instagram sharing: Save the image and share it manually on Instagram')
      return
    }

    window.open(urls[platform as keyof typeof urls], '_blank', 'width=600,height=400')
  }

  const handleDownload = () => {
    onDownload(generation.id, selectedFormat)
    toast.success(`Downloading ${selectedFormat.toUpperCase()} format...`)
  }

  const socialPlatforms = [
    { 
      name: 'Twitter', 
      icon: Twitter, 
      color: 'hover:bg-blue-500/20 hover:text-blue-500',
      key: 'twitter'
    },
    { 
      name: 'Facebook', 
      icon: Facebook, 
      color: 'hover:bg-blue-600/20 hover:text-blue-600',
      key: 'facebook'
    },
    { 
      name: 'LinkedIn', 
      icon: Linkedin, 
      color: 'hover:bg-blue-700/20 hover:text-blue-700',
      key: 'linkedin'
    },
    { 
      name: 'Instagram', 
      icon: Instagram, 
      color: 'hover:bg-pink-500/20 hover:text-pink-500',
      key: 'instagram'
    },
    { 
      name: 'Email', 
      icon: Mail, 
      color: 'hover:bg-gray-500/20 hover:text-gray-600',
      key: 'email'
    },
    { 
      name: 'WhatsApp', 
      icon: MessageCircle, 
      color: 'hover:bg-green-500/20 hover:text-green-500',
      key: 'whatsapp'
    }
  ]

  const downloadFormats = [
    { value: 'png', label: 'PNG (Best Quality)', description: 'Lossless, transparent background support' },
    { value: 'jpg', label: 'JPG (Smaller Size)', description: 'Compressed, smaller file size' },
    { value: 'webp', label: 'WebP (Modern)', description: 'Modern format, great compression' }
  ]

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
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            >
              <GlassCard className="p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-text-primary">
                    Share & Download
                  </h2>
                  <button
                    onClick={onClose}
                    className="p-2 rounded-xl hover:bg-white/20 transition-colors text-text-muted hover:text-text-primary"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Preview */}
                <div className="mb-6">
                  <div className="aspect-video bg-white/10 rounded-xl overflow-hidden mb-3">
                    {generation.thumbnail_url && (
                      <img
                        src={generation.thumbnail_url}
                        alt={generation.prompt}
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <p className="text-text-secondary text-sm line-clamp-2">
                    {generation.prompt}
                  </p>
                </div>

                {/* Copy Link */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-3">
                    Share Link
                  </h3>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={shareUrl}
                      readOnly
                      className="flex-1 px-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary bg-white/20 backdrop-blur-xl"
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={copyToClipboard}
                      className={`px-4 py-3 rounded-xl transition-all flex items-center gap-2 ${
                        copied 
                          ? 'bg-green-500/20 text-green-600' 
                          : 'bg-white/20 hover:bg-white/30 text-text-primary'
                      }`}
                    >
                      {copied ? (
                        <>
                          <Check className="w-5 h-5" />
                          <span className="hidden sm:inline">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-5 h-5" />
                          <span className="hidden sm:inline">Copy</span>
                        </>
                      )}
                    </motion.button>
                  </div>
                </div>

                {/* Social Sharing */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-3">
                    Share on Social Media
                  </h3>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                    {socialPlatforms.map((platform) => (
                      <motion.button
                        key={platform.key}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleSocialShare(platform.key)}
                        className={`p-4 rounded-xl bg-white/20 transition-all text-text-primary ${platform.color} flex flex-col items-center gap-2`}
                      >
                        <platform.icon className="w-6 h-6" />
                        <span className="text-xs font-medium">{platform.name}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Download Options */}
                <div>
                  <h3 className="text-lg font-semibold text-text-primary mb-3">
                    Download Options
                  </h3>
                  
                  {/* Format Selection */}
                  <div className="space-y-3 mb-4">
                    {downloadFormats.map((format) => (
                      <motion.label
                        key={format.value}
                        whileHover={{ scale: 1.01 }}
                        className={`flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all ${
                          selectedFormat === format.value
                            ? 'bg-routix-purple/20 border border-routix-purple/30'
                            : 'bg-white/10 hover:bg-white/20'
                        }`}
                      >
                        <input
                          type="radio"
                          name="format"
                          value={format.value}
                          checked={selectedFormat === format.value}
                          onChange={(e) => setSelectedFormat(e.target.value)}
                          className="w-4 h-4 text-routix-purple"
                        />
                        <div className="flex-1">
                          <div className="font-medium text-text-primary">
                            {format.label}
                          </div>
                          <div className="text-sm text-text-secondary">
                            {format.description}
                          </div>
                        </div>
                      </motion.label>
                    ))}
                  </div>

                  {/* Download Button */}
                  <GradientButton
                    onClick={handleDownload}
                    className="w-full flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    <span>Download {selectedFormat.toUpperCase()}</span>
                  </GradientButton>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}