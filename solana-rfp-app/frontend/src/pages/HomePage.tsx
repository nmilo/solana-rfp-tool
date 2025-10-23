import React, { useState } from 'react';
import { QuestionInput } from '../components/QuestionInput';
import { AnswerDisplay } from '../components/AnswerDisplay';
import { ProcessingResult } from '../types';

export const HomePage: React.FC = () => {
  const [results, setResults] = useState<ProcessingResult | null>(null);

  const handleResults = (newResults: ProcessingResult) => {
    setResults(newResults);
  };

  return (
    <div className="arena-container min-h-screen">
      <div className="arena-grid">
        <div className="relative">
          {!results ? (
            <QuestionInput onResults={handleResults} />
          ) : (
            <AnswerDisplay results={results} />
          )}
        </div>
      </div>
    </div>
  );
};
