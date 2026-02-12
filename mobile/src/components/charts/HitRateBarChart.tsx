/**
 * HitRateBarChart — Props.Cash-style vertical bars for last N games.
 * Each bar colored green (hit) or red (miss) relative to the betting line.
 * Horizontal dashed threshold line. "X/Y hit (80%)" label below.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Rect, Line } from 'react-native-svg';
import { theme } from '../../constants/theme';

interface HitRateBarChartProps {
  values: number[];
  line: number;
  label?: string; // e.g. "L5", "L10", "L20"
  height?: number;
  showLabel?: boolean;
}

function HitRateBarChart({
  values,
  line,
  label,
  height = 48,
  showLabel = true,
}: HitRateBarChartProps) {
  if (!values || values.length === 0) return null;

  const hits = values.filter(v => v >= line).length;
  const hitRate = Math.round((hits / values.length) * 100);
  const barWidth = Math.max(6, Math.min(16, 120 / values.length));
  const gap = 3;
  const chartWidth = values.length * (barWidth + gap) - gap;

  const allValues = [...values, line];
  const max = Math.max(...allValues) * 1.1;
  const min = Math.min(...allValues) * 0.9;
  const range = max - min || 1;

  const lineY = height - ((line - min) / range) * height;

  return (
    <View style={styles.container}>
      <Svg width={chartWidth} height={height}>
        {/* Threshold line */}
        <Line
          x1={0}
          y1={lineY}
          x2={chartWidth}
          y2={lineY}
          stroke={theme.colors.textTertiary}
          strokeWidth={1}
          strokeDasharray="3,3"
        />
        {/* Bars */}
        {values.map((v, i) => {
          const barHeight = Math.max(((v - min) / range) * height, 3);
          const isHit = v >= line;
          const x = i * (barWidth + gap);
          const y = height - barHeight;
          // Fade older bars
          const opacity = 0.4 + (i / values.length) * 0.6;

          return (
            <Rect
              key={i}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              rx={2}
              fill={isHit ? theme.colors.chartHit : theme.colors.chartMiss}
              opacity={opacity}
            />
          );
        })}
      </Svg>
      {showLabel && (
        <View style={styles.labelRow}>
          {label && <Text style={styles.periodLabel}>{label}:</Text>}
          <Text style={[styles.hitLabel, { color: hitRate >= 60 ? theme.colors.chartHit : theme.colors.chartMiss }]}>
            {hits}/{values.length} hit ({hitRate}%)
          </Text>
        </View>
      )}
    </View>
  );
}

export default React.memo(HitRateBarChart);

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 6,
  },
  periodLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
  },
  hitLabel: {
    fontSize: 11,
    fontWeight: '700',
  },
});
