import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';
import OnboardingCarousel from './src/components/onboarding/OnboardingCarousel';
import { useOnboarding } from './src/hooks/useOnboarding';
import { analytics, AnalyticsEvent } from './src/utils/analytics';
import { AuthProvider } from './src/contexts/AuthContext';
import { ModeProvider } from './src/contexts/ModeContext';

export default function App() {
  const { isLoading, showOnboarding, completeOnboarding } = useOnboarding();

  useEffect(() => {
    analytics.track(AnalyticsEvent.APP_OPENED);
  }, []);

  const handleOnboardingComplete = async () => {
    await completeOnboarding();
    analytics.trackOnboardingCompleted(3);
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  return (
    <AuthProvider>
      <ModeProvider>
        {showOnboarding ? (
          <OnboardingCarousel onComplete={handleOnboardingComplete} />
        ) : (
          <AppNavigator />
        )}
        <StatusBar style="light" />
      </ModeProvider>
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1F2937',
  },
});
