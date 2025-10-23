import React, { useState } from 'react';
import { ProcessingResult } from '../types';
import { apiService } from '../services/api';

interface AnswerDisplayProps {
  results: ProcessingResult;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ results }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportType, setExportType] = useState<'pdf' | 'docx' | null>(null);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'text-arena-success';
    if (confidence >= 0.4) return 'text-arena-warning';
    return 'text-arena-error';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.7) return 'High Confidence';
    if (confidence >= 0.4) return 'Medium Confidence';
    return 'Low Confidence';
  };

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExport = async (format: 'pdf' | 'docx') => {
    if (!results.submission_id) {
      // Use direct export for immediate results
      try {
        setIsExporting(true);
        setExportType(format);
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `rfp_answers_${timestamp}`;
        
        let blob: Blob;
        if (format === 'pdf') {
          blob = await apiService.exportToPDFDirect(results, filename);
        } else {
          blob = await apiService.exportToDOCXDirect(results, filename);
        }
        
        downloadFile(blob, `${filename}.${format}`);
      } catch (error) {
        console.error(`Error exporting to ${format}:`, error);
        alert(`Failed to export to ${format.toUpperCase()}. Please try again.`);
      } finally {
        setIsExporting(false);
        setExportType(null);
      }
    } else {
      // Use submission-based export
      try {
        setIsExporting(true);
        setExportType(format);
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `rfp_answers_${timestamp}`;
        
        let blob: Blob;
        if (format === 'pdf') {
          blob = await apiService.exportToPDF(results.submission_id, filename);
        } else {
          blob = await apiService.exportToDOCX(results.submission_id, filename);
        }
        
        downloadFile(blob, `${filename}.${format}`);
      } catch (error) {
        console.error(`Error exporting to ${format}:`, error);
        alert(`Failed to export to ${format.toUpperCase()}. Please try again.`);
      } finally {
        setIsExporting(false);
        setExportType(null);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="arena-card rounded-xl p-8">
        {/* Summary */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-arena-text mb-4">Results Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="arena-card p-4 rounded-lg">
              <div className="text-arena-text-muted text-sm">Questions Processed</div>
              <div className="text-2xl font-bold text-arena-text">{results.questions_processed}</div>
            </div>
            <div className="arena-card p-4 rounded-lg">
              <div className="text-arena-text-muted text-sm">Answers Found</div>
              <div className="text-2xl font-bold text-arena-success">{results.answers_found}</div>
            </div>
            <div className="arena-card p-4 rounded-lg">
              <div className="text-arena-text-muted text-sm">Processing Time</div>
              <div className="text-2xl font-bold text-arena-accent">
                {results.processing_time ? `${results.processing_time.toFixed(2)}s` : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-arena-text">Question & Answer Pairs</h3>
          
          {results.results.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-arena-error/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-arena-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <p className="text-arena-text-muted">No questions were processed or no answers were found.</p>
            </div>
          ) : (
            results.results.map((result, index) => (
              <div key={index} className="arena-card p-6 rounded-lg">
                <div className="mb-4">
                  <h4 className="text-lg font-medium text-arena-text mb-2">
                    Question {index + 1}
                  </h4>
                  <p className="text-arena-text-muted bg-arena-light-gray/30 p-3 rounded-lg">
                    {result.question}
                  </p>
                </div>

                <div>
                  <h5 className="text-md font-medium text-arena-text mb-2">Answer</h5>
                  <div className="bg-arena-dark/50 p-4 rounded-lg border-l-4 border-arena-accent">
                    <p className="text-arena-text leading-relaxed">
                      {result.answer}
                    </p>
                  </div>
                </div>

                {result.source_id && (
                  <div className="mt-4 pt-4 border-t border-arena-border">
                    <div className="flex items-center space-x-2 text-xs text-arena-text-muted">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Source: Knowledge Base Entry</span>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Actions */}
        <div className="mt-8">
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => window.location.reload()}
              className="arena-button px-6 py-3 rounded-lg font-medium"
            >
              Ask New Questions
            </button>
            <button
              onClick={() => {
                const text = results.results.map((r, i) => 
                  `${i + 1}. ${r.question}\n   Answer: ${r.answer}\n`
                ).join('\n');
                navigator.clipboard.writeText(text);
              }}
              className="bg-arena-light-gray hover:bg-arena-border text-arena-text px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Copy Results
            </button>
          </div>
          
          {/* Export Section */}
          <div className="mt-6 pt-6 border-t border-arena-border">
            <h4 className="text-lg font-semibold text-arena-text mb-4 text-center">Export Results</h4>
            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={() => handleExport('pdf')}
                disabled={isExporting}
                className="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                {isExporting && exportType === 'pdf' ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Generating PDF...</span>
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Export PDF</span>
                  </>
                )}
              </button>
              
              <button
                onClick={() => handleExport('docx')}
                disabled={isExporting}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                {isExporting && exportType === 'docx' ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Generating DOCX...</span>
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Export DOCX</span>
                  </>
                )}
              </button>
            </div>
            
            <div className="mt-4 text-center">
              <p className="text-sm text-arena-text-muted">
                Export includes all questions and answers. Empty answers are marked for manual completion.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
