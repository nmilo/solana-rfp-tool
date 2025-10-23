import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// Extend Window interface for Google Sign-in
declare global {
  interface Window {
    google?: {
      accounts?: {
        id?: {
          initialize: (config: any) => void;
          renderButton: (element: HTMLElement, config: any) => void;
          prompt: () => void;
        };
      };
    };
  }
}

const LoginPage: React.FC = () => {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleGoogleResponse = useCallback(async (response: any) => {
    setError('');
    setIsLoading(true);

    try {
      // Decode the JWT token to get user info
      const payload = JSON.parse(atob(response.credential.split('.')[1]));
      const email = payload.email;
      const name = payload.name;

      const success = await loginWithGoogle(email, name);
      if (success) {
        navigate('/');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Google login failed');
    } finally {
      setIsLoading(false);
    }
  }, [loginWithGoogle, navigate]);

  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 50; // 5 seconds max wait time

    const initializeGoogleSignIn = () => {
      console.log('Initializing Google Sign-in, retry count:', retryCount);
      console.log('window.google:', window.google);
      console.log('window.google?.accounts:', window.google?.accounts);
      console.log('window.google?.accounts?.id:', window.google?.accounts?.id);
      
      if (window.google?.accounts?.id) {
        const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
        console.log('Client ID:', clientId);
        
        if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
          // Show error message if no client ID is configured
          setError('Google Client ID not configured. Please set REACT_APP_GOOGLE_CLIENT_ID in your .env file.');
          return;
        }

        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: handleGoogleResponse,
          auto_select: false,
          cancel_on_tap_outside: true
        });

        // Render the button
        const buttonElement = document.getElementById('google-signin-button');
        if (buttonElement) {
          window.google.accounts.id.renderButton(buttonElement, {
            theme: 'outline',
            size: 'large',
            width: '100%',
            text: 'continue_with',
            shape: 'rectangular'
          });
        }
      } else if (retryCount < maxRetries) {
        // Google script not loaded yet, retry after a short delay
        retryCount++;
        setTimeout(initializeGoogleSignIn, 100);
      } else {
        // Max retries reached, show error
        setError('Google Sign-in script not loaded. Please check your internet connection.');
      }
    };

    // Start initialization
    initializeGoogleSignIn();
  }, [handleGoogleResponse]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-arena-dark to-arena-darker flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-arena-primary rounded-full mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Solana RFP Database</h1>
          <p className="text-arena-text-muted">Access the knowledge base</p>
        </div>

        {/* Login Form */}
        <div className="arena-card p-8 rounded-lg">
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-lg font-medium text-arena-text mb-2">Sign in to continue</h2>
              <p className="text-sm text-arena-text-muted">
                Use your authorized email account to access the Solana RFP Database
              </p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <div className="flex">
                  <svg className="w-5 h-5 text-red-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h3 className="text-sm font-medium text-red-400">Login Failed</h3>
                    <p className="text-sm text-red-300 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Google Sign-in Button */}
            <div className="space-y-4">
              <div id="google-signin-button" className="w-full"></div>
              
              {/* Temporary bypass buttons for testing */}
              <div className="space-y-2">
                <button
                  onClick={async () => {
                    try {
                      const success = await loginWithGoogle('mandicnikola1989@gmail.com', 'Manda');
                      if (success) {
                        navigate('/');
                      }
                    } catch (err) {
                      console.error('Test login failed:', err);
                      setError('Test login failed: ' + (err as Error).message);
                    }
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Test Login (Manda)
                </button>
                
                <button
                  onClick={async () => {
                    try {
                      const success = await loginWithGoogle('dragan.zurzin@solana.org', 'Dragan');
                      if (success) {
                        navigate('/');
                      }
                    } catch (err) {
                      console.error('Test login failed:', err);
                      setError('Test login failed: ' + (err as Error).message);
                    }
                  }}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Test Login (Dragan)
                </button>
                
                <button
                  onClick={async () => {
                    try {
                      const success = await loginWithGoogle('anyone@example.com', 'Demo User');
                      if (success) {
                        navigate('/');
                      }
                    } catch (err) {
                      console.error('Test login failed:', err);
                      setError('Test login failed: ' + (err as Error).message);
                    }
                  }}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Test Login (Any Email)
                </button>
              </div>
              
              {/* Fallback button for testing when Google Client ID is not configured */}
              {(!process.env.REACT_APP_GOOGLE_CLIENT_ID || process.env.REACT_APP_GOOGLE_CLIENT_ID === 'your-google-client-id.apps.googleusercontent.com') && (
                <div className="space-y-4">
                  <div className="text-center text-sm text-arena-text-muted mb-4">
                    Google Client ID not configured. For testing, you can use the developer email:
                  </div>
                  <button
                    onClick={async () => {
                      // Simulate Google response for testing
                      const mockResponse = {
                        credential: btoa(JSON.stringify({
                          email: 'mandicnikola1989@gmail.com',
                          name: 'Nikola Mandic',
                          sub: '123456789',
                          aud: 'test',
                          iss: 'https://accounts.google.com',
                          iat: Math.floor(Date.now() / 1000),
                          exp: Math.floor(Date.now() / 1000) + 3600
                        }))
                      };
                      await handleGoogleResponse(mockResponse);
                    }}
                    disabled={isLoading}
                    className="w-full bg-arena-primary hover:bg-arena-primary/90 disabled:bg-arena-primary/50 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center"
                  >
                    {isLoading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Signing in...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Test Login (Developer)
                      </>
                    )}
                  </button>
                </div>
              )}
              
              {isLoading && (
                <div className="flex items-center justify-center py-4">
                  <svg className="animate-spin h-6 w-6 text-arena-primary" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="ml-2 text-arena-text">Signing in...</span>
                </div>
              )}
            </div>
          </div>

          {/* Info Section */}
          <div className="mt-8 pt-6 border-t border-arena-border">
            <div className="text-center">
              <h3 className="text-sm font-medium text-arena-text mb-2">Authorized Access Only</h3>
              <p className="text-xs text-arena-text-muted">
                This application is restricted to Solana Foundation team members and authorized personnel.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-arena-text-muted">
            © 2025 Solana Foundation. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
