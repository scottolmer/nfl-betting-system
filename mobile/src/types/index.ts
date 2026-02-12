/**
 * TypeScript types for NFL Betting Analysis App
 * Matches backend API schemas
 */

export interface AgentAnalysis {
  name: string;
  confidence: number;
  reasoning: string;
  weight: number;
}

export interface PropAnalysis {
  player_id?: number;
  player_name: string;
  team: string;
  position: string;
  headshot_url?: string | null;
  stat_type: string;
  line: number;
  bet_type: 'OVER' | 'UNDER';
  opponent: string;
  confidence: number;
  projection?: number;
  cushion?: number;
  recommendation?: string;
  edge_explanation?: string;
  top_reasons: string[];
  agent_breakdown: Record<string, { score: number; weight: number; direction: string; rationale?: string[] }>;
  bookmaker?: string;
  all_books?: Array<{ bookmaker: string; line: number; odds?: number }>;
}

export interface ParlayLeg {
  player_name: string;
  team: string;
  stat_type: string;
  line: number;
  bet_type: 'OVER' | 'UNDER';
  confidence: number;
  opponent: string;
}

export interface Parlay {
  id: string;
  name: string;
  parlay_type?: string;
  legs: ParlayLeg[];
  combined_confidence: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  rationale?: string;
  leg_count: number;
}

export interface LineAdjustmentRequest {
  week: number;
  player_name: string;
  stat_type: string;
  bet_type: 'OVER' | 'UNDER';
  original_line: number;
  new_line: number;
}

export interface LineAdjustmentResponse {
  player_name: string;
  stat_type: string;
  bet_type: 'OVER' | 'UNDER';
  original_line: number;
  new_line: number;
  original_confidence: number;
  adjusted_confidence: number;
  confidence_change: number;
  projection?: number;
  original_cushion?: number;
  adjusted_cushion?: number;
  recommendation: string;
}

// Saved Parlay types for Parlay Builder
export type ParlayStatus = 'draft' | 'placed' | 'won' | 'lost' | 'pending';

export type Sportsbook =
  | 'DraftKings Pick 6'
  | 'FanDuel Pick 6'
  | 'Underdog Fantasy'
  | 'PrizePicks'
  | 'BetMGM'
  | 'Caesars'
  | 'ESPN Bet'
  | 'Other';

export interface SavedParlayLeg extends ParlayLeg {
  position: string;
  original_line?: number;  // For line adjustments
  adjusted_line?: number;
  projection?: number;
  cushion?: number;
}

export interface SavedParlay {
  id: string;
  name: string;
  week: number;
  legs: SavedParlayLeg[];
  combined_confidence: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  sportsbook?: Sportsbook;
  status: ParlayStatus;
  created_at: string;
  placed_at?: string;
  backend_id?: string;  // Backend database parlay_id after sync
  result?: {
    won: boolean;
    legs_hit: number;
    legs_total: number;
  };
}

// Filter options for prop selection
export interface PropFilters {
  min_confidence?: number;
  max_confidence?: number;
  teams?: string[];
  positions?: string[];
  stat_types?: string[];
  bet_type?: 'OVER' | 'UNDER';
}

// --- Sprint 1: New Types ---

export type AppMode = 'props' | 'parlays';

export interface UserProfile {
  id: string;
  email: string;
  display_name: string | null;
  subscription_tier: 'free' | 'trial' | 'premium';
  trial_start: string | null;
  trial_end: string | null;
  created_at: string | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Player {
  id: number;
  name: string;
  team: string;
  position: string;
  espn_id: string | null;
  headshot_url: string | null;
  status: string | null;
}

export interface PlayerProjection {
  id: number;
  player_id: number;
  week: number;
  stat_type: string;
  implied_line: number | null;
  engine_projection: number | null;
  confidence: number | null;
  direction: string | null;
  agent_breakdown: Record<string, {
    score: number;
    weight: number;
    direction: string;
  }> | null;
}

export interface BookOddsEntry {
  id: number;
  player_id: number;
  week: number;
  stat_type: string;
  bookmaker: string;
  line: number;
  over_price: number | null;
  under_price: number | null;
  fetched_at: string | null;
}

export interface BestPrices {
  player_id: number;
  stat_type: string;
  best_over: { bookmaker: string; line: number; price: number } | null;
  best_under: { bookmaker: string; line: number; price: number } | null;
}

export interface LineMovementEntry {
  bookmaker: string;
  line: number;
  over_price: number | null;
  under_price: number | null;
  recorded_at: string | null;
}

export interface RawBookOdds {
  book: string;
  line: number;
  price: number;
  side: 'over' | 'under';
  timestamp: string;
}
