/**
 * ParlayContext — Tracks props selected for parlay building.
 * Shared across Props screens so picks persist while browsing.
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { PropAnalysis } from '../types';

const MAX_PICKS = 6;

interface ParlayState {
  picks: PropAnalysis[];
  maxPicks: number;
  addPick: (prop: PropAnalysis) => void;
  removePick: (prop: PropAnalysis) => void;
  togglePick: (prop: PropAnalysis) => void;
  clearPicks: () => void;
  isPicked: (prop: PropAnalysis) => boolean;
  combinedConfidence: number;
}

const ParlayContext = createContext<ParlayState>({
  picks: [],
  maxPicks: MAX_PICKS,
  addPick: () => {},
  removePick: () => {},
  togglePick: () => {},
  clearPicks: () => {},
  isPicked: () => false,
  combinedConfidence: 0,
});

function pickKey(prop: PropAnalysis): string {
  return `${prop.player_name}|${prop.stat_type}|${prop.bet_type}`;
}

export function ParlayProvider({ children }: { children: ReactNode }) {
  const [picks, setPicks] = useState<PropAnalysis[]>([]);

  const isPicked = useCallback(
    (prop: PropAnalysis) => picks.some((p) => pickKey(p) === pickKey(prop)),
    [picks],
  );

  const addPick = useCallback((prop: PropAnalysis) => {
    setPicks((prev) => {
      if (prev.length >= MAX_PICKS) return prev;
      if (prev.some((p) => pickKey(p) === pickKey(prop))) return prev;
      return [...prev, prop];
    });
  }, []);

  const removePick = useCallback((prop: PropAnalysis) => {
    setPicks((prev) => prev.filter((p) => pickKey(p) !== pickKey(prop)));
  }, []);

  const togglePick = useCallback((prop: PropAnalysis) => {
    setPicks((prev) => {
      const exists = prev.some((p) => pickKey(p) === pickKey(prop));
      if (exists) return prev.filter((p) => pickKey(p) !== pickKey(prop));
      if (prev.length >= MAX_PICKS) return prev;
      return [...prev, prop];
    });
  }, []);

  const clearPicks = useCallback(() => setPicks([]), []);

  // Combined confidence: geometric mean of individual confidences
  const combinedConfidence =
    picks.length > 0
      ? Math.round(
          picks.reduce((acc, p) => acc * (p.confidence / 100), 1) *
            100 *
            // Slight bonus for fewer correlated legs
            (1 - picks.length * 0.02),
        )
      : 0;

  return (
    <ParlayContext.Provider
      value={{
        picks,
        maxPicks: MAX_PICKS,
        addPick,
        removePick,
        togglePick,
        clearPicks,
        isPicked,
        combinedConfidence,
      }}
    >
      {children}
    </ParlayContext.Provider>
  );
}

export const useParlay = () => useContext(ParlayContext);
