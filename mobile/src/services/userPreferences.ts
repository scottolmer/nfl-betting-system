/**
 * User Preferences Service
 * Manages persistent user preferences using AsyncStorage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// Storage keys
const KEYS = {
  ONBOARDING_COMPLETED: '@onboarding_completed',
  DISMISSED_BANNERS: '@dismissed_banners',
  PREFERRED_SPORTSBOOK: '@preferred_sportsbook',
  TUTORIAL_VIEWED: '@tutorial_viewed',
};

/**
 * Onboarding Preferences
 */
export const onboardingPreferences = {
  async hasCompletedOnboarding(): Promise<boolean> {
    try {
      const value = await AsyncStorage.getItem(KEYS.ONBOARDING_COMPLETED);
      return value === 'true';
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      return false;
    }
  },

  async setOnboardingCompleted(): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.ONBOARDING_COMPLETED, 'true');
    } catch (error) {
      console.error('Error setting onboarding completed:', error);
    }
  },

  async resetOnboarding(): Promise<void> {
    try {
      await AsyncStorage.removeItem(KEYS.ONBOARDING_COMPLETED);
    } catch (error) {
      console.error('Error resetting onboarding:', error);
    }
  },
};

/**
 * Help Banner Preferences
 */
export const bannerPreferences = {
  async isBannerDismissed(bannerId: string): Promise<boolean> {
    try {
      const dismissedBanners = await AsyncStorage.getItem(KEYS.DISMISSED_BANNERS);
      if (!dismissedBanners) return false;

      const banners: string[] = JSON.parse(dismissedBanners);
      return banners.includes(bannerId);
    } catch (error) {
      console.error('Error checking banner dismissed status:', error);
      return false;
    }
  },

  async dismissBanner(bannerId: string): Promise<void> {
    try {
      const dismissedBanners = await AsyncStorage.getItem(KEYS.DISMISSED_BANNERS);
      let banners: string[] = dismissedBanners ? JSON.parse(dismissedBanners) : [];

      if (!banners.includes(bannerId)) {
        banners.push(bannerId);
        await AsyncStorage.setItem(KEYS.DISMISSED_BANNERS, JSON.stringify(banners));
      }
    } catch (error) {
      console.error('Error dismissing banner:', error);
    }
  },

  async resetDismissedBanners(): Promise<void> {
    try {
      await AsyncStorage.removeItem(KEYS.DISMISSED_BANNERS);
    } catch (error) {
      console.error('Error resetting dismissed banners:', error);
    }
  },
};

/**
 * Sportsbook Preferences
 */
export const sportsbookPreferences = {
  async getPreferredSportsbook(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(KEYS.PREFERRED_SPORTSBOOK);
    } catch (error) {
      console.error('Error getting preferred sportsbook:', error);
      return null;
    }
  },

  async setPreferredSportsbook(sportsbook: string): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.PREFERRED_SPORTSBOOK, sportsbook);
    } catch (error) {
      console.error('Error setting preferred sportsbook:', error);
    }
  },
};

/**
 * Tutorial Preferences
 */
export const tutorialPreferences = {
  async hasTutorialBeenViewed(): Promise<boolean> {
    try {
      const value = await AsyncStorage.getItem(KEYS.TUTORIAL_VIEWED);
      return value === 'true';
    } catch (error) {
      console.error('Error checking tutorial viewed status:', error);
      return false;
    }
  },

  async setTutorialViewed(): Promise<void> {
    try {
      await AsyncStorage.setItem(KEYS.TUTORIAL_VIEWED, 'true');
    } catch (error) {
      console.error('Error setting tutorial viewed:', error);
    }
  },

  async resetTutorial(): Promise<void> {
    try {
      await AsyncStorage.removeItem(KEYS.TUTORIAL_VIEWED);
    } catch (error) {
      console.error('Error resetting tutorial:', error);
    }
  },
};

/**
 * Clear all preferences (useful for testing)
 */
export async function clearAllPreferences(): Promise<void> {
  try {
    await AsyncStorage.multiRemove(Object.values(KEYS));
  } catch (error) {
    console.error('Error clearing all preferences:', error);
  }
}
