'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Upload, X, FileImage, AlertCircle, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

interface UploadedFile extends File {
  preview?: string
  id: string
  status: 'uploading' | 'success' | 'error'
  progress: number
}

interface UploadZoneProps {
  onUpload: (files: File[]) => Promise<void>
  maxFiles?: number
  acceptedTypes?: string[]
  maxSize?: number
}

export function UploadZone({ 
  onUpload, 
  maxFiles = 10, 
  acceptedTypes = ['image/*'],
  maxSize = 10 * 1024 * 1024 // 10MB
}: UploadZoneProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [uploading, setUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach((error: any) => {
        if (error.code === 'file-too-large') {
          toast.error(`${file.name} is too large. Max size is ${maxSize / 1024 / 1024}MB`)
        } else if (error.code === 'file-invalid-type') {
          toast.error(`${file.name} is not a supported file type`)
        } else {
          toast.error(`Error with ${file.name}: ${error.message}`)
        }
      })
    })

    // Handle accepted files
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      ...file,
      id: Math.random().toString(36).substr(2, 9),
      preview: URL.createObjectURL(file),
      status: 'uploading' as const,
      progress: 0
    }))

    setFiles(prev => [...prev, ...newFiles])

    // Simulate upload progress
    newFiles.forEach(file => {
      const interval = setInterval(() => {
        setFiles(prev => prev.map(f => 
          f.id === file.id 
            ? { ...f, progress: Math.min(f.progress + 10, 100) }
            : f
        ))
      }, 200)

      setTimeout(() => {
        clearInterval(interval)
        setFiles(prev => prev.map(f => 
          f.id === file.id 
            ? { ...f, status: 'success' as const, progress: 100 }
            : f
        ))
      }, 2000)
    })
  }, [maxSize])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    maxFiles,
    multiple: maxFiles > 1
  })

  const removeFile = (fileId: string) => {
    setFiles(prev => {
      const file = prev.find(f => f.id === fileId)
      if (file?.preview) {
        URL.revokeObjectURL(file.preview)
      }
      return prev.filter(f => f.id !== fileId)
    })
  }

  const handleUpload = async () => {
    const successFiles = files.filter(f => f.status === 'success')
    if (successFiles.length === 0) {
      toast.error('No files ready for upload')
      return
    }

    setUploading(true)
    try {
      await onUpload(successFiles)
      setFiles([])
      toast.success(`Successfully uploaded ${successFiles.length} file(s)`)
    } catch (error) {
      toast.error('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Drop Zone */}
      <motion.div
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        {...getRootProps()}
        className={`
          relative cursor-pointer transition-all duration-300
          ${isDragActive ? 'scale-105' : ''}
        `}
      >
        <input {...getInputProps()} />
        <GlassCard className={`
          p-12 text-center border-2 border-dashed transition-all
          ${isDragActive 
            ? 'border-routix-purple bg-routix-purple/10' 
            : 'border-white/30 hover:border-routix-purple/50'
          }
        `}>
          <motion.div
            animate={{ y: isDragActive ? -10 : 0 }}
            className="space-y-4"
          >
            <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-purple flex items-center justify-center">
              <Upload className="w-8 h-8 text-white" />
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-text-primary mb-2">
                {isDragActive ? 'Drop files here' : 'Upload Templates'}
              </h3>
              <p className="text-text-secondary">
                Drag and drop your template files here, or click to browse
              </p>
              <p className="text-sm text-text-muted mt-2">
                Supports: {acceptedTypes.join(', ')} • Max {maxSize / 1024 / 1024}MB per file
              </p>
            </div>
          </motion.div>
        </GlassCard>
      </motion.div>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-text-primary">
                  Uploaded Files ({files.length})
                </h4>
                <GradientButton
                  onClick={handleUpload}
                  loading={uploading}
                  disabled={files.every(f => f.status !== 'success')}
                  className="px-4 py-2"
                >
                  Upload All
                </GradientButton>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {files.map((file) => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="relative"
                  >
                    <GlassCard className="p-4">
                      {/* Preview */}
                      <div className="aspect-video bg-white/10 rounded-xl mb-3 overflow-hidden">
                        {file.preview ? (
                          <img
                            src={file.preview}
                            alt={file.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <FileImage className="w-8 h-8 text-text-muted" />
                          </div>
                        )}
                      </div>

                      {/* File Info */}
                      <div className="space-y-2">
                        <p className="font-medium text-text-primary truncate" title={file.name}>
                          {file.name}
                        </p>
                        <p className="text-sm text-text-muted">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>

                        {/* Progress */}
                        {file.status === 'uploading' && (
                          <div className="space-y-1">
                            <div className="w-full bg-white/20 rounded-full h-2">
                              <motion.div
                                className="h-2 bg-gradient-purple rounded-full"
                                initial={{ width: 0 }}
                                animate={{ width: `${file.progress}%` }}
                                transition={{ duration: 0.3 }}
                              />
                            </div>
                            <p className="text-xs text-text-muted">{file.progress}%</p>
                          </div>
                        )}

                        {/* Status */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {file.status === 'success' && (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            )}
                            {file.status === 'error' && (
                              <AlertCircle className="w-4 h-4 text-red-500" />
                            )}
                            <span className={`text-xs font-medium ${
                              file.status === 'success' ? 'text-green-600' :
                              file.status === 'error' ? 'text-red-600' :
                              'text-text-muted'
                            }`}>
                              {file.status === 'uploading' ? 'Processing...' :
                               file.status === 'success' ? 'Ready' :
                               'Failed'}
                            </span>
                          </div>

                          <button
                            onClick={() => removeFile(file.id)}
                            className="p-1 rounded-lg hover:bg-white/20 transition-colors"
                          >
                            <X className="w-4 h-4 text-text-muted" />
                          </button>
                        </div>
                      </div>
                    </GlassCard>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}