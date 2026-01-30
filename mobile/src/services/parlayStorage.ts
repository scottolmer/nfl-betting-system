/**
 * Parlay Storage Service
 * Manages saved parlays using AsyncStorage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { SavedParlay } from '../types';

const STORAGE_KEY = '@nfl_betting:saved_parlays';
const FREE_TIER_LIMIT = 3; // Max 3 saved parlays for free tier

class ParlayStorageService {
  /**
   * Get all saved parlays
   */
  async getAllParlays(): Promise<SavedParlay[]> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEY);
      if (!data) return [];
      return JSON.parse(data) as SavedParlay[];
    } catch (error) {
      console.error('Error loading parlays:', error);
      return [];
    }
  }

  /**
   * Get a specific parlay by ID
   */
  async getParlay(id: string): Promise<SavedParlay | null> {
    const parlays = await this.getAllParlays();
    return parlays.find(p => p.id === id) || null;
  }

  /**
   * Save a new parlay
   */
  async saveParlay(parlay: SavedParlay): Promise<{ success: boolean; error?: string }> {
    try {
      const parlays = await this.getAllParlays();

      // Check free tier limit
      if (parlays.length >= FREE_TIER_LIMIT) {
        return {
          success: false,
          error: `Free tier limit reached (${FREE_TIER_LIMIT} parlays). Delete old parlays or upgrade to Premium.`
        };
      }

      // Add new parlay
      parlays.push(parlay);
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(parlays));
      return { success: true };
    } catch (error) {
      console.error('Error saving parlay:', error);
      return {
        success: false,
        error: 'Failed to save parlay. Please try again.'
      };
    }
  }

  /**
   * Update an existing parlay
   */
  async updateParlay(id: string, updates: Partial<SavedParlay>): Promise<boolean> {
    try {
      const parlays = await this.getAllParlays();
      const index = parlays.findIndex(p => p.id === id);

      if (index === -1) return false;

      parlays[index] = { ...parlays[index], ...updates };
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(parlays));
      return true;
    } catch (error) {
      console.error('Error updating parlay:', error);
      return false;
    }
  }

  /**
   * Delete a parlay
   */
  async deleteParlay(id: string): Promise<boolean> {
    try {
      const parlays = await this.getAllParlays();
      const filtered = parlays.filter(p => p.id !== id);
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error deleting parlay:', error);
      return false;
    }
  }

  /**
   * Get parlay count (for free tier limit display)
   */
  async getParlayCount(): Promise<number> {
    const parlays = await this.getAllParlays();
    return parlays.length;
  }

  /**
   * Check if user has reached free tier limit
   */
  async hasReachedLimit(): Promise<boolean> {
    const count = await this.getParlayCount();
    return count >= FREE_TIER_LIMIT;
  }

  /**
   * Get remaining parlay slots
   */
  async getRemainingSlots(): Promise<number> {
    const count = await this.getParlayCount();
    return Math.max(0, FREE_TIER_LIMIT - count);
  }

  /**
   * Mark parlay as placed
   */
  async markAsPlaced(id: string): Promise<boolean> {
    return this.updateParlay(id, {
      status: 'placed',
      placed_at: new Date().toISOString(),
    });
  }

  /**
   * Grade a parlay with backend result data
   */
  async gradeParlay(
    id: string,
    result: { won: boolean; legs_hit: number; legs_total: number }
  ): Promise<boolean> {
    const status = result.won ? 'won' : 'lost';
    return this.updateParlay(id, {
      status,
      result,
    });
  }

  /**
   * Mark parlay as won
   */
  async markAsWon(id: string, legsHit: number, legsTotal: number): Promise<boolean> {
    return this.gradeParlay(id, {
      won: true,
      legs_hit: legsHit,
      legs_total: legsTotal,
    });
  }

  /**
   * Mark parlay as lost
   */
  async markAsLost(id: string, legsHit: number, legsTotal: number): Promise<boolean> {
    return this.gradeParlay(id, {
      won: false,
      legs_hit: legsHit,
      legs_total: legsTotal,
    });
  }

  /**
   * Sync parlay to backend for future scoring
   */
  async syncToBackend(id: string, backendUrl: string): Promise<{ success: boolean; backend_id?: string; error?: string }> {
    try {
      const parlay = await this.getParlay(id);
      if (!parlay) {
        return { success: false, error: 'Parlay not found' };
      }

      // Send to backend
      const response = await fetch(`${backendUrl}/api/results/sync-parlay`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parlay),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();

      // Update local parlay with backend_id
      if (data.parlay_id) {
        await this.updateParlay(id, { backend_id: data.parlay_id });
      }

      return {
        success: true,
        backend_id: data.parlay_id,
      };
    } catch (error) {
      console.error('Error syncing to backend:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to sync',
      };
    }
  }

  /**
   * Fetch results from backend for a specific week
   */
  async fetchResults(week: number, backendUrl: string): Promise<{ success: boolean; updated: number; error?: string }> {
    try {
      // Fetch results from backend
      const response = await fetch(`${backendUrl}/api/results/parlay-results?week=${week}`);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();

      if (!data.success || !data.parlays) {
        throw new Error('Invalid response from backend');
      }

      // Match backend parlays with local parlays
      const localParlays = await this.getAllParlays();
      let updatedCount = 0;

      for (const backendParlay of data.parlays) {
        // Find matching local parlay by backend_id or by matching week + legs
        let localParlay = localParlays.find(p => p.backend_id === backendParlay.parlay_id);

        if (!localParlay) {
          // Try to match by week and player names
          localParlay = localParlays.find(p => {
            if (p.week !== week) return false;
            if (p.legs.length !== backendParlay.legs_total) return false;

            // Check if all players match
            const localPlayers = p.legs.map(l => l.player_name.toLowerCase()).sort();
            const backendPlayers = backendParlay.legs.map((l: any) => l.player.toLowerCase()).sort();

            return JSON.stringify(localPlayers) === JSON.stringify(backendPlayers);
          });
        }

        if (localParlay && backendParlay.status !== 'pending') {
          // Update local parlay with backend results
          const won = backendParlay.status === 'won';
          await this.gradeParlay(localParlay.id, {
            won,
            legs_hit: backendParlay.legs_hit,
            legs_total: backendParlay.legs_total,
          });

          // Update backend_id if not set
          if (!localParlay.backend_id) {
            await this.updateParlay(localParlay.id, { backend_id: backendParlay.parlay_id });
          }

          updatedCount++;
        }
      }

      return {
        success: true,
        updated: updatedCount,
      };
    } catch (error) {
      console.error('Error fetching results:', error);
      return {
        success: false,
        updated: 0,
        error: error instanceof Error ? error.message : 'Failed to fetch results',
      };
    }
  }

  /**
   * Get won parlays
   */
  async getWonParlays(): Promise<SavedParlay[]> {
    return this.getParlaysByStatus('won');
  }

  /**
   * Get lost parlays
   */
  async getLostParlays(): Promise<SavedParlay[]> {
    return this.getParlaysByStatus('lost');
  }

  /**
   * Get analytics across all graded parlays
   */
  async getAnalytics(): Promise<{
    total_graded: number;
    wins: number;
    losses: number;
    win_rate: number;
    avg_confidence: number;
    by_confidence_tier: Array<{
      tier: string;
      min_confidence: number;
      max_confidence: number;
      count: number;
      wins: number;
      win_rate: number;
    }>;
    by_risk_level: Array<{
      risk_level: string;
      count: number;
      wins: number;
      win_rate: number;
    }>;
    by_prop_type: Array<{
      prop_type: string;
      total_legs: number;
      legs_hit: number;
      hit_rate: number;
    }>;
    by_position: Array<{
      position: string;
      total_legs: number;
      legs_hit: number;
      hit_rate: number;
    }>;
  }> {
    const allParlays = await this.getAllParlays();
    const gradedParlays = allParlays.filter(p => p.status === 'won' || p.status === 'lost');

    const wins = gradedParlays.filter(p => p.status === 'won').length;
    const losses = gradedParlays.filter(p => p.status === 'lost').length;
    const total_graded = gradedParlays.length;
    const win_rate = total_graded > 0 ? (wins / total_graded) * 100 : 0;

    // Average confidence
    const totalConfidence = gradedParlays.reduce((sum, p) => sum + p.combined_confidence, 0);
    const avg_confidence = total_graded > 0 ? totalConfidence / total_graded : 0;

    // By confidence tier
    const confidenceTiers = [
      { tier: '80+', min: 80, max: 100 },
      { tier: '75-79', min: 75, max: 79.99 },
      { tier: '70-74', min: 70, max: 74.99 },
      { tier: '<70', min: 0, max: 69.99 },
    ];

    const by_confidence_tier = confidenceTiers.map(tier => {
      const tieredParlays = gradedParlays.filter(
        p => p.combined_confidence >= tier.min && p.combined_confidence <= tier.max
      );
      const tierWins = tieredParlays.filter(p => p.status === 'won').length;
      const count = tieredParlays.length;

      return {
        tier: tier.tier,
        min_confidence: tier.min,
        max_confidence: tier.max,
        count,
        wins: tierWins,
        win_rate: count > 0 ? (tierWins / count) * 100 : 0,
      };
    });

    // By risk level
    const riskLevels = ['LOW', 'MEDIUM', 'HIGH'] as const;
    const by_risk_level = riskLevels.map(level => {
      const levelParlays = gradedParlays.filter(p => p.risk_level === level);
      const levelWins = levelParlays.filter(p => p.status === 'won').length;
      const count = levelParlays.length;

      return {
        risk_level: level,
        count,
        wins: levelWins,
        win_rate: count > 0 ? (levelWins / count) * 100 : 0,
      };
    });

    // By prop type (analyze individual legs)
    const propTypeStats: Record<string, { total: number; hits: number }> = {};

    for (const parlay of gradedParlays) {
      if (!parlay.result) continue;

      for (const leg of parlay.legs) {
        const propType = leg.stat_type;
        if (!propTypeStats[propType]) {
          propTypeStats[propType] = { total: 0, hits: 0 };
        }

        propTypeStats[propType].total += 1;

        // Count as hit if parlay won (simplified - assumes all legs hit if parlay won)
        // For more accurate tracking, would need individual leg results
        if (parlay.status === 'won') {
          propTypeStats[propType].hits += 1;
        }
      }
    }

    const by_prop_type = Object.entries(propTypeStats).map(([prop_type, stats]) => ({
      prop_type,
      total_legs: stats.total,
      legs_hit: stats.hits,
      hit_rate: stats.total > 0 ? (stats.hits / stats.total) * 100 : 0,
    }));

    // By position (analyze individual legs)
    const positionStats: Record<string, { total: number; hits: number }> = {};

    for (const parlay of gradedParlays) {
      if (!parlay.result) continue;

      for (const leg of parlay.legs) {
        const position = leg.position || 'Unknown';
        if (!positionStats[position]) {
          positionStats[position] = { total: 0, hits: 0 };
        }

        positionStats[position].total += 1;

        // Count as hit if parlay won (simplified)
        if (parlay.status === 'won') {
          positionStats[position].hits += 1;
        }
      }
    }

    const by_position = Object.entries(positionStats).map(([position, stats]) => ({
      position,
      total_legs: stats.total,
      legs_hit: stats.hits,
      hit_rate: stats.total > 0 ? (stats.hits / stats.total) * 100 : 0,
    }));

    return {
      total_graded,
      wins,
      losses,
      win_rate,
      avg_confidence,
      by_confidence_tier,
      by_risk_level,
      by_prop_type,
      by_position,
    };
  }

  /**
   * Clear all parlays (for testing/reset)
   */
  async clearAll(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing parlays:', error);
    }
  }

  /**
   * Get parlays by status
   */
  async getParlaysByStatus(status: SavedParlay['status']): Promise<SavedParlay[]> {
    const parlays = await this.getAllParlays();
    return parlays.filter(p => p.status === status);
  }

  /**
   * Get draft parlays
   */
  async getDraftParlays(): Promise<SavedParlay[]> {
    return this.getParlaysByStatus('draft');
  }

  /**
   * Get placed parlays
   */
  async getPlacedParlays(): Promise<SavedParlay[]> {
    return this.getParlaysByStatus('placed');
  }
}

// Export singleton instance
export const parlayStorage = new ParlayStorageService();
export const FREE_TIER_PARLAY_LIMIT = FREE_TIER_LIMIT;
