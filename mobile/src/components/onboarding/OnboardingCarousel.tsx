/**
 * Onboarding Carousel
 * 3-screen swipeable tutorial shown on first app launch
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
        <Text style={styles.largeIcon}>🏈</Text>
      </View>

      <Text style={styles.title}>{title}</Text>
      <Text style={styles.subtitle}>{subtitle}</Text>
      <Text style={styles.description}>{description}</Text>

      <View style={styles.featureList}>
        <FeatureItem icon="🤖" text="9 specialized AI agents" />
        <FeatureItem icon="📊" text="Advanced analytics & projections" />
        <FeatureItem icon="🎯" text="Optimized for DraftKings Pick 6" />
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
            <Text style={styles.optionIcon}>{option.icon}</Text>
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
          <View key={index} style={styles.tierCard}>
            <View style={styles.tierHeader}>
              <Text style={styles.tierEmoji}>{tier.emoji}</Text>
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

function FeatureItem({ icon, text }: { icon: string; text: string }) {
  return (
    <View style={styles.featureItem}>
      <Text style={styles.featureIcon}>{icon}</Text>
      <Text style={styles.featureText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1F2937',
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
  largeIcon: {
    fontSize: 80,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#3B82F6',
    textAlign: 'center',
    fontWeight: '600',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: '#D1D5DB',
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
    backgroundColor: '#374151',
    padding: 16,
    borderRadius: 12,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#FFFFFF',
    fontWeight: '500',
  },
  optionsList: {
    marginTop: 24,
    gap: 16,
  },
  optionCard: {
    flexDirection: 'row',
    backgroundColor: '#374151',
    padding: 20,
    borderRadius: 12,
    alignItems: 'flex-start',
  },
  optionIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  optionContent: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  optionDescription: {
    fontSize: 14,
    color: '#D1D5DB',
    lineHeight: 20,
  },
  tiersList: {
    marginTop: 24,
    gap: 12,
  },
  tierCard: {
    backgroundColor: '#374151',
    padding: 16,
    borderRadius: 12,
  },
  tierHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tierEmoji: {
    fontSize: 32,
    marginRight: 12,
  },
  tierInfo: {
    flex: 1,
  },
  tierRange: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  tierLabel: {
    fontSize: 16,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  tierDescription: {
    fontSize: 14,
    color: '#D1D5DB',
    lineHeight: 20,
    marginLeft: 44,
  },
  footer: {
    fontSize: 13,
    color: '#9CA3AF',
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
    backgroundColor: '#3B82F6',
    width: 24,
  },
  dotInactive: {
    backgroundColor: '#4B5563',
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
    color: '#9CA3AF',
    fontSize: 16,
    fontWeight: '600',
  },
  nextButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
  },
  nextText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
