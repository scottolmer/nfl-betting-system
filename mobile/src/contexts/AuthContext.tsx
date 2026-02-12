/**
 * Auth state context with auto-refresh.
 * Wraps the app to provide authentication state everywhere.
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authService } from '../services/authService';
import { UserProfile } from '../types';

interface AuthState {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: UserProfile | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  isLoading: true,
  isAuthenticated: false,
  user: null,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  refreshProfile: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);

  // Initialize: check for stored tokens on app start
  useEffect(() => {
    (async () => {
      const tokens = await authService.init();
      if (tokens) {
        try {
          const profile = await authService.getProfile();
          setUser(profile);
        } catch {
          // Token expired — try refresh
          const refreshed = await authService.refresh();
          if (refreshed) {
            try {
              const profile = await authService.getProfile();
              setUser(profile);
            } catch {
              await authService.logout();
            }
          }
        }
      }
      setIsLoading(false);
    })();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    await authService.login(email, password);
    const profile = await authService.getProfile();
    setUser(profile);
  }, []);

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    await authService.register(email, password, displayName);
    const profile = await authService.getProfile();
    setUser(profile);
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    if (authService.isAuthenticated()) {
      const profile = await authService.getProfile();
      setUser(profile);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isLoading,
        isAuthenticated: user !== null,
        user,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
