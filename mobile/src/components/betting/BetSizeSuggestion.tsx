/**
 * BetSizeSuggestion — Kelly-based unit recommendation display.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

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
    <View style={styles.card}>
      <Text style={styles.title}>Bet Sizing</Text>

      <View style={styles.mainRow}>
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
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Confidence</Text>
            <Text style={styles.statValue}>{Math.round(confidence)}</Text>
          </View>
          {kellyPct != null && (
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Kelly (1/4)</Text>
              <Text style={styles.statValue}>{kellyPct.toFixed(1)}%</Text>
            </View>
          )}
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Risk</Text>
            <Text style={[styles.statValue, { color: riskColor, textTransform: 'capitalize' }]}>
              {riskLevel}
            </Text>
          </View>
        </View>
      </View>

      <Text style={styles.disclaimer}>
        Based on quarter-Kelly criterion. Never exceed 3% of bankroll on a single bet.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
  },
  title: {
    ...theme.typography.caption,
    marginBottom: 12,
  },
  mainRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  unitsBox: {
    backgroundColor: theme.colors.glassHigh,
    borderRadius: theme.borderRadius.m,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
    minWidth: 80,
  },
  unitsValue: {
    fontSize: 28,
    fontWeight: '800',
  },
  unitsLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    marginTop: 2,
  },
  statsCol: {
    flex: 1,
    gap: 4,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
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
  disclaimer: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
    textAlign: 'center',
  },
});
