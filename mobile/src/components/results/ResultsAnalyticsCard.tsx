/**
 * Results Analytics Card
 * Shows calibration analysis and performance by confidence tier — dark theme
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface ConfidenceTier {
  tier: string;
  min_confidence: number;
  max_confidence: number;
  count: number;
  wins: number;
  win_rate: number;
}

interface ResultsAnalyticsCardProps {
  confidenceTiers: ConfidenceTier[];
}

export default function ResultsAnalyticsCard({ confidenceTiers }: ResultsAnalyticsCardProps) {
  const getCalibrationColor = (predicted: number, actual: number): string => {
    const error = Math.abs(predicted - actual);
    if (error < 5) return theme.colors.success;
    if (error < 10) return theme.colors.warning;
    return theme.colors.danger;
  };

  const getCalibrationLabel = (predicted: number, actual: number): string => {
    const diff = actual - predicted;
    if (Math.abs(diff) < 5) return 'Well calibrated';
    if (diff > 0) return `+${diff.toFixed(0)}pp`;
    return `${diff.toFixed(0)}pp`;
  };

  const getPredictedConfidence = (tier: ConfidenceTier): number => {
    return (tier.min_confidence + tier.max_confidence) / 2;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Calibration Analysis</Text>
        <Text style={styles.subtitle}>Predicted vs Actual Win Rate</Text>
      </View>

      {confidenceTiers.filter(t => t.count > 0).length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Not enough data yet</Text>
        </View>
      ) : (
        <View style={styles.tiers}>
          {confidenceTiers
            .filter(tier => tier.count > 0)
            .map((tier, index) => {
              const predicted = getPredictedConfidence(tier);
              const actual = tier.win_rate;
              const calibrationColor = getCalibrationColor(predicted, actual);
              const calibrationLabel = getCalibrationLabel(predicted, actual);

              return (
                <View key={index} style={styles.tierRow}>
                  <View style={styles.tierInfo}>
                    <Text style={styles.tierLabel}>{tier.tier}% Confidence</Text>
                    <Text style={styles.tierCount}>
                      {tier.wins}/{tier.count} parlays
                    </Text>
                  </View>

                  <View style={styles.tierStats}>
                    <View style={styles.confidenceComparison}>
                      <View style={styles.comparisonRow}>
                        <Text style={styles.comparisonLabel}>Predicted:</Text>
                        <Text style={styles.comparisonValue}>
                          {predicted.toFixed(0)}%
                        </Text>
                      </View>
                      <View style={styles.comparisonRow}>
                        <Text style={styles.comparisonLabel}>Actual:</Text>
                        <Text style={[styles.comparisonValue, { fontWeight: '700' }]}>
                          {actual.toFixed(0)}%
                        </Text>
                      </View>
                    </View>

                    <View style={[styles.calibrationBadge, { backgroundColor: calibrationColor }]}>
                      <Text style={styles.calibrationText}>{calibrationLabel}</Text>
                    </View>
                  </View>
                </View>
              );
            })}
        </View>
      )}

      <View style={styles.explainer}>
        <Text style={styles.explainerText}>
          Calibration shows if the AI's confidence matches reality. A well-calibrated 80% confidence
          should win ~80% of the time.
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    ...theme.shadows.card,
  },
  header: {
    marginBottom: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  emptyState: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: theme.colors.textTertiary,
  },
  tiers: {
    gap: 12,
  },
  tierRow: {
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: theme.borderRadius.s,
    padding: 12,
    marginBottom: 8,
  },
  tierInfo: {
    marginBottom: 8,
  },
  tierLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  tierCount: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  tierStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  confidenceComparison: {
    flex: 1,
  },
  comparisonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  comparisonLabel: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  comparisonValue: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  calibrationBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginLeft: 12,
  },
  calibrationText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
    textAlign: 'center',
  },
  explainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  explainerText: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    lineHeight: 18,
  },
});
