/**
 * BetSizeSuggestion V2 — Kelly-based unit recommendation with ConfidenceGauge.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';
import GlassCard from '../common/GlassCard';
import ConfidenceGauge from '../charts/ConfidenceGauge';

interface BetSizeSuggestionProps {
  confidence: number;
  edgePct: number;
  suggestedUnits: number;
  riskLevel: 'low' | 'medium' | 'high';
  kellyPct?: number;
}

function getRiskColor(level: string): string {
  switch (level) {
    case 'low': return theme.colors.success;
    case 'medium': return theme.colors.gold;
    case 'high': return theme.colors.danger;
    default: return theme.colors.textSecondary;
  }
}

export default function BetSizeSuggestion({
  confidence,
  edgePct,
  suggestedUnits,
  riskLevel,
  kellyPct,
}: BetSizeSuggestionProps) {
  const riskColor = getRiskColor(riskLevel);

  return (
    <GlassCard>
      <Text style={styles.title}>BET SIZING</Text>

      <View style={styles.mainRow}>
        {/* Confidence Gauge */}
        <View style={styles.gaugeBox}>
          <ConfidenceGauge score={confidence} size="md" />
        </View>

        {/* Units recommendation */}
        <View style={styles.unitsBox}>
          <Text style={[styles.unitsValue, { color: riskColor }]}>
            {suggestedUnits.toFixed(1)}u
          </Text>
          <Text style={styles.unitsLabel}>Suggested</Text>
        </View>

        {/* Stats */}
        <View style={styles.statsCol}>
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Edge</Text>
            <Text style={[styles.statValue, { color: edgePct > 5 ? theme.colors.success : theme.colors.textPrimary }]}>
              +{edgePct.toFixed(1)}%
            </Text>
          </View>
          {kellyPct != null && (
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Kelly</Text>
              <Text style={styles.statValue}>{kellyPct.toFixed(1)}%</Text>
            </View>
          )}
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Risk</Text>
            <View style={[styles.riskBadge, { backgroundColor: riskColor + '1A' }]}>
              <Text style={[styles.riskText, { color: riskColor }]}>
                {riskLevel.toUpperCase()}
              </Text>
            </View>
          </View>
        </View>
      </View>

      <Text style={styles.disclaimer}>
        Based on quarter-Kelly criterion. Never exceed 3% of bankroll on a single bet.
      </Text>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  title: {
    ...theme.typography.caption,
    marginBottom: 12,
  },
  mainRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  gaugeBox: {
    marginRight: 12,
  },
  unitsBox: {
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: theme.borderRadius.m,
    padding: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
    minWidth: 64,
  },
  unitsValue: {
    fontSize: 24,
    fontWeight: '800',
  },
  unitsLabel: {
    fontSize: 9,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    marginTop: 2,
    textTransform: 'uppercase',
  },
  statsCol: {
    flex: 1,
    gap: 4,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  statValue: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  riskBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  riskText: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  disclaimer: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
    textAlign: 'center',
  },
});
