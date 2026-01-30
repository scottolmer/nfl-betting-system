/**
 * Quick Start Section
 * Hero section on Home screen with featured pick and clear CTAs
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { PropAnalysis } from '../../types';

interface QuickStartSectionProps {
  featuredProp?: PropAnalysis;
  onViewPreBuilt: () => void;
  onBuildCustom: () => void;
  onFeaturedPress?: () => void;
}

export default function QuickStartSection({
  featuredProp,
  onViewPreBuilt,
  onBuildCustom,
  onFeaturedPress,
}: QuickStartSectionProps) {
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return '#22C55E';
    if (confidence >= 75) return '#F59E0B';
    if (confidence >= 70) return '#3B82F6';
    return '#6B7280';
  };

  const getConfidenceEmoji = (confidence: number): string => {
    if (confidence >= 80) return '🔥';
    if (confidence >= 75) return '⭐';
    if (confidence >= 70) return '✅';
    return '📊';
  };

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>🎯 Quick Start</Text>

      {featuredProp ? (
        <TouchableOpacity
          style={styles.featuredCard}
          onPress={onFeaturedPress}
          activeOpacity={0.8}
        >
          <View style={styles.featuredHeader}>
            <Text style={styles.featuredBadge}>TODAY'S TOP PICK</Text>
            <View style={styles.confidenceContainer}>
              <Text style={styles.confidenceEmoji}>
                {getConfidenceEmoji(featuredProp.confidence)}
              </Text>
              <Text
                style={[
                  styles.confidenceScore,
                  { color: getConfidenceColor(featuredProp.confidence) },
                ]}
              >
                {Math.round(featuredProp.confidence)}
              </Text>
            </View>
          </View>

          <Text style={styles.playerName}>{featuredProp.player_name}</Text>
          <Text style={styles.matchup}>
            {featuredProp.team} {featuredProp.position} vs {featuredProp.opponent}
          </Text>

          <View style={styles.propLine}>
            <Text style={styles.statType}>{featuredProp.stat_type}</Text>
            <Text style={styles.betType}>{featuredProp.bet_type}</Text>
            <Text style={styles.line}>{featuredProp.line}</Text>
          </View>

          {featuredProp.top_reasons && featuredProp.top_reasons[0] && (
            <Text style={styles.topReason} numberOfLines={2}>
              💡 {featuredProp.top_reasons[0]}
            </Text>
          )}

          <Text style={styles.tapHint}>Tap to see full analysis</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.featuredCard}>
          <Text style={styles.noFeaturedText}>
            Loading today's top pick...
          </Text>
        </View>
      )}

      <View style={styles.ctaContainer}>
        <TouchableOpacity
          style={[styles.ctaButton, styles.ctaPrimary]}
          onPress={onViewPreBuilt}
        >
          <Text style={styles.ctaIcon}>🎰</Text>
          <Text style={styles.ctaTextPrimary}>View Pre-Built</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.ctaButton, styles.ctaSecondary]}
          onPress={onBuildCustom}
        >
          <Text style={styles.ctaIcon}>⚡</Text>
          <Text style={styles.ctaTextSecondary}>Build Custom</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  featuredCard: {
    backgroundColor: '#1F2937',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  featuredHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  featuredBadge: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#FCD34D',
    letterSpacing: 0.5,
  },
  confidenceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  confidenceEmoji: {
    fontSize: 20,
  },
  confidenceScore: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  playerName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  matchup: {
    fontSize: 14,
    color: '#9CA3AF',
    marginBottom: 12,
  },
  propLine: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  statType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  betType: {
    fontSize: 15,
    fontWeight: '600',
    color: '#3B82F6',
  },
  line: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  topReason: {
    fontSize: 13,
    color: '#D1D5DB',
    lineHeight: 18,
    marginBottom: 12,
  },
  tapHint: {
    fontSize: 12,
    color: '#6B7280',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  noFeaturedText: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
  },
  ctaContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  ctaButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    gap: 8,
  },
  ctaPrimary: {
    backgroundColor: '#3B82F6',
  },
  ctaSecondary: {
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  ctaIcon: {
    fontSize: 18,
  },
  ctaTextPrimary: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  ctaTextSecondary: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
  },
});
