import axios from 'axios';
import { 
  KnowledgeBaseEntry, 
  ProcessingResult, 
  SearchResponse, 
  KnowledgeBaseStats,
  QuestionSubmission 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear it and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Knowledge Base Management
  async getKnowledgeBaseEntries(category?: string, tags?: string): Promise<KnowledgeBaseEntry[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (tags) params.append('tags', tags);
    
    const response = await api.get(`/api/v1/knowledge/entries?${params.toString()}`);
    return response.data;
  },

  async addKnowledgeBaseEntry(entry: Omit<KnowledgeBaseEntry, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'last_modified_by'>): Promise<KnowledgeBaseEntry> {
    const response = await api.post('/api/v1/knowledge/entries', entry);
    return response.data;
  },

  async updateKnowledgeBaseEntry(id: string, update: Partial<KnowledgeBaseEntry>): Promise<KnowledgeBaseEntry> {
    const response = await api.put(`/api/v1/knowledge/entries/${id}`, update);
    return response.data;
  },

  async deleteKnowledgeBaseEntry(id: string): Promise<void> {
    await api.delete(`/api/v1/knowledge/entries/${id}`);
  },

  async searchKnowledgeBase(query: string, minConfidence: number = 0.1, limit: number = 10): Promise<SearchResponse> {
    const response = await api.get('/api/v1/knowledge/search', {
      params: { query, min_confidence: minConfidence, limit }
    });
    return response.data;
  },

  async getKnowledgeBaseStats(): Promise<KnowledgeBaseStats> {
    const response = await api.get('/api/v1/knowledge/stats');
    return response.data;
  },

  async uploadDocument(file: File, category?: string, tags?: string): Promise<{
    message: string;
    filename: string;
    extracted_questions: number;
    added_entries: number;
    skipped_entries: number;
    added_questions: string[];
    skipped_questions: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    if (category) formData.append('category', category);
    if (tags) formData.append('tags', tags);
    
    const response = await api.post('/api/v1/knowledge/upload-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Question Processing
  async processTextQuestions(text: string): Promise<ProcessingResult> {
    const response = await api.post('/api/v1/questions/process-text', { text });
    return response.data;
  },

  async processPDFQuestions(file: File): Promise<ProcessingResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/v1/questions/process-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getRecentSubmissions(limit: number = 10): Promise<QuestionSubmission[]> {
    const response = await api.get('/api/v1/questions/submissions', {
      params: { limit }
    });
    return response.data;
  },

  // Export functionality
  async exportToPDF(submissionId: string, customFilename?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (customFilename) params.append('custom_filename', customFilename);
    
    const response = await api.post(`/api/v1/export/pdf?submission_id=${submissionId}&${params.toString()}`, {}, {
      responseType: 'blob',
    });
    return response.data;
  },

  async exportToDOCX(submissionId: string, customFilename?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (customFilename) params.append('custom_filename', customFilename);
    
    const response = await api.post(`/api/v1/export/docx?submission_id=${submissionId}&${params.toString()}`, {}, {
      responseType: 'blob',
    });
    return response.data;
  },

  async exportToPDFDirect(results: ProcessingResult, customFilename?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (customFilename) params.append('custom_filename', customFilename);
    
    const response = await api.post(`/api/v1/export/pdf/direct?${params.toString()}`, results, {
      responseType: 'blob',
    });
    return response.data;
  },

  async exportToDOCXDirect(results: ProcessingResult, customFilename?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (customFilename) params.append('custom_filename', customFilename);
    
    const response = await api.post(`/api/v1/export/docx/direct?${params.toString()}`, results, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await api.get('/health');
    return response.data;
  }
};
