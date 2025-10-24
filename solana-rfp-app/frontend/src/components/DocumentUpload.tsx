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

interface MultiUploadResult {
  message: string;
  total_files: number;
  successful_files: number;
  failed_files: number;
  total_extracted_questions: number;
  total_added_entries: number;
  total_skipped_entries: number;
  file_results: Array<{
    filename: string;
    status: 'success' | 'error';
    error?: string;
    extracted_questions: number;
    added_entries: number;
    skipped_entries: number;
    added_questions: string[];
    skipped_questions: string[];
  }>;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [multiUploadResult, setMultiUploadResult] = useState<MultiUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploadMode, setUploadMode] = useState<'single' | 'multiple'>('single');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    const fileExtension = file.name.toLowerCase().split('.').pop();
    const supportedFormats = ['pdf', 'docx', 'doc', 'xlsx', 'xls'];
    
    if (!fileExtension || !supportedFormats.includes(fileExtension)) {
      setError(`Unsupported file format: ${file.name}. Supported formats: PDF, DOCX, DOC, XLSX, XLS`);
      return false;
    }
    return true;
  };

  const handleFileSelect = (file: File) => {
    if (!validateFile(file)) return;
    
    setError(null);
    setUploadResult(null);
    setMultiUploadResult(null);
    
    if (uploadMode === 'single') {
      uploadFile(file);
    } else {
      setSelectedFiles([file]);
    }
  };

  const handleMultipleFileSelect = (files: FileList) => {
    const fileArray = Array.from(files);
    
    // Validate all files
    for (const file of fileArray) {
      if (!validateFile(file)) return;
    }
    
    if (fileArray.length > 10) {
      setError('Maximum 10 files allowed per upload');
      return;
    }
    
    setError(null);
    setUploadResult(null);
    setMultiUploadResult(null);
    setSelectedFiles(fileArray);
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

  const uploadMultipleFiles = async () => {
    if (selectedFiles.length === 0) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      const result = await apiService.uploadMultipleDocuments(
        selectedFiles,
        category || undefined,
        tags || undefined
      );
      setMultiUploadResult(result);
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
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (uploadMode === 'single') {
        handleFileSelect(e.dataTransfer.files[0]);
      } else {
        handleMultipleFileSelect(e.dataTransfer.files);
      }
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      if (uploadMode === 'single') {
        handleFileSelect(e.target.files[0]);
      } else {
        handleMultipleFileSelect(e.target.files);
      }
    }
  };

  const resetForm = () => {
    setUploadResult(null);
    setMultiUploadResult(null);
    setError(null);
    setCategory('');
    setTags('');
    setSelectedFiles([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="arena-card p-6 rounded-lg mb-6">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-arena-text mb-2">
          Upload Document{uploadMode === 'multiple' ? 's' : ''} to Knowledge Base
        </h3>
        <p className="text-arena-text-muted">
          Upload {uploadMode === 'multiple' ? 'multiple documents' : 'a document'} (PDF, Word, Excel) to automatically extract questions and add them to the knowledge base.
        </p>
        
        {/* Upload Mode Toggle */}
        <div className="mt-4 flex space-x-4">
          <button
            onClick={() => {
              setUploadMode('single');
              resetForm();
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              uploadMode === 'single'
                ? 'bg-arena-accent text-white'
                : 'bg-arena-border text-arena-text hover:bg-arena-border/80'
            }`}
          >
            Single File
          </button>
          <button
            onClick={() => {
              setUploadMode('multiple');
              resetForm();
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              uploadMode === 'multiple'
                ? 'bg-arena-accent text-white'
                : 'bg-arena-border text-arena-text hover:bg-arena-border/80'
            }`}
          >
            Multiple Files
          </button>
        </div>
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
            Drag and drop {uploadMode === 'multiple' ? 'documents' : 'a document'} here, or click to select
          </p>
          <p className="text-sm text-arena-text-muted">
            Supported formats: PDF, DOCX, DOC, XLSX, XLS
            {uploadMode === 'multiple' && ' (Max 10 files)'}
          </p>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.xlsx,.xls"
          multiple={uploadMode === 'multiple'}
          onChange={handleFileInputChange}
          className="hidden"
        />
        
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="arena-button px-6 py-3 rounded-lg font-medium disabled:opacity-50"
        >
          {isUploading ? 'Uploading...' : `Select ${uploadMode === 'multiple' ? 'Documents' : 'Document'}`}
        </button>
      </div>

      {/* Selected Files Display (Multiple Mode) */}
      {uploadMode === 'multiple' && selectedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-medium text-arena-text mb-3">
            Selected Files ({selectedFiles.length})
          </h4>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-arena-border/20 p-3 rounded-lg">
                <div className="flex items-center space-x-3">
                  <svg className="w-5 h-5 text-arena-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-arena-text font-medium">{file.name}</span>
                  <span className="text-arena-text-muted text-sm">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <button
                  onClick={() => {
                    const newFiles = selectedFiles.filter((_, i) => i !== index);
                    setSelectedFiles(newFiles);
                  }}
                  className="text-arena-text-muted hover:text-red-500 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex space-x-4">
            <button
              onClick={uploadMultipleFiles}
              disabled={isUploading || selectedFiles.length === 0}
              className="arena-button px-6 py-3 rounded-lg font-medium disabled:opacity-50"
            >
              {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} File${selectedFiles.length !== 1 ? 's' : ''}`}
            </button>
            <button
              onClick={() => setSelectedFiles([])}
              disabled={isUploading}
              className="px-6 py-3 rounded-lg font-medium border border-arena-border text-arena-text hover:bg-arena-border/20 transition-colors disabled:opacity-50"
            >
              Clear All
            </button>
          </div>
        </div>
      )}

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

      {/* Multi-File Upload Result */}
      {multiUploadResult && (
        <div className="mt-6 p-4 bg-arena-accent/10 border border-arena-accent/30 rounded-lg">
          <div className="flex justify-between items-start mb-4">
            <h4 className="text-lg font-medium text-arena-accent">
              Multi-File Upload Complete!
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
          
          <div className="space-y-3 mb-4">
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">Total files:</span>
              <span className="text-arena-text">{multiUploadResult.total_files}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">Successful:</span>
              <span className="text-green-400">{multiUploadResult.successful_files}</span>
            </div>
            
            {multiUploadResult.failed_files > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-arena-text-muted">Failed:</span>
                <span className="text-red-400">{multiUploadResult.failed_files}</span>
              </div>
            )}
            
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">Total questions extracted:</span>
              <span className="text-arena-text">{multiUploadResult.total_extracted_questions}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-arena-text-muted">Total added to knowledge base:</span>
              <span className="text-green-400">{multiUploadResult.total_added_entries}</span>
            </div>
            
            {multiUploadResult.total_skipped_entries > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-arena-text-muted">Total skipped (duplicates):</span>
                <span className="text-yellow-400">{multiUploadResult.total_skipped_entries}</span>
              </div>
            )}
          </div>

          {/* File Results */}
          <div className="mt-4">
            <h5 className="text-sm font-medium text-arena-text mb-3">
              File Results:
            </h5>
            <div className="max-h-64 overflow-y-auto space-y-2">
              {multiUploadResult.file_results.map((result, index) => (
                <div key={index} className={`p-3 rounded-lg border ${
                  result.status === 'success' 
                    ? 'bg-green-400/10 border-green-400/30' 
                    : 'bg-red-400/10 border-red-400/30'
                }`}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-arena-text">{result.filename}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      result.status === 'success' 
                        ? 'bg-green-400/20 text-green-400' 
                        : 'bg-red-400/20 text-red-400'
                    }`}>
                      {result.status}
                    </span>
                  </div>
                  
                  {result.status === 'success' ? (
                    <div className="text-xs text-arena-text-muted space-y-1">
                      <div>Questions: {result.extracted_questions} | Added: {result.added_entries} | Skipped: {result.skipped_entries}</div>
                    </div>
                  ) : (
                    <div className="text-xs text-red-400">
                      Error: {result.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
