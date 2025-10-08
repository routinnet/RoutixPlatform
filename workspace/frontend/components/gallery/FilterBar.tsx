'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { 
  Search, 
  Filter, 
  Calendar, 
  Grid, 
  List, 
  Grid3X3,
  Heart,
  CheckCircle,
  Clock,
  AlertCircle,
  X
} from 'lucide-react'

interface FilterBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  statusFilter: string
  onStatusFilterChange: (status: string) => void
  dateRange: { start?: string; end?: string }
  onDateRangeChange: (range: { start?: string; end?: string }) => void
  showFavorites: boolean
  onShowFavoritesChange: (show: boolean) => void
  viewMode: 'grid' | 'masonry' | 'list'
  onViewModeChange: (mode: 'grid' | 'masonry' | 'list') => void
  sortBy: string
  onSortByChange: (sort: string) => void
  totalCount: number
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  dateRange,
  onDateRangeChange,
  showFavorites,
  onShowFavoritesChange,
  viewMode,
  onViewModeChange,
  sortBy,
  onSortByChange,
  totalCount
}: FilterBarProps) {
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)

  const statusOptions = [
    { value: 'all', label: 'All Status', icon: null },
    { value: 'completed', label: 'Completed', icon: CheckCircle, color: 'text-green-500' },
    { value: 'processing', label: 'Processing', icon: Clock, color: 'text-blue-500' },
    { value: 'queued', label: 'Queued', icon: Clock, color: 'text-yellow-500' },
    { value: 'failed', label: 'Failed', icon: AlertCircle, color: 'text-red-500' },
  ]

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'most_downloaded', label: 'Most Downloaded' },
    { value: 'most_shared', label: 'Most Shared' },
    { value: 'processing_time', label: 'Fastest Generation' },
  ]

  const clearFilters = () => {
    onSearchChange('')
    onStatusFilterChange('all')
    onDateRangeChange({})
    onShowFavoritesChange(false)
    onSortByChange('newest')
  }

  const hasActiveFilters = searchQuery || statusFilter !== 'all' || 
                          dateRange.start || dateRange.end || showFavorites

  return (
    <div className="space-y-4">
      {/* Main Filter Bar */}
      <GlassCard className="p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
          {/* Left Side - Search and Filters */}
          <div className="flex-1 flex flex-col sm:flex-row gap-4 items-center w-full lg:w-auto">
            {/* Search */}
            <div className="relative flex-1 max-w-md w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
              <input
                type="text"
                placeholder="Search your thumbnails..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary placeholder:text-text-muted bg-white/20 backdrop-blur-xl"
              />
              {searchQuery && (
                <button
                  onClick={() => onSearchChange('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-lg hover:bg-white/20 transition-colors"
                >
                  <X className="w-4 h-4 text-text-muted" />
                </button>
              )}
            </div>

            {/* Quick Filters */}
            <div className="flex items-center gap-2">
              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => onStatusFilterChange(e.target.value)}
                className="px-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary bg-white/20 backdrop-blur-xl"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              {/* Favorites Toggle */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onShowFavoritesChange(!showFavorites)}
                className={`p-3 rounded-xl transition-all ${
                  showFavorites
                    ? 'bg-red-500/20 text-red-600 border border-red-500/30'
                    : 'bg-white/20 text-text-muted hover:text-text-primary'
                }`}
              >
                <Heart className={`w-5 h-5 ${showFavorites ? 'fill-current' : ''}`} />
              </motion.button>

              {/* Advanced Filters Toggle */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className={`p-3 rounded-xl transition-all ${
                  showAdvancedFilters
                    ? 'bg-routix-purple/20 text-routix-purple'
                    : 'bg-white/20 text-text-muted hover:text-text-primary'
                }`}
              >
                <Filter className="w-5 h-5" />
              </motion.button>
            </div>
          </div>

          {/* Right Side - View Controls */}
          <div className="flex items-center gap-4">
            {/* Results Count */}
            <span className="text-sm text-text-secondary whitespace-nowrap">
              {totalCount.toLocaleString()} thumbnails
            </span>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => onSortByChange(e.target.value)}
              className="px-4 py-3 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary bg-white/20 backdrop-blur-xl"
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            {/* View Mode */}
            <div className="flex items-center gap-1 p-1 rounded-xl bg-white/20">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onViewModeChange('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-routix-purple text-white' 
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                <Grid className="w-4 h-4" />
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onViewModeChange('masonry')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'masonry' 
                    ? 'bg-routix-purple text-white' 
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                <Grid3X3 className="w-4 h-4" />
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onViewModeChange('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-routix-purple text-white' 
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                <List className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>

        {/* Active Filters */}
        {hasActiveFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-4 pt-4 border-t border-white/20"
          >
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm text-text-secondary">Active filters:</span>
              
              {searchQuery && (
                <span className="px-3 py-1 text-sm rounded-lg bg-routix-purple/20 text-routix-purple flex items-center gap-2">
                  Search: "{searchQuery}"
                  <button onClick={() => onSearchChange('')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )}
              
              {statusFilter !== 'all' && (
                <span className="px-3 py-1 text-sm rounded-lg bg-routix-purple/20 text-routix-purple flex items-center gap-2">
                  Status: {statusOptions.find(s => s.value === statusFilter)?.label}
                  <button onClick={() => onStatusFilterChange('all')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )}
              
              {showFavorites && (
                <span className="px-3 py-1 text-sm rounded-lg bg-red-500/20 text-red-600 flex items-center gap-2">
                  Favorites only
                  <button onClick={() => onShowFavoritesChange(false)}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )}
              
              <button
                onClick={clearFilters}
                className="px-3 py-1 text-sm rounded-lg bg-white/20 hover:bg-white/30 transition-colors text-text-primary"
              >
                Clear all
              </button>
            </div>
          </motion.div>
        )}
      </GlassCard>

      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <GlassCard className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Date Range */}
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Date Range
                </label>
                <div className="flex gap-2">
                  <input
                    type="date"
                    value={dateRange.start || ''}
                    onChange={(e) => onDateRangeChange({ ...dateRange, start: e.target.value })}
                    className="flex-1 px-3 py-2 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary bg-white/20 backdrop-blur-xl"
                  />
                  <span className="text-text-muted self-center">to</span>
                  <input
                    type="date"
                    value={dateRange.end || ''}
                    onChange={(e) => onDateRangeChange({ ...dateRange, end: e.target.value })}
                    className="flex-1 px-3 py-2 rounded-xl glass border-0 focus:ring-2 focus:ring-routix-purple text-text-primary bg-white/20 backdrop-blur-xl"
                  />
                </div>
              </div>

              {/* Quick Date Filters */}
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Quick Filters
                </label>
                <div className="flex gap-2 flex-wrap">
                  {[
                    { label: 'Today', days: 0 },
                    { label: 'This Week', days: 7 },
                    { label: 'This Month', days: 30 },
                    { label: 'This Year', days: 365 },
                  ].map(({ label, days }) => (
                    <button
                      key={label}
                      onClick={() => {
                        const end = new Date().toISOString().split('T')[0]
                        const start = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
                          .toISOString().split('T')[0]
                        onDateRangeChange({ start, end })
                      }}
                      className="px-3 py-2 text-sm rounded-lg bg-white/20 hover:bg-white/30 transition-colors text-text-primary"
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}
    </div>
  )
}