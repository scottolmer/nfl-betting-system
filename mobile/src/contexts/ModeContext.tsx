/**
 * App mode context: DFS / Props / Fantasy.
 * Controls which pillar the user is in, persisted across sessions.
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppMode } from '../types';

const MODE_KEY = 'app_mode';

interface ModeState {
  mode: AppMode;
  setMode: (mode: AppMode) => void;
}

const ModeContext = createContext<ModeState>({
  mode: 'props',
  setMode: () => {},
});

export function ModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<AppMode>('props');

  useEffect(() => {
    (async () => {
      try {
        const stored = await AsyncStorage.getItem(MODE_KEY);
        if (stored && ['props', 'parlays'].includes(stored)) {
          setModeState(stored as AppMode);
        }
      } catch {
        // Default to props
      }
    })();
  }, []);

  const setMode = useCallback((newMode: AppMode) => {
    setModeState(newMode);
    AsyncStorage.setItem(MODE_KEY, newMode).catch(() => {});
  }, []);

  return (
    <ModeContext.Provider value={{ mode, setMode }}>
      {children}
    </ModeContext.Provider>
  );
}

export const useMode = () => useContext(ModeContext);
