import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { KnowledgeBaseEntry, SearchResponse } from '../types';

export const KnowledgeBasePage: React.FC = () => {
  const [entries, setEntries] = useState<KnowledgeBaseEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    try {
      const data = await apiService.getKnowledgeBaseEntries();
      setEntries(data);
      
      // Extract unique categories
      const uniqueCategories = [...new Set(data.map(entry => entry.category).filter(Boolean))] as string[];
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Error loading entries:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const results = await apiService.searchKnowledgeBase(searchQuery);
      setSearchResults(results);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults(null);
  };

  const displayEntries = searchResults ? searchResults.matches : entries;

  return (
    <div className="arena-container min-h-screen">
      <div className="max-w-6xl mx-auto p-6">
        <div className="arena-card rounded-xl p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-arena-text mb-4 glow-text">
              Knowledge Base
            </h1>
            <p className="text-arena-text-muted">
              Browse and search through our curated RFP knowledge base
            </p>
          </div>

          {/* Search */}
          <div className="mb-8">
            <div className="flex space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search knowledge base..."
                  className="arena-input w-full p-4 rounded-lg"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
                className="arena-button px-6 py-4 rounded-lg font-medium disabled:opacity-50"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
              {searchResults && (
                <button
                  onClick={clearSearch}
                  className="bg-arena-light-gray hover:bg-arena-border text-arena-text px-6 py-4 rounded-lg font-medium transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Category Filter */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === ''
                    ? 'arena-button text-arena-dark'
                    : 'bg-arena-light-gray text-arena-text-muted hover:text-arena-text'
                }`}
              >
                All Categories
              </button>
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'arena-button text-arena-dark'
                      : 'bg-arena-light-gray text-arena-text-muted hover:text-arena-text'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* Results Summary */}
          {searchResults && (
            <div className="mb-6 p-4 bg-arena-accent/10 border border-arena-accent/30 rounded-lg">
              <p className="text-arena-accent">
                Found {searchResults.total_matches} matches for "{searchResults.query}"
              </p>
            </div>
          )}

          {/* Entries List */}
          <div className="space-y-4">
          {(displayEntries as KnowledgeBaseEntry[])
            .filter((entry: KnowledgeBaseEntry) => !selectedCategory || entry.category === selectedCategory)
            .map((entry: KnowledgeBaseEntry) => (
                <div key={entry.id} className="arena-card p-6 rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-medium text-arena-text flex-1">
                      {entry.question}
                    </h3>
                    {entry.category && (
                      <span className="ml-4 bg-arena-accent/20 text-arena-accent px-3 py-1 rounded-full text-sm">
                        {entry.category}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-arena-text-muted mb-4 leading-relaxed">
                    {entry.answer}
                  </p>
                  
                  {entry.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {entry.tags.map((tag: string) => (
                        <span
                          key={tag}
                          className="bg-arena-light-gray/50 text-arena-text-muted px-2 py-1 rounded text-sm"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <div className="mt-4 pt-4 border-t border-arena-border text-xs text-arena-text-muted">
                    <div className="flex justify-between">
                      <span>Created: {new Date(entry.created_at).toLocaleDateString()}</span>
                      <span>Modified: {new Date(entry.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              ))}
          </div>

          {displayEntries.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-arena-text-muted/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-arena-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-arena-text-muted">
                {searchResults ? 'No results found for your search.' : 'No knowledge base entries found.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
