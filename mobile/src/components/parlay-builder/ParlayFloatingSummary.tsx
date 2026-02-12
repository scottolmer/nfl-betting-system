/**
 * Parlay Floating Summary
 * Always-visible summary showing current parlay state during creation
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SavedParlayLeg } from '../../types';
import InfoTooltip from '../common/InfoTooltip';
import { theme } from '../../constants/theme';

interface ParlayFloatingSummaryProps {
  legs: SavedParlayLeg[];
  combinedConfidence: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  maxLegs?: number;
}

export default function ParlayFloatingSummary({
  legs,
  combinedConfidence,
  riskLevel,
  maxLegs = 6,
}: ParlayFloatingSummaryProps) {
  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'LOW':
        return theme.colors.success;
      case 'MEDIUM':
        return theme.colors.warning;
      case 'HIGH':
        return theme.colors.danger;
      default:
        return theme.colors.textSecondary;
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 70) return theme.colors.success;
    if (confidence >= 60) return theme.colors.warning;
    return theme.colors.danger;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Parlay</Text>
        {legs.length > 0 && (
          <View style={styles.badges}>
            <View
              style={[
                styles.badge,
                { backgroundColor: getConfidenceColor(combinedConfidence) },
              ]}
            >
              <Text style={styles.badgeText}>{Math.round(combinedConfidence)}%</Text>
            </View>
            <View
              style={[
                styles.badge,
                { backgroundColor: getRiskColor(riskLevel) },
              ]}
            >
              <Text style={styles.badgeText}>{riskLevel}</Text>
            </View>
          </View>
        )}
      </View>

      <View style={styles.content}>
        {legs.length === 0 ? (
          <Text style={styles.emptyText}>No legs added yet</Text>
        ) : (
          <>
            <View style={styles.legCountRow}>
              <View style={styles.legCountLeft}>
                <Text style={styles.legCountText}>
                  {legs.length} / {maxLegs} legs
                </Text>
                {legs.length >= 2 && legs.length <= maxLegs && (
                  <Text style={styles.validIndicator}>✓ Valid parlay</Text>
                )}
                {legs.length < 2 && (
                  <Text style={styles.invalidIndicator}>Need at least 2 legs</Text>
                )}
                {legs.length > maxLegs && (
                  <Text style={styles.invalidIndicator}>Max {maxLegs} legs</Text>
                )}
              </View>
              <View style={styles.confidenceRow}>
                <Text style={styles.confidenceLabel}>Combined:</Text>
                <InfoTooltip tooltipKey="combinedConfidence" iconSize={12} />
              </View>
            </View>

            <View style={styles.legsPreview}>
              {legs.slice(0, 3).map((leg, index) => (
                <Text key={index} style={styles.legPreview} numberOfLines={1}>
                  {index + 1}. {leg.player_name} - {leg.stat_type}
                </Text>
              ))}
              {legs.length > 3 && (
                <Text style={styles.moreLegText}>+ {legs.length - 3} more...</Text>
              )}
            </View>
          </>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundElevated,
    marginHorizontal: 16,
    marginVertical: 12,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
  },
  badges: {
    flexDirection: 'row',
    gap: 6,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  content: {
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    paddingTop: 12,
  },
  emptyText: {
    fontSize: 14,
    color: theme.colors.textTertiary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  legCountRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  legCountLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  legCountText: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  validIndicator: {
    fontSize: 12,
    color: theme.colors.success,
    fontWeight: '500',
  },
  invalidIndicator: {
    fontSize: 12,
    color: theme.colors.warning,
    fontWeight: '500',
  },
  confidenceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  confidenceLabel: {
    fontSize: 12,
    color: theme.colors.textTertiary,
  },
  legsPreview: {
    gap: 4,
  },
  legPreview: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  moreLegText: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
    marginTop: 2,
  },
});
