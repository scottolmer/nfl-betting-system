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
  async markAsPlaced(id: string, betAmount?: number): Promise<boolean> {
    return this.updateParlay(id, {
      status: 'placed',
      placed_at: new Date().toISOString(),
      bet_amount: betAmount,
    });
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
