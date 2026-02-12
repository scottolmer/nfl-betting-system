/**
 * LineMovementChartV2 — SVG time-series line chart for line movements.
 * Area fill, reference line at opening, dots at data points.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Polyline, Polygon, Line, Circle, Text as SvgText } from 'react-native-svg';
import { theme } from '../../constants/theme';
import { LineMovementEntry } from '../../types';

interface LineMovementChartV2Props {
  movements: LineMovementEntry[];
  currentLine?: number;
}

function LineMovementChartV2({ movements, currentLine }: LineMovementChartV2Props) {
  if (!movements || movements.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No line movement data</Text>
      </View>
    );
  }

  const chartWidth = 280;
  const chartHeight = 80;
  const paddingH = 8;
  const paddingV = 12;
  const w = chartWidth - paddingH * 2;
  const h = chartHeight - paddingV * 2;

  const lines = movements.map(m => m.line);
  const min = Math.min(...lines) - 0.5;
  const max = Math.max(...lines) + 0.5;
  const range = max - min || 1;

  const firstLine = movements[0].line;
  const lastLine = movements[movements.length - 1].line;
  const delta = lastLine - firstLine;

  const points = movements.map((m, i) => ({
    x: paddingH + (i / Math.max(movements.length - 1, 1)) * w,
    y: paddingV + h - ((m.line - min) / range) * h,
  }));

  const linePoints = points.map(p => `${p.x},${p.y}`).join(' ');
  const areaPoints = [
    ...points.map(p => `${p.x},${p.y}`),
    `${points[points.length - 1].x},${chartHeight}`,
    `${points[0].x},${chartHeight}`,
  ].join(' ');

  // Opening reference line
  const openingY = paddingV + h - ((firstLine - min) / range) * h;

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>LINE MOVEMENT</Text>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>
            {firstLine} {'\u2192'} {lastLine}
          </Text>
          <Text
            style={[
              styles.summaryDelta,
              { color: delta > 0 ? theme.colors.danger : delta < 0 ? theme.colors.success : theme.colors.textSecondary },
            ]}
          >
            {delta > 0 ? '\u2191' : delta < 0 ? '\u2193' : '-'}
            {Math.abs(delta).toFixed(1)}
          </Text>
        </View>
      </View>

      <Svg width={chartWidth} height={chartHeight}>
        {/* Opening reference line */}
        <Line
          x1={paddingH}
          y1={openingY}
          x2={chartWidth - paddingH}
          y2={openingY}
          stroke={theme.colors.textTertiary}
          strokeWidth={1}
          strokeDasharray="4,3"
          opacity={0.5}
        />
        {/* Area fill */}
        <Polygon points={areaPoints} fill={theme.colors.primary} opacity={0.1} />
        {/* Line */}
        <Polyline
          points={linePoints}
          fill="none"
          stroke={theme.colors.primary}
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Data points */}
        {points.map((p, i) => (
          <Circle
            key={i}
            cx={p.x}
            cy={p.y}
            r={i === points.length - 1 ? 4 : 2.5}
            fill={i === points.length - 1 ? theme.colors.primary : theme.colors.backgroundCard}
            stroke={theme.colors.primary}
            strokeWidth={1.5}
          />
        ))}
        {/* Opening label */}
        <SvgText
          x={paddingH + 2}
          y={openingY - 4}
          fontSize={9}
          fill={theme.colors.textTertiary}
        >
          Open: {firstLine}
        </SvgText>
      </Svg>

      {/* Book labels */}
      <View style={styles.bookLabels}>
        {movements.slice(0, 6).map((m, i) => (
          <Text key={i} style={styles.bookLabel} numberOfLines={1}>
            {m.bookmaker?.substring(0, 4).toUpperCase() || ''}
          </Text>
        ))}
      </View>
    </View>
  );
}

export default React.memo(LineMovementChartV2);

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.backgroundCard,
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
  bookLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 8,
    marginTop: 4,
  },
  bookLabel: {
    fontSize: 8,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
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
