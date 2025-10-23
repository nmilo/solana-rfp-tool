import React, { useState } from 'react';
import { useQuestions } from '../hooks/useQuestions';
import { ProcessingResult } from '../types';

interface QuestionInputProps {
  onResults: (results: ProcessingResult) => void;
}

export const QuestionInput: React.FC<QuestionInputProps> = ({ onResults }) => {
  const [inputType, setInputType] = useState<'text' | 'pdf'>('text');
  const [textInput, setTextInput] = useState('');
  const { isProcessing, error, processTextQuestions, processPDFQuestions, clearError } = useQuestions();

  const handleTextSubmit = async () => {
    if (!textInput.trim()) return;
    
    clearError();
    const results = await processTextQuestions(textInput);
    if (results) {
      onResults(results);
    }
  };

  const handlePDFUpload = async (file: File) => {
    clearError();
    const results = await processPDFQuestions(file);
    if (results) {
      onResults(results);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="arena-card rounded-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-arena-text mb-4 glow-text">
            Solana RFP Database
          </h1>
          <p className="text-arena-text-muted text-lg">
            Ask questions or upload PDFs to get answers from our knowledge base
          </p>
        </div>
        
        {/* Input Type Selection */}
        <div className="mb-8">
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setInputType('text')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                inputType === 'text'
                  ? 'arena-button text-arena-dark'
                  : 'bg-arena-light-gray text-arena-text-muted hover:text-arena-text hover:bg-arena-border'
              }`}
            >
              Text Input
            </button>
            <button
              onClick={() => setInputType('pdf')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                inputType === 'pdf'
                  ? 'arena-button text-arena-dark'
                  : 'bg-arena-light-gray text-arena-text-muted hover:text-arena-text hover:bg-arena-border'
              }`}
            >
              PDF Upload
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-arena-error/10 border border-arena-error/30 rounded-lg">
            <p className="text-arena-error text-sm">{error}</p>
          </div>
        )}

        {/* Text Input */}
        {inputType === 'text' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-arena-text-muted mb-3">
                Enter your RFP questions
              </label>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste your RFP questions here...&#10;&#10;Example:&#10;What are the transaction processing capabilities of your chain?&#10;Do you have explorers and recent audit coverage?"
                className="arena-textarea w-full h-40 p-4 rounded-lg resize-none"
                disabled={isProcessing}
              />
            </div>
            <button
              onClick={handleTextSubmit}
              disabled={isProcessing || !textInput.trim()}
              className="w-full arena-button py-4 px-6 rounded-lg font-medium text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-arena-dark border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing Questions...</span>
                </div>
              ) : (
                'Process Questions'
              )}
            </button>
          </div>
        )}

        {/* PDF Upload */}
        {inputType === 'pdf' && (
          <div className="space-y-6">
            <PDFUploader onUpload={handlePDFUpload} isProcessing={isProcessing} />
          </div>
        )}
      </div>
    </div>
  );
};

// PDF Uploader Component
interface PDFUploaderProps {
  onUpload: (file: File) => void;
  isProcessing: boolean;
}

const PDFUploader: React.FC<PDFUploaderProps> = ({ onUpload, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);

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
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        onUpload(file);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-arena-text-muted mb-3">
        Upload RFP PDF Document
      </label>
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive 
            ? 'border-arena-accent bg-arena-accent/5' 
            : 'border-arena-border hover:border-arena-accent/50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isProcessing}
        />
        
        <div className="space-y-4">
          <div className="mx-auto w-12 h-12 bg-arena-accent/20 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-arena-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          
          <div>
            <p className="text-arena-text font-medium">
              {isProcessing ? 'Processing PDF...' : 'Drop your PDF here or click to browse'}
            </p>
            <p className="text-arena-text-muted text-sm mt-1">
              Only PDF files are supported
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
