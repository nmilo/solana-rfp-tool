import { useState } from 'react';
import { apiService } from '../services/api';
import { ProcessingResult } from '../types';

export const useQuestions = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processTextQuestions = async (text: string): Promise<ProcessingResult | null> => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const result = await apiService.processTextQuestions(text);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  const processPDFQuestions = async (file: File): Promise<ProcessingResult | null> => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const result = await apiService.processPDFQuestions(file);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  return {
    isProcessing,
    error,
    processTextQuestions,
    processPDFQuestions,
    clearError: () => setError(null)
  };
};
