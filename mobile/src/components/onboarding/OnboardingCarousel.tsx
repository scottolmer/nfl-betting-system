/**
 * Onboarding Carousel
 * 3-screen swipeable tutorial shown on first app launch — dark theme
 */

import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Dimensions,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { theme } from '../../constants/theme';
import { ONBOARDING_CONTENT } from '../../constants/tooltips';
import { onboardingPreferences } from '../../services/userPreferences';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface OnboardingCarouselProps {
  onComplete: () => void;
}

export default function OnboardingCarousel({ onComplete }: OnboardingCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const screens = [
    {
      id: 'welcome',
      content: ONBOARDING_CONTENT.welcome,
      render: () => <WelcomeScreen />,
    },
    {
      id: 'how-it-works',
      content: ONBOARDING_CONTENT.howItWorks,
      render: () => <HowItWorksScreen />,
    },
    {
      id: 'confidence',
      content: ONBOARDING_CONTENT.confidenceSystem,
      render: () => <ConfidenceScreen />,
    },
  ];

  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const scrollPosition = event.nativeEvent.contentOffset.x;
    const index = Math.round(scrollPosition / SCREEN_WIDTH);
    setCurrentIndex(index);
  };

  const handleNext = () => {
    if (currentIndex < screens.length - 1) {
      flatListRef.current?.scrollToIndex({
        index: currentIndex + 1,
        animated: true,
      });
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = async () => {
    await onboardingPreferences.setOnboardingCompleted();
    onComplete();
  };

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={screens}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onScroll={handleScroll}
        scrollEventThrottle={16}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.screenContainer}>{item.render()}</View>
        )}
        getItemLayout={(data, index) => ({
          length: SCREEN_WIDTH,
          offset: SCREEN_WIDTH * index,
          index,
        })}
      />

      {/* Pagination Dots */}
      <View style={styles.pagination}>
        {screens.map((_, index) => (
          <View
            key={index}
            style={[
              styles.dot,
              index === currentIndex ? styles.dotActive : styles.dotInactive,
            ]}
          />
        ))}
      </View>

      {/* Navigation Buttons */}
      <View style={styles.navigation}>
        <TouchableOpacity onPress={handleSkip} style={styles.skipButton}>
          <Text style={styles.skipText}>Skip</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={handleNext} style={styles.nextButton}>
          <Text style={styles.nextText}>
            {currentIndex === screens.length - 1 ? "Get Started" : "Next"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

function WelcomeScreen() {
  const { title, subtitle, description } = ONBOARDING_CONTENT.welcome;

  return (
    <View style={styles.screen}>
      <View style={styles.iconContainer}>
        <View style={styles.iconCircle}>
          <Text style={styles.iconText}>P6</Text>
        </View>
      </View>

      <Text style={styles.title}>{title}</Text>
      <Text style={styles.subtitle}>{subtitle}</Text>
      <Text style={styles.description}>{description}</Text>

      <View style={styles.featureList}>
        <FeatureItem label="AI" text="6 specialized AI agents" />
        <FeatureItem label="DATA" text="Advanced analytics & projections" />
        <FeatureItem label="DK" text="Optimized for DraftKings Pick 6" />
      </View>
    </View>
  );
}

function HowItWorksScreen() {
  const { title, options } = ONBOARDING_CONTENT.howItWorks;

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>{title}</Text>

      <View style={styles.optionsList}>
        {options.map((option, index) => (
          <View key={index} style={styles.optionCard}>
            <View style={styles.optionIconCircle}>
              <Text style={styles.optionIconText}>{index + 1}</Text>
            </View>
            <View style={styles.optionContent}>
              <Text style={styles.optionTitle}>{option.title}</Text>
              <Text style={styles.optionDescription}>{option.description}</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  );
}

function ConfidenceScreen() {
  const { title, tiers, footer } = ONBOARDING_CONTENT.confidenceSystem;

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>{title}</Text>

      <View style={styles.tiersList}>
        {tiers.map((tier, index) => (
          <View key={index} style={[styles.tierCard, { borderLeftColor: tier.color }]}>
            <View style={styles.tierHeader}>
              <View style={styles.tierInfo}>
                <Text style={[styles.tierRange, { color: tier.color }]}>
                  {tier.range}%
                </Text>
                <Text style={styles.tierLabel}>{tier.label}</Text>
              </View>
            </View>
            <Text style={styles.tierDescription}>{tier.description}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.footer}>{footer}</Text>
    </View>
  );
}

function FeatureItem({ label, text }: { label: string; text: string }) {
  return (
    <View style={styles.featureItem}>
      <View style={styles.featureLabelBox}>
        <Text style={styles.featureLabelText}>{label}</Text>
      </View>
      <Text style={styles.featureText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  screenContainer: {
    width: SCREEN_WIDTH,
  },
  screen: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: theme.colors.primaryMuted,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  iconText: {
    fontSize: 28,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: theme.colors.textPrimary,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: theme.colors.primary,
    textAlign: 'center',
    fontWeight: '600',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  featureList: {
    gap: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    borderRadius: theme.borderRadius.m,
  },
  featureLabelBox: {
    backgroundColor: theme.colors.primaryMuted,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    marginRight: 12,
  },
  featureLabelText: {
    fontSize: 11,
    fontWeight: '800',
    color: theme.colors.primary,
    letterSpacing: 0.5,
  },
  featureText: {
    fontSize: 16,
    color: theme.colors.textPrimary,
    fontWeight: '500',
  },
  optionsList: {
    marginTop: 24,
    gap: 16,
  },
  optionCard: {
    flexDirection: 'row',
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 20,
    borderRadius: theme.borderRadius.m,
    alignItems: 'flex-start',
  },
  optionIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: theme.colors.primaryMuted,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  optionIconText: {
    fontSize: 16,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  optionContent: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  optionDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  tiersList: {
    marginTop: 24,
    gap: 12,
  },
  tierCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderLeftWidth: 4,
    padding: 16,
    borderRadius: theme.borderRadius.m,
  },
  tierHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tierInfo: {
    flex: 1,
  },
  tierRange: {
    fontSize: 20,
    fontWeight: '800',
  },
  tierLabel: {
    fontSize: 16,
    color: theme.colors.textPrimary,
    fontWeight: '600',
  },
  tierDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  footer: {
    fontSize: 13,
    color: theme.colors.textTertiary,
    textAlign: 'center',
    marginTop: 24,
    lineHeight: 20,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingVertical: 20,
    gap: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  dotActive: {
    backgroundColor: theme.colors.primary,
    width: 24,
  },
  dotInactive: {
    backgroundColor: theme.colors.backgroundElevated,
  },
  navigation: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  skipButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  skipText: {
    color: theme.colors.textTertiary,
    fontSize: 16,
    fontWeight: '600',
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: theme.borderRadius.s,
  },
  nextText: {
    color: '#000',
    fontSize: 16,
    fontWeight: '700',
  },
});
