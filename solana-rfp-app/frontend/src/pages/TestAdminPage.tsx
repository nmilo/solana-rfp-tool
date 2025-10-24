import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const TestAdminPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    testAdminPreview();
  }, []);

  const testAdminPreview = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Testing admin preview API...');
      const result = await apiService.getKnowledgeBasePreview(1, 5);
      
      console.log('Admin preview result:', result);
      setData(result);
    } catch (err) {
      console.error('Admin preview error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load admin preview');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Testing Admin Preview</h1>
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Testing Admin Preview</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error</h3>
          <p className="text-red-700 mt-2">{error}</p>
          <button
            onClick={testAdminPreview}
            className="mt-4 bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Admin Preview Test</h1>
      
      <div className="mb-4">
        <button
          onClick={testAdminPreview}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          Refresh Data
        </button>
      </div>

      {data && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="text-green-800 font-medium">✅ API Working!</h3>
            <p className="text-green-700">
              Total entries: {data.pagination?.total_entries || 0}
            </p>
            <p className="text-green-700">
              Current page: {data.pagination?.page || 0} of {data.pagination?.total_pages || 0}
            </p>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <h3 className="font-medium mb-2">Sample Entries:</h3>
            {data.entries?.slice(0, 3).map((entry: any, index: number) => (
              <div key={entry.id} className="mb-3 p-3 bg-gray-50 rounded">
                <div className="font-medium text-sm text-gray-600">
                  Entry {index + 1}
                </div>
                <div className="font-medium">
                  {entry.question}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {entry.answer_preview}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Category: {entry.category || 'None'} | 
                  Created: {new Date(entry.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-blue-800 font-medium">Raw API Response:</h3>
            <pre className="text-xs text-blue-700 mt-2 overflow-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestAdminPage;

