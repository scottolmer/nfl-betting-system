/**
 * StatTrendRow V2 — SVG sparkline replaces manual bars. Hit rate circular badge.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';
import MiniSparkline from '../charts/MiniSparkline';

interface StatTrendRowProps {
  label: string;
  line: number;
  last5: number[];
  last10Avg?: number;
}

function TrendArrow({ values }: { values: number[] }) {
  if (values.length < 3) return null;
  const recent = values.slice(-3).reduce((a, b) => a + b, 0) / 3;
  const earlier = values.slice(0, Math.max(values.length - 3, 1)).reduce((a, b) => a + b, 0) /
    Math.max(values.slice(0, values.length - 3).length, 1);
  const diff = recent - earlier;

  if (Math.abs(diff) < 1) return <Text style={[styles.arrow, { color: theme.colors.textSecondary }]}>-</Text>;
  if (diff > 0) return <Text style={[styles.arrow, { color: theme.colors.success }]}>{'\u2191'}</Text>;
  return <Text style={[styles.arrow, { color: theme.colors.danger }]}>{'\u2193'}</Text>;
}

export default function StatTrendRow({ label, line, last5, last10Avg }: StatTrendRowProps) {
  const avg5 = last5.length > 0 ? last5.reduce((a, b) => a + b, 0) / last5.length : 0;
  const hitCount = last5.filter((v) => v >= line).length;
  const hitRate = last5.length > 0 ? Math.round((hitCount / last5.length) * 100) : 0;
  const hitColor = hitRate >= 60 ? theme.colors.success : theme.colors.danger;

  return (
    <View style={styles.row}>
      <View style={styles.labelCol}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.lineText}>Line: {line}</Text>
      </View>

      {/* SVG Sparkline */}
      <View style={styles.sparklineContainer}>
        <MiniSparkline
          values={last5}
          threshold={line}
          width={80}
          height={32}
          color={hitRate >= 60 ? theme.colors.chartHit : theme.colors.chartMiss}
        />
      </View>

      <View style={styles.statsCol}>
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>L5 Avg</Text>
          <Text style={styles.statValue}>{avg5.toFixed(1)}</Text>
        </View>
        {last10Avg != null && (
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>L10</Text>
            <Text style={styles.statValue}>{last10Avg.toFixed(1)}</Text>
          </View>
        )}
      </View>

      {/* Hit rate badge */}
      <View style={[styles.hitBadge, { backgroundColor: hitColor + '1A' }]}>
        <Text style={[styles.hitText, { color: hitColor }]}>{hitRate}%</Text>
      </View>

      <TrendArrow values={last5} />
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 10,
    marginBottom: 6,
  },
  labelCol: {
    width: 72,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  lineText: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
  sparklineContainer: {
    marginHorizontal: 6,
  },
  statsCol: {
    width: 58,
    marginRight: 4,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statLabel: {
    fontSize: 9,
    color: theme.colors.textTertiary,
  },
  statValue: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  hitBadge: {
    width: 38,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 4,
  },
  hitText: {
    fontSize: 10,
    fontWeight: '800',
  },
  arrow: {
    fontSize: 18,
    fontWeight: '700',
    width: 18,
    textAlign: 'center',
  },
});
