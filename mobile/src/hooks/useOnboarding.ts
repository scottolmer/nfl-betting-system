/**
 * useOnboarding Hook
 * Custom hook for managing onboarding state
 */

import { useState, useEffect } from 'react';
import { onboardingPreferences } from '../services/userPreferences';

interface UseOnboardingReturn {
  isLoading: boolean;
  showOnboarding: boolean;
  completeOnboarding: () => Promise<void>;
  resetOnboarding: () => Promise<void>;
}

export function useOnboarding(): UseOnboardingReturn {
  const [isLoading, setIsLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      const hasCompleted = await onboardingPreferences.hasCompletedOnboarding();
      setShowOnboarding(!hasCompleted);
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      setShowOnboarding(false);
    } finally {
      setIsLoading(false);
    }
  };

  const completeOnboarding = async () => {
    try {
      await onboardingPreferences.setOnboardingCompleted();
      setShowOnboarding(false);
    } catch (error) {
      console.error('Error completing onboarding:', error);
    }
  };

  const resetOnboarding = async () => {
    try {
      await onboardingPreferences.resetOnboarding();
      // Don't immediately show onboarding, just reset the flag
      // It will show on next app launch
    } catch (error) {
      console.error('Error resetting onboarding:', error);
    }
  };

  return {
    isLoading,
    showOnboarding,
    completeOnboarding,
    resetOnboarding,
  };
}
