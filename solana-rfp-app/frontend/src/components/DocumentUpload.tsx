import React, { useState, useRef } from 'react';
import { apiService } from '../services/api';

interface DocumentUploadProps {
  onUploadSuccess: () => void;
}

interface UploadResult {
  message: string;
  filename: string;
  extracted_questions: number;
  added_entries: number;
  skipped_entries: number;
  added_questions: string[];
  skipped_questions: string[];
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }
    
    setError(null);
    setUploadResult(null);
    uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setError(null);
    
    try {
      const result = await apiService.uploadDocument(
        file, 
        category || undefined, 
        tags || undefined
      );
      setUploadResult(result);
      onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const resetForm = () => {
    setUploadResult(null);
    setError(null);
    setCategory('');
    setTags('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="arena-card p-6 rounded-lg mb-6">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-arena-text mb-2">
          Upload Document to Knowledge Base
        </h3>
        <p className="text-arena-text-muted">
          Upload a PDF document to automatically extract questions and add them to the knowledge base.
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-arena-accent bg-arena-accent/10'
            : 'border-arena-border hover:border-arena-accent/50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="mb-4">
          <svg
            className="w-12 h-12 text-arena-text-muted mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-arena-text-muted mb-2">
            Drag and drop a PDF file here, or click to select
          </p>
          <p className="text-sm text-arena-text-muted">
            Only PDF files are supported
          </p>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileInputChange}
          className="hidden"
        />
        
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="arena-button px-6 py-3 rounded-lg font-medium disabled:opacity-50"
        >
          {isUploading ? 'Uploading...' : 'Select PDF File'}
        </button>
      </div>

      {/* Category and Tags */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <div>
          <label className="block text-sm font-medium text-arena-text mb-2">
            Category (optional)
          </label>
          <input
            type="text"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g., Technical Requirements"
            className="arena-input w-full p-3 rounded-lg"
            disabled={isUploading}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-arena-text mb-2">
            Tags (optional)
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g., blockchain, security, compliance"
            className="arena-input w-full p-3 rounded-lg"
            disabled={isUploading}
          />
          <p className="text-xs text-arena-text-muted mt-1">
            Separate multiple tags with commas
          </p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <div className="mt-6 p-4 bg-arena-accent/10 border border-arena-accent/30 rounded-lg">
          <div className="flex justify-between items-start mb-4">
            <h4 className="text-lg font-medium text-arena-accent">
              Upload Successful!
            </h4>
            <button
              onClick={resetForm}
              className="text-arena-text-muted hover:text-arena-text transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">File:</span>
              <span className="text-arena-text">{uploadResult.filename}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">Questions extracted:</span>
              <span className="text-arena-text">{uploadResult.extracted_questions}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">Added to knowledge base:</span>
              <span className="text-green-400">{uploadResult.added_entries}</span>
            </div>
            
            {uploadResult.skipped_entries > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-arena-text-muted">Skipped (duplicates):</span>
                <span className="text-yellow-400">{uploadResult.skipped_entries}</span>
              </div>
            )}
          </div>

          {uploadResult.added_questions.length > 0 && (
            <div className="mt-4">
              <h5 className="text-sm font-medium text-arena-text mb-2">
                Added Questions:
              </h5>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {uploadResult.added_questions.map((question, index) => (
                  <div key={index} className="text-xs text-arena-text-muted bg-arena-light-gray/30 p-2 rounded">
                    {question}
                  </div>
                ))}
              </div>
            </div>
          )}

          {uploadResult.skipped_questions.length > 0 && (
            <div className="mt-4">
              <h5 className="text-sm font-medium text-arena-text mb-2">
                Skipped Questions (already exist):
              </h5>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {uploadResult.skipped_questions.map((question, index) => (
                  <div key={index} className="text-xs text-yellow-400 bg-yellow-400/10 p-2 rounded">
                    {question}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
