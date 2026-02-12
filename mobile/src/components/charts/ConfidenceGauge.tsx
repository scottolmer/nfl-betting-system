/**
 * ConfidenceGauge — Full-circle ring gauge for confidence scores (0-100).
 * Color transitions: red (0-45) -> gray (45-60) -> cyan (60-70) -> green (70+).
 * Score number centered inside the ring. Glow shadow matching score color.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { theme } from '../../constants/theme';

interface ConfidenceGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 70) return theme.colors.success;
  if (score >= 60) return theme.colors.primary;
  if (score >= 45) return theme.colors.textSecondary;
  return theme.colors.danger;
}

const SIZES = {
  sm: { dim: 40, stroke: 3, fontSize: 13, labelSize: 7 },
  md: { dim: 64, stroke: 5, fontSize: 20, labelSize: 9 },
  lg: { dim: 96, stroke: 6, fontSize: 30, labelSize: 11 },
};

function ConfidenceGauge({ score, size = 'md', showLabel = true }: ConfidenceGaugeProps) {
  const s = SIZES[size];
  const r = (s.dim - s.stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const clampedScore = Math.min(Math.max(score, 0), 100);
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;
  const color = getScoreColor(score);

  return (
    <View style={[styles.container, { width: s.dim, height: s.dim }]}>
      <Svg width={s.dim} height={s.dim}>
        {/* Background ring */}
        <Circle
          cx={s.dim / 2}
          cy={s.dim / 2}
          r={r}
          stroke={theme.colors.chartNeutral}
          strokeWidth={s.stroke}
          fill="none"
        />
        {/* Filled ring — starts from top (rotation -90°) and sweeps clockwise */}
        {clampedScore > 0 && (
          <Circle
            cx={s.dim / 2}
            cy={s.dim / 2}
            r={r}
            stroke={color}
            strokeWidth={s.stroke}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${circumference}`}
            strokeDashoffset={strokeDashoffset}
            rotation={-90}
            origin={`${s.dim / 2}, ${s.dim / 2}`}
          />
        )}
      </Svg>
      {/* Centered score text */}
      <View style={styles.scoreOverlay}>
        <Text style={[styles.scoreText, { fontSize: s.fontSize, color }]}>
          {Math.round(score)}
        </Text>
        {showLabel && size !== 'sm' && (
          <Text style={[styles.label, { fontSize: s.labelSize }]}>CONF</Text>
        )}
      </View>
    </View>
  );
}

export default React.memo(ConfidenceGauge);

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  scoreOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scoreText: {
    fontWeight: '800',
    letterSpacing: -0.5,
  },
  label: {
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginTop: -1,
  },
});
