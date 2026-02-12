/**
 * MiniSparkline — SVG line chart for stat trends.
 * Area fill below with 15% opacity. Optional threshold line.
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Polyline, Polygon, Line, Circle } from 'react-native-svg';
import { theme } from '../../constants/theme';

interface MiniSparklineProps {
  values: number[];
  threshold?: number;
  width?: number;
  height?: number;
  color?: string;
  showDots?: boolean;
}

function MiniSparkline({
  values,
  threshold,
  width = 100,
  height = 32,
  color = theme.colors.chartLine,
  showDots = false,
}: MiniSparklineProps) {
  if (!values || values.length < 2) return null;

  const padding = 2;
  const w = width - padding * 2;
  const h = height - padding * 2;

  const allValues = threshold != null ? [...values, threshold] : values;
  const max = Math.max(...allValues) * 1.05;
  const min = Math.min(...allValues) * 0.95;
  const range = max - min || 1;

  const points = values.map((v, i) => {
    const x = padding + (i / (values.length - 1)) * w;
    const y = padding + h - ((v - min) / range) * h;
    return { x, y };
  });

  const linePoints = points.map(p => `${p.x},${p.y}`).join(' ');

  // Area polygon: line points + bottom-right + bottom-left
  const areaPoints = [
    ...points.map(p => `${p.x},${p.y}`),
    `${points[points.length - 1].x},${height}`,
    `${points[0].x},${height}`,
  ].join(' ');

  const thresholdY = threshold != null
    ? padding + h - ((threshold - min) / range) * h
    : null;

  return (
    <View style={[styles.container, { width, height }]}>
      <Svg width={width} height={height}>
        {/* Threshold line */}
        {thresholdY != null && (
          <Line
            x1={padding}
            y1={thresholdY}
            x2={width - padding}
            y2={thresholdY}
            stroke={theme.colors.textTertiary}
            strokeWidth={1}
            strokeDasharray="3,2"
          />
        )}
        {/* Area fill */}
        <Polygon points={areaPoints} fill={color} opacity={0.12} />
        {/* Line */}
        <Polyline
          points={linePoints}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Dots */}
        {showDots &&
          points.map((p, i) => (
            <Circle
              key={i}
              cx={p.x}
              cy={p.y}
              r={i === points.length - 1 ? 3 : 2}
              fill={i === points.length - 1 ? color : 'transparent'}
              stroke={color}
              strokeWidth={1}
            />
          ))}
        {/* Last dot always visible */}
        {!showDots && points.length > 0 && (
          <Circle
            cx={points[points.length - 1].x}
            cy={points[points.length - 1].y}
            r={2.5}
            fill={color}
          />
        )}
      </Svg>
    </View>
  );
}

export default React.memo(MiniSparkline);

const styles = StyleSheet.create({
  container: {},
});
