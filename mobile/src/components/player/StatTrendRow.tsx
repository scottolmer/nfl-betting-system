/**
 * StatTrendRow — L5/L10 stats with mini sparkline and trend arrow.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

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
  if (diff > 0) return <Text style={[styles.arrow, { color: theme.colors.success }]}>↑</Text>;
  return <Text style={[styles.arrow, { color: theme.colors.danger }]}>↓</Text>;
}

function MiniSparkline({ values, line }: { values: number[]; line: number }) {
  if (values.length === 0) return null;
  const max = Math.max(...values, line) * 1.1;
  const min = Math.min(...values, line) * 0.9;
  const range = max - min || 1;

  return (
    <View style={styles.sparkline}>
      {/* Line threshold marker */}
      <View
        style={[
          styles.threshold,
          { bottom: `${((line - min) / range) * 100}%` },
        ]}
      />
      {values.map((v, i) => {
        const height = Math.max(((v - min) / range) * 32, 2);
        const overLine = v >= line;
        return (
          <View
            key={i}
            style={[
              styles.sparkBar,
              {
                height,
                backgroundColor: overLine ? theme.colors.success : theme.colors.danger,
                opacity: 0.4 + (i / values.length) * 0.6,
              },
            ]}
          />
        );
      })}
    </View>
  );
}

export default function StatTrendRow({ label, line, last5, last10Avg }: StatTrendRowProps) {
  const avg5 = last5.length > 0 ? last5.reduce((a, b) => a + b, 0) / last5.length : 0;
  const hitRate = last5.length > 0
    ? Math.round((last5.filter((v) => v >= line).length / last5.length) * 100)
    : 0;

  return (
    <View style={styles.row}>
      <View style={styles.labelCol}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.lineText}>Line: {line}</Text>
      </View>
      <MiniSparkline values={last5} line={line} />
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
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Hit</Text>
          <Text style={[styles.statValue, { color: hitRate >= 60 ? theme.colors.success : theme.colors.danger }]}>
            {hitRate}%
          </Text>
        </View>
      </View>
      <TrendArrow values={last5} />
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 10,
    marginBottom: 6,
  },
  labelCol: {
    width: 80,
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
  sparkline: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: 32,
    marginHorizontal: 8,
    gap: 2,
  },
  sparkBar: {
    flex: 1,
    borderRadius: 2,
    minWidth: 4,
  },
  threshold: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: theme.colors.textTertiary,
  },
  statsCol: {
    width: 60,
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
  arrow: {
    fontSize: 18,
    fontWeight: '700',
    width: 20,
    textAlign: 'center',
  },
});
