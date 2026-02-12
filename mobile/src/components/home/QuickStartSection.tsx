/**
 * Quick Start Section
 * Hero section on Home screen with featured pick and clear CTAs — dark theme
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../../constants/theme';
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
    if (confidence >= 70) return theme.colors.primary;
    if (confidence >= 60) return theme.colors.success;
    return theme.colors.textSecondary;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Quick Start</Text>

      {featuredProp ? (
        <TouchableOpacity
          style={styles.featuredCard}
          onPress={onFeaturedPress}
          activeOpacity={0.8}
        >
          <View style={styles.featuredHeader}>
            <Text style={styles.featuredBadge}>TOP PICK</Text>
            <Text
              style={[
                styles.confidenceScore,
                { color: getConfidenceColor(featuredProp.confidence) },
              ]}
            >
              {Math.round(featuredProp.confidence)}
            </Text>
          </View>

          <Text style={styles.playerName}>{featuredProp.player_name}</Text>
          <Text style={styles.matchup}>
            {featuredProp.team} {featuredProp.position} vs {featuredProp.opponent}
          </Text>

          <View style={styles.propLine}>
            <Text style={styles.statType}>{featuredProp.stat_type}</Text>
            <Text style={[styles.betType, { color: featuredProp.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger }]}>
              {featuredProp.bet_type}
            </Text>
            <Text style={styles.line}>{featuredProp.line}</Text>
          </View>

          {featuredProp.top_reasons && featuredProp.top_reasons[0] && (
            <Text style={styles.topReason} numberOfLines={2}>
              {featuredProp.top_reasons[0]}
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
          <Text style={styles.ctaTextPrimary}>View Pre-Built</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.ctaButton, styles.ctaSecondary]}
          onPress={onBuildCustom}
        >
          <Text style={styles.ctaTextSecondary}>Build Custom</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.background,
    padding: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 12,
  },
  featuredCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorderActive,
    padding: 20,
    marginBottom: 16,
    ...theme.shadows.glow,
  },
  featuredHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  featuredBadge: {
    fontSize: 11,
    fontWeight: '800',
    color: theme.colors.gold,
    letterSpacing: 0.5,
  },
  confidenceScore: {
    fontSize: 24,
    fontWeight: '800',
  },
  playerName: {
    fontSize: 22,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  matchup: {
    fontSize: 14,
    color: theme.colors.textSecondary,
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
    color: theme.colors.textPrimary,
  },
  betType: {
    fontSize: 15,
    fontWeight: '800',
  },
  line: {
    fontSize: 18,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  topReason: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
    marginBottom: 12,
  },
  tapHint: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
    textAlign: 'center',
  },
  noFeaturedText: {
    fontSize: 14,
    color: theme.colors.textTertiary,
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
    borderRadius: theme.borderRadius.s,
    gap: 8,
  },
  ctaPrimary: {
    backgroundColor: theme.colors.primary,
  },
  ctaSecondary: {
    backgroundColor: theme.colors.backgroundElevated,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
  },
  ctaTextPrimary: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000',
  },
  ctaTextSecondary: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
});
