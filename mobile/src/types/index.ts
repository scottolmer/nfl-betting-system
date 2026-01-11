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
  player_name: string;
  team: string;
  position: string;
  stat_type: string;
  line: number;
  bet_type: 'OVER' | 'UNDER';
  opponent: string;
  confidence: number;
  projection?: number;
  cushion?: number;
  top_reasons: string[];
  agent_analyses: AgentAnalysis[];
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
  legs: ParlayLeg[];
  combined_confidence: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
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
  bet_amount?: number;
  status: ParlayStatus;
  created_at: string;
  placed_at?: string;
  result?: {
    won: boolean;
    profit?: number;
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
