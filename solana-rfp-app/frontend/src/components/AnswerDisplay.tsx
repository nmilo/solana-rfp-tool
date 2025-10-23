import React from 'react';
import { ProcessingResult } from '../types';

interface AnswerDisplayProps {
  results: ProcessingResult;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ results }) => {
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
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-medium text-arena-text mb-2">
                      Question {index + 1}
                    </h4>
                    <p className="text-arena-text-muted bg-arena-light-gray/30 p-3 rounded-lg">
                      {result.question}
                    </p>
                  </div>
                  
                  <div className="ml-4 text-right">
                    <div className={`text-sm font-medium ${getConfidenceColor(result.confidence)}`}>
                      {getConfidenceLabel(result.confidence)}
                    </div>
                    <div className="text-xs text-arena-text-muted">
                      {Math.round(result.confidence * 100)}% match
                    </div>
                  </div>
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
        <div className="mt-8 flex justify-center space-x-4">
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
      </div>
    </div>
  );
};
