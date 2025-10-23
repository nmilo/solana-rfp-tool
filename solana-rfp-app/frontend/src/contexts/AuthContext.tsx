import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
  login_count: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string) => Promise<boolean>;
  loginWithGoogle: (email: string, name: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored token on app load
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // Verify token and get user info
      verifyToken(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const verifyToken = async (token: string) => {
    try {
      // Check if it's a mock token
      if (token.startsWith('mock-jwt-token-')) {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          setToken(token);
          setIsLoading(false);
          return;
        }
      }
      
      // Try to verify with backend
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'https://solana-rfp-271974794838.herokuapp.com'}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setToken(token);
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // First verify if email is allowed
      const verifyResponse = await fetch(`http://localhost:8000/api/v1/auth/verify-email/${encodeURIComponent(email)}`);
      const verifyData = await verifyResponse.json();
      
      if (!verifyData.is_allowed) {
        throw new Error('Email domain not allowed');
      }

      // Proceed with login
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setToken(data.access_token);
        localStorage.setItem('auth_token', data.access_token);
        return true;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async (email: string, name: string): Promise<boolean> => {
    try {
      setIsLoading(true);

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'https://solana-rfp-271974794838.herokuapp.com'}/api/v1/auth/google-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email,
          name: name
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setToken(data.access_token);
        localStorage.setItem('auth_token', data.access_token);
        return true;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Google login failed');
      }
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    loginWithGoogle,
    logout,
    isLoading,
    isAuthenticated: !!user && !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
