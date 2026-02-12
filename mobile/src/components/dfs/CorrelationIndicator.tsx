/**
 * CorrelationIndicator — Visual green/yellow/red correlation gauge.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface CorrelationIndicatorProps {
  penalty: number;       // e.g. -7.5
  riskLevel: 'low' | 'medium' | 'high';
  warnings?: string[];
  compact?: boolean;
}

function getRiskColor(risk: string): string {
  switch (risk) {
    case 'low': return theme.colors.success;
    case 'medium': return theme.colors.gold;
    case 'high': return theme.colors.danger;
    default: return theme.colors.textSecondary;
  }
}

function getGaugeWidth(penalty: number): number {
  // Map penalty from 0 to -20 → gauge 0% to 100%
  return Math.min(Math.abs(penalty) / 20 * 100, 100);
}

export default function CorrelationIndicator({
  penalty,
  riskLevel,
  warnings,
  compact,
}: CorrelationIndicatorProps) {
  const color = getRiskColor(riskLevel);
  const gaugeWidth = getGaugeWidth(penalty);

  if (compact) {
    return (
      <View style={styles.compactRow}>
        <View style={[styles.dot, { backgroundColor: color }]} />
        <Text style={[styles.compactLabel, { color }]}>
          {riskLevel.toUpperCase()}
        </Text>
        {penalty < 0 && (
          <Text style={styles.compactPenalty}>{penalty.toFixed(1)}%</Text>
        )}
      </View>
    );
  }

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>Correlation Risk</Text>
        <Text style={[styles.riskBadge, { color }]}>{riskLevel.toUpperCase()}</Text>
      </View>

      {/* Gauge bar */}
      <View style={styles.gaugeTrack}>
        <View style={[styles.gaugeFill, { width: `${gaugeWidth}%`, backgroundColor: color }]} />
      </View>

      {penalty < 0 && (
        <Text style={styles.penaltyText}>
          {penalty.toFixed(1)}% confidence penalty applied
        </Text>
      )}

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <View style={styles.warnings}>
          {warnings.map((w, i) => (
            <Text key={i} style={styles.warning} numberOfLines={2}>
              {w}
            </Text>
          ))}
        </View>
      )}
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  title: {
    ...theme.typography.caption,
  },
  riskBadge: {
    fontSize: 12,
    fontWeight: '800',
  },
  gaugeTrack: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 6,
  },
  gaugeFill: {
    height: 6,
    borderRadius: 3,
  },
  penaltyText: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginBottom: 6,
  },
  warnings: {
    marginTop: 6,
    gap: 4,
  },
  warning: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    lineHeight: 16,
  },
  // Compact mode
  compactRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  compactLabel: {
    fontSize: 11,
    fontWeight: '700',
  },
  compactPenalty: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
});
