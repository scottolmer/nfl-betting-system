import AsyncStorage from '@react-native-async-storage/async-storage';
import { SavedParlay } from '../types';

const GUEST_BETS_KEY = 'guest_bets';

export const storageService = {
    async saveGuestBet(bet: SavedParlay): Promise<void> {
        try {
            const existing = await this.getGuestBets();
            const updated = [bet, ...existing];
            await AsyncStorage.setItem(GUEST_BETS_KEY, JSON.stringify(updated));
        } catch (error) {
            console.error('Failed to save guest bet:', error);
        }
    },

    async getGuestBets(): Promise<SavedParlay[]> {
        try {
            const json = await AsyncStorage.getItem(GUEST_BETS_KEY);
            return json ? JSON.parse(json) : [];
        } catch (error) {
            console.error('Failed to load guest bets:', error);
            return [];
        }
    },

    async clearGuestBets(): Promise<void> {
        try {
            await AsyncStorage.removeItem(GUEST_BETS_KEY);
        } catch (error) {
            console.error('Failed to clear guest bets:', error);
        }
    }
};
