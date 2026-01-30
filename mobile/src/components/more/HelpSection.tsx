/**
 * Help Section Component
 * Help & Learning resources for the More screen
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

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
      icon: '📖',
      title: 'View Tutorial',
      description: 'Revisit the onboarding guide',
      action: onViewTutorial,
    },
    {
      icon: '❓',
      title: 'Understanding Confidence',
      description: 'Learn how AI scores are calculated',
      tooltip: 'confidence',
    },
    {
      icon: '🎯',
      title: 'How to Build Parlays',
      description: 'Tips for creating winning combinations',
      tooltip: 'parlays',
    },
    {
      icon: '🔢',
      title: 'Reading Projections',
      description: 'What projections and cushions mean',
      tooltip: 'projection',
    },
  ];

  const settingsItems = [
    {
      icon: '🔄',
      title: 'Reset Tutorial',
      description: 'See the onboarding guide again on next launch',
      action: onResetTutorial,
    },
  ];

  return (
    <View style={styles.container}>
      {/* Help & Learning Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Help & Learning</Text>
        <View style={styles.itemsContainer}>
          {helpItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.item}
              onPress={item.action}
            >
              <View style={styles.itemLeft}>
                <Text style={styles.itemIcon}>{item.icon}</Text>
                <View style={styles.itemContent}>
                  <Text style={styles.itemTitle}>{item.title}</Text>
                  <Text style={styles.itemDescription}>{item.description}</Text>
                </View>
              </View>
              <Text style={styles.itemArrow}>›</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Settings Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tutorial Settings</Text>
        <View style={styles.itemsContainer}>
          {settingsItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={styles.item}
              onPress={item.action}
            >
              <View style={styles.itemLeft}>
                <Text style={styles.itemIcon}>{item.icon}</Text>
                <View style={styles.itemContent}>
                  <Text style={styles.itemTitle}>{item.title}</Text>
                  <Text style={styles.itemDescription}>{item.description}</Text>
                </View>
              </View>
              <Text style={styles.itemArrow}>›</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Quick Tips */}
      <View style={styles.tipsBox}>
        <Text style={styles.tipsTitle}>💡 Quick Tips</Text>
        <Text style={styles.tipsText}>
          • Tap the [?] icon anywhere in the app for explanations{'\n'}
          • 80+ confidence = Elite picks with high conviction{'\n'}
          • Use 2-3 leg parlays for better hit rates{'\n'}
          • Adjust lines to match your sportsbook's odds
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
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  itemsContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginHorizontal: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  itemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  itemIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  itemContent: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  itemDescription: {
    fontSize: 13,
    color: '#6B7280',
    lineHeight: 18,
  },
  itemArrow: {
    fontSize: 24,
    color: '#9CA3AF',
    marginLeft: 12,
  },
  tipsBox: {
    backgroundColor: '#FEF3C7',
    borderLeftWidth: 4,
    borderLeftColor: '#F59E0B',
    borderRadius: 8,
    padding: 16,
    marginHorizontal: 16,
  },
  tipsTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#92400E',
    marginBottom: 8,
  },
  tipsText: {
    fontSize: 13,
    color: '#78350F',
    lineHeight: 20,
  },
});
