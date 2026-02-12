/**
 * LineMovementChart — Time-series line movement visualization.
 * Uses a simple SVG-free bar chart since react-native-chart-kit isn't installed yet.
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { theme } from '../../constants/theme';
import { LineMovementEntry } from '../../types';

interface LineMovementChartProps {
  movements: LineMovementEntry[];
  currentLine?: number;
}

export default function LineMovementChart({ movements, currentLine }: LineMovementChartProps) {
  if (!movements || movements.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No line movement data</Text>
      </View>
    );
  }

  const lines = movements.map((m) => m.line);
  const minLine = Math.min(...lines);
  const maxLine = Math.max(...lines);
  const range = maxLine - minLine || 1;

  // Calculate if line moved up or down overall
  const firstLine = movements[0].line;
  const lastLine = movements[movements.length - 1].line;
  const overallDirection = lastLine > firstLine ? 'up' : lastLine < firstLine ? 'down' : 'flat';

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>Line Movement</Text>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>
            {firstLine} → {lastLine}
          </Text>
          <Text
            style={[
              styles.summaryDelta,
              {
                color:
                  overallDirection === 'up'
                    ? theme.colors.danger
                    : overallDirection === 'down'
                    ? theme.colors.success
                    : theme.colors.textSecondary,
              },
            ]}
          >
            {overallDirection === 'up' ? '↑' : overallDirection === 'down' ? '↓' : '-'}
            {Math.abs(lastLine - firstLine).toFixed(1)}
          </Text>
        </View>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chartScroll}>
        <View style={styles.chart}>
          {movements.map((m, i) => {
            const normalizedHeight = ((m.line - minLine) / range) * 40 + 8;
            const isLast = i === movements.length - 1;
            const time = m.recorded_at
              ? new Date(m.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : '';

            return (
              <View key={i} style={styles.barGroup}>
                <Text style={[styles.barValue, isLast && styles.barValueLast]}>
                  {m.line}
                </Text>
                <View
                  style={[
                    styles.bar,
                    {
                      height: normalizedHeight,
                      backgroundColor: isLast ? theme.colors.primary : theme.colors.glassHigh,
                    },
                  ]}
                />
                <Text style={styles.barLabel} numberOfLines={1}>
                  {m.bookmaker?.substring(0, 3).toUpperCase() || ''}
                </Text>
                {time ? <Text style={styles.timeLabel}>{time}</Text> : null}
              </View>
            );
          })}
        </View>
      </ScrollView>
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
    marginBottom: 12,
  },
  title: {
    ...theme.typography.caption,
  },
  summaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  summaryLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  summaryDelta: {
    fontSize: 12,
    fontWeight: '700',
  },
  chartScroll: {
    marginTop: 4,
  },
  chart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingBottom: 4,
    gap: 8,
  },
  barGroup: {
    alignItems: 'center',
    minWidth: 40,
  },
  bar: {
    width: 24,
    borderRadius: 4,
    marginVertical: 2,
  },
  barValue: {
    fontSize: 10,
    color: theme.colors.textSecondary,
    fontWeight: '600',
    marginBottom: 2,
  },
  barValueLast: {
    color: theme.colors.primary,
    fontWeight: '800',
  },
  barLabel: {
    fontSize: 8,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  timeLabel: {
    fontSize: 7,
    color: theme.colors.textTertiary,
  },
  empty: {
    padding: 20,
    alignItems: 'center',
  },
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 13,
  },
});
