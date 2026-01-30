/**
 * Coming Soon Card
 * Placeholder for Results screen with upcoming features
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface ComingSoonCardProps {
  onNavigateToMyParlays?: () => void;
}

export default function ComingSoonCard({ onNavigateToMyParlays }: ComingSoonCardProps) {
  const upcomingFeatures = [
    {
      icon: '✅',
      title: 'Auto-graded Results',
      description: 'Automatic result tracking from ESPN',
    },
    {
      icon: '📊',
      title: 'Win Rate Analytics',
      description: 'Track your success rate by confidence tier',
    },
    {
      icon: '🔍',
      title: 'Why It Hit/Miss Analysis',
      description: 'AI explains what went right or wrong',
    },
    {
      icon: '📈',
      title: 'Performance Trends',
      description: 'See your betting patterns over time',
    },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>📈</Text>
        <Text style={styles.headerTitle}>Results Tracking Coming Soon!</Text>
      </View>

      <Text style={styles.description}>
        We're building powerful results tracking features to help you analyze your
        betting performance and improve over time.
      </Text>

      <View style={styles.featuresSection}>
        <Text style={styles.featuresTitle}>What's Coming:</Text>
        {upcomingFeatures.map((feature, index) => (
          <View key={index} style={styles.featureItem}>
            <Text style={styles.featureIcon}>{feature.icon}</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDescription}>{feature.description}</Text>
            </View>
          </View>
        ))}
      </View>

      <View style={styles.currentStateSection}>
        <View style={styles.infoBox}>
          <Text style={styles.infoIcon}>💡</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>For Now:</Text>
            <Text style={styles.infoText}>
              Mark parlays as "Placed" in My Parlays to keep track of what you've bet.
              Full auto-grading is coming in the next update!
            </Text>
          </View>
        </View>

        {onNavigateToMyParlays && (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={onNavigateToMyParlays}
          >
            <Text style={styles.actionButtonText}>View My Parlays →</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Want to help prioritize features? Share your feedback in the More tab!
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 16,
    marginTop: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    alignItems: 'center',
    marginBottom: 16,
  },
  headerIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1F2937',
    textAlign: 'center',
  },
  description: {
    fontSize: 15,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  featuresSection: {
    marginBottom: 24,
  },
  featuresTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  featureDescription: {
    fontSize: 13,
    color: '#6B7280',
    lineHeight: 18,
  },
  currentStateSection: {
    marginBottom: 16,
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  infoIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 13,
    color: '#4B5563',
    lineHeight: 18,
  },
  actionButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingTop: 16,
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 18,
  },
});
