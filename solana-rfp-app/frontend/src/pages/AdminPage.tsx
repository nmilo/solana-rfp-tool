import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { KnowledgeBaseEntry, KnowledgeBaseStats } from '../types';
import KnowledgeBasePreview from '../components/KnowledgeBasePreview';

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'manage' | 'preview'>('preview');
  const [entries, setEntries] = useState<KnowledgeBaseEntry[]>([]);
  const [stats, setStats] = useState<KnowledgeBaseStats | null>(null);
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [newEntry, setNewEntry] = useState({
    question: '',
    answer: '',
    tags: '',
    category: ''
  });
  const [editingEntry, setEditingEntry] = useState<Partial<KnowledgeBaseEntry>>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [entriesData, statsData] = await Promise.all([
        apiService.getKnowledgeBaseEntries(),
        apiService.getKnowledgeBaseStats()
      ]);
      setEntries(entriesData);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const addEntry = async () => {
    if (!newEntry.question.trim() || !newEntry.answer.trim()) return;
    
    try {
      const tags = newEntry.tags.split(',').map(t => t.trim()).filter(t => t);
      await apiService.addKnowledgeBaseEntry({
        question: newEntry.question,
        answer: newEntry.answer,
        tags,
        category: newEntry.category || undefined
      });
      setNewEntry({ question: '', answer: '', tags: '', category: '' });
      loadData();
    } catch (error) {
      console.error('Error adding entry:', error);
    }
  };

  const updateEntry = async (id: string) => {
    try {
      await apiService.updateKnowledgeBaseEntry(id, editingEntry);
      setIsEditing(null);
      setEditingEntry({});
      loadData();
    } catch (error) {
      console.error('Error updating entry:', error);
    }
  };

  const deleteEntry = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      try {
        await apiService.deleteKnowledgeBaseEntry(id);
        loadData();
      } catch (error) {
        console.error('Error deleting entry:', error);
      }
    }
  };

  const startEditing = (entry: KnowledgeBaseEntry) => {
    setIsEditing(entry.id);
    setEditingEntry({
      question: entry.question,
      answer: entry.answer,
      tags: entry.tags,
      category: entry.category
    });
  };

  const cancelEditing = () => {
    setIsEditing(null);
    setEditingEntry({});
  };

  return (
    <div className="arena-container min-h-screen">
      <div className="max-w-6xl mx-auto p-6">
        <div className="arena-card rounded-xl p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-arena-text mb-4 glow-text">
              Knowledge Base Management
            </h1>
            <p className="text-arena-text-muted">
              Add, edit, and manage knowledge base entries
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="mb-8">
            <div className="border-b border-arena-border">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('preview')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'preview'
                      ? 'border-arena-accent text-arena-accent'
                      : 'border-transparent text-arena-text-muted hover:text-arena-text hover:border-arena-border'
                  }`}
                >
                  Knowledge Base Preview
                </button>
                <button
                  onClick={() => setActiveTab('manage')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'manage'
                      ? 'border-arena-accent text-arena-accent'
                      : 'border-transparent text-arena-text-muted hover:text-arena-text hover:border-arena-border'
                  }`}
                >
                  Manage Entries
                </button>
              </nav>
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'preview' ? (
            <KnowledgeBasePreview />
          ) : (
            <div>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="arena-card p-4 rounded-lg">
                <div className="text-arena-text-muted text-sm">Total Entries</div>
                <div className="text-2xl font-bold text-arena-text">{stats.total_entries}</div>
              </div>
              <div className="arena-card p-4 rounded-lg">
                <div className="text-arena-text-muted text-sm">Categories</div>
                <div className="text-2xl font-bold text-arena-accent">{Object.keys(stats.categories).length}</div>
              </div>
              <div className="arena-card p-4 rounded-lg">
                <div className="text-arena-text-muted text-sm">Top Tags</div>
                <div className="text-2xl font-bold text-arena-success">{Object.keys(stats.top_tags).length}</div>
              </div>
            </div>
          )}

          {/* Add New Entry */}
          <div className="arena-card p-6 rounded-lg mb-8">
            <h2 className="text-xl font-semibold text-arena-text mb-4">Add New Entry</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-arena-text-muted mb-2">
                  Question
                </label>
                <textarea
                  value={newEntry.question}
                  onChange={(e) => setNewEntry({...newEntry, question: e.target.value})}
                  className="arena-textarea w-full p-3 rounded-lg"
                  rows={3}
                  placeholder="Enter the question..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-arena-text-muted mb-2">
                  Answer
                </label>
                <textarea
                  value={newEntry.answer}
                  onChange={(e) => setNewEntry({...newEntry, answer: e.target.value})}
                  className="arena-textarea w-full p-3 rounded-lg"
                  rows={3}
                  placeholder="Enter the answer..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-arena-text-muted mb-2">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={newEntry.tags}
                  onChange={(e) => setNewEntry({...newEntry, tags: e.target.value})}
                  className="arena-input w-full p-3 rounded-lg"
                  placeholder="stablecoin, partnerships, etc."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-arena-text-muted mb-2">
                  Category
                </label>
                <input
                  type="text"
                  value={newEntry.category}
                  onChange={(e) => setNewEntry({...newEntry, category: e.target.value})}
                  className="arena-input w-full p-3 rounded-lg"
                  placeholder="e.g., Technical, Business, Legal"
                />
              </div>
            </div>
            <button
              onClick={addEntry}
              className="mt-4 arena-button px-6 py-3 rounded-lg font-medium"
            >
              Add Entry
            </button>
          </div>

          {/* Entries List */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-arena-text">Knowledge Base Entries ({entries.length})</h2>
            {entries.map((entry) => (
              <div key={entry.id} className="arena-card p-6 rounded-lg">
                {isEditing === entry.id ? (
                  // Edit Mode
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-arena-text-muted mb-2">
                          Question
                        </label>
                        <textarea
                          value={editingEntry.question || ''}
                          onChange={(e) => setEditingEntry({...editingEntry, question: e.target.value})}
                          className="arena-textarea w-full p-3 rounded-lg"
                          rows={2}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-arena-text-muted mb-2">
                          Answer
                        </label>
                        <textarea
                          value={editingEntry.answer || ''}
                          onChange={(e) => setEditingEntry({...editingEntry, answer: e.target.value})}
                          className="arena-textarea w-full p-3 rounded-lg"
                          rows={2}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-arena-text-muted mb-2">
                          Tags
                        </label>
                        <input
                          type="text"
                          value={Array.isArray(editingEntry.tags) ? editingEntry.tags.join(', ') : ''}
                          onChange={(e) => setEditingEntry({...editingEntry, tags: e.target.value.split(',').map(t => t.trim())})}
                          className="arena-input w-full p-3 rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-arena-text-muted mb-2">
                          Category
                        </label>
                        <input
                          type="text"
                          value={editingEntry.category || ''}
                          onChange={(e) => setEditingEntry({...editingEntry, category: e.target.value})}
                          className="arena-input w-full p-3 rounded-lg"
                        />
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => updateEntry(entry.id)}
                        className="arena-button px-4 py-2 rounded-lg font-medium"
                      >
                        Save
                      </button>
                      <button
                        onClick={cancelEditing}
                        className="bg-arena-light-gray hover:bg-arena-border text-arena-text px-4 py-2 rounded-lg font-medium transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-medium text-lg text-arena-text flex-1">
                        {entry.question}
                      </h3>
                      <div className="flex space-x-2 ml-4">
                        <button
                          onClick={() => startEditing(entry)}
                          className="text-arena-accent hover:text-arena-accent-dark text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => deleteEntry(entry.id)}
                          className="text-arena-error hover:text-red-400 text-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                    <p className="text-arena-text-muted mb-3">{entry.answer}</p>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {entry.tags.map((tag) => (
                        <span key={tag} className="bg-arena-light-gray/50 text-arena-text-muted px-2 py-1 rounded text-sm">
                          {tag}
                        </span>
                      ))}
                      {entry.category && (
                        <span className="bg-arena-accent/20 text-arena-accent px-2 py-1 rounded text-sm">
                          {entry.category}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-arena-text-muted">
                      Created: {new Date(entry.created_at).toLocaleDateString()} | 
                      Modified: {new Date(entry.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
