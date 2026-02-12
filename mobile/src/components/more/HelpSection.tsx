/**
 * Help Section Component
 * Help & Learning resources for the More screen — dark theme
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../../constants/theme';

interface HelpSectionProps {
  onViewTutorial: () => void;
  onResetTutorial: () => void;
}

export default function HelpSection({
  onViewTutorial,
  onResetTutorial,
}: HelpSectionProps) {
  const helpItems = [
    {
      title: 'View Tutorial',
      description: 'Revisit the onboarding guide',
      action: onViewTutorial,
    },
    {
      title: 'Understanding Confidence',
      description: 'Learn how AI scores are calculated',
    },
    {
      title: 'How to Build Parlays',
      description: 'Tips for creating winning combinations',
    },
    {
      title: 'Reading Projections',
      description: 'What projections and cushions mean',
    },
  ];

  const settingsItems = [
    {
      title: 'Reset Tutorial',
      description: 'See the onboarding guide again on next launch',
      action: onResetTutorial,
    },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Help & Learning</Text>
        <View style={styles.itemsContainer}>
          {helpItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.item}
              onPress={item.action}
            >
              <View style={styles.itemContent}>
                <Text style={styles.itemTitle}>{item.title}</Text>
                <Text style={styles.itemDescription}>{item.description}</Text>
              </View>
              <Text style={styles.itemArrow}>{'\u203A'}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tutorial Settings</Text>
        <View style={styles.itemsContainer}>
          {settingsItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.item}
              onPress={item.action}
            >
              <View style={styles.itemContent}>
                <Text style={styles.itemTitle}>{item.title}</Text>
                <Text style={styles.itemDescription}>{item.description}</Text>
              </View>
              <Text style={styles.itemArrow}>{'\u203A'}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.tipsBox}>
        <Text style={styles.tipsTitle}>Quick Tips</Text>
        <Text style={styles.tipsText}>
          {'\u2022'} Tap the [?] icon anywhere for explanations{'\n'}
          {'\u2022'} 80+ confidence = Elite picks with high conviction{'\n'}
          {'\u2022'} Use 2-3 leg parlays for better hit rates{'\n'}
          {'\u2022'} Adjust lines to match your sportsbook's odds
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  itemsContainer: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    marginHorizontal: 16,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    overflow: 'hidden',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  itemContent: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  itemDescription: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
  },
  itemArrow: {
    fontSize: 24,
    color: theme.colors.textTertiary,
    marginLeft: 12,
  },
  tipsBox: {
    backgroundColor: theme.colors.warningMuted,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.warning,
    borderRadius: theme.borderRadius.s,
    padding: 16,
    marginHorizontal: 16,
  },
  tipsTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.warning,
    marginBottom: 8,
  },
  tipsText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
});
