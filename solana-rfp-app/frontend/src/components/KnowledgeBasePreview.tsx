import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface KnowledgeBaseEntry {
  id: string;
  question: string;
  answer: string;
  answer_preview: string;
  category: string;
  tags: string[];
  created_at: string;
  created_by: string;
  is_active: boolean;
  confidence_threshold: number;
}

interface PaginationInfo {
  page: number;
  page_size: number;
  total_entries: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface KnowledgeBasePreviewData {
  entries: KnowledgeBaseEntry[];
  pagination: PaginationInfo;
  filters: {
    category?: string;
    search?: string;
  };
}

const KnowledgeBasePreview: React.FC = () => {
  const [data, setData] = useState<KnowledgeBasePreviewData | null>(null);
  const [categories, setCategories] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    loadData();
    loadCategories();
  }, [currentPage, pageSize, selectedCategory, searchTerm]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiService.getKnowledgeBasePreview(
        currentPage,
        pageSize,
        selectedCategory || undefined,
        searchTerm || undefined
      );
      
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load knowledge base');
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const result = await apiService.getKnowledgeBaseCategories();
      setCategories(result.categories);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setCurrentPage(1); // Reset to first page when filtering
  };

  const handleSearchChange = (search: string) => {
    setSearchTerm(search);
    setCurrentPage(1); // Reset to first page when searching
  };

  const clearFilters = () => {
    setSelectedCategory('');
    setSearchTerm('');
    setCurrentPage(1);
  };

  if (loading && !data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <div className="mt-4">
              <button
                onClick={loadData}
                className="bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded text-sm"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Knowledge Base Preview</h2>
          <p className="text-gray-600">
            {data.pagination.total_entries} total entries
          </p>
        </div>
        <button
          onClick={loadData}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="Search questions and answers..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {Object.entries(categories).map(([category, count]) => (
                <option key={category} value={category}>
                  {category} ({count})
                </option>
              ))}
            </select>
          </div>

          {/* Page Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Items per page
            </label>
            <select
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {/* Clear Filters */}
        {(selectedCategory || searchTerm) && (
          <div className="mt-4">
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Entries List */}
      <div className="space-y-4">
        {data.entries.map((entry) => (
          <div key={entry.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900 mb-1">
                  {entry.question}
                </h3>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {entry.category || 'Uncategorized'}
                  </span>
                  <span>Created by: {entry.created_by}</span>
                  <span>{new Date(entry.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {entry.is_active ? (
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                    Active
                  </span>
                ) : (
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
                    Inactive
                  </span>
                )}
              </div>
            </div>
            
            <div className="text-gray-700 mb-3">
              {entry.answer_preview}
            </div>
            
            {entry.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {entry.tags.map((tag) => (
                  <span
                    key={tag}
                    className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {data.pagination.total_pages > 1 && (
        <div className="flex justify-center items-center space-x-2">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={!data.pagination.has_prev}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          
          <span className="text-sm text-gray-600">
            Page {data.pagination.page} of {data.pagination.total_pages}
          </span>
          
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={!data.pagination.has_next}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}

      {loading && (
        <div className="flex justify-center items-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBasePreview;

