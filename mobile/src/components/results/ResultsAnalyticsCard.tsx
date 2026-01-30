/**
 * Results Analytics Card
 * Shows calibration analysis and performance by confidence tier
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

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
    if (error < 5) return '#10B981'; // Green - well calibrated
    if (error < 10) return '#F59E0B'; // Yellow - okay calibration
    return '#EF4444'; // Red - poor calibration
  };

  const getCalibrationLabel = (predicted: number, actual: number): string => {
    const diff = actual - predicted;
    if (Math.abs(diff) < 5) return 'Well calibrated';
    if (diff > 0) return `+${diff.toFixed(0)}pp`;
    return `${diff.toFixed(0)}pp`;
  };

  // Get average of min/max for predicted confidence
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
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  header: {
    marginBottom: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: '#6B7280',
  },
  emptyState: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  tiers: {
    gap: 12,
  },
  tierRow: {
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  tierInfo: {
    marginBottom: 8,
  },
  tierLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2,
  },
  tierCount: {
    fontSize: 13,
    color: '#6B7280',
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
    color: '#6B7280',
  },
  comparisonValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
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
    borderTopColor: '#E5E7EB',
  },
  explainerText: {
    fontSize: 12,
    color: '#6B7280',
    lineHeight: 18,
  },
});
