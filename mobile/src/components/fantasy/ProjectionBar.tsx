/**
 * ProjectionBar — Floor/ceiling range bar with confidence indicator.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface ProjectionBarProps {
  floor: number;
  ceiling: number;
  projected: number;
  confidence: number;
  label?: string;
}

export default function ProjectionBar({
  floor,
  ceiling,
  projected,
  confidence,
  label,
}: ProjectionBarProps) {
  // Calculate positions as percentages of the range
  const range = ceiling - floor;
  const projectedPct = range > 0 ? ((projected - floor) / range) * 100 : 50;

  const confColor =
    confidence >= 65
      ? theme.colors.success
      : confidence >= 50
      ? theme.colors.primary
      : theme.colors.textSecondary;

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}

      <View style={styles.barRow}>
        <Text style={styles.boundLabel}>{floor.toFixed(1)}</Text>

        <View style={styles.barContainer}>
          {/* Range bar */}
          <View style={styles.rangeFill} />

          {/* Projected marker */}
          <View
            style={[
              styles.marker,
              {
                left: `${Math.min(Math.max(projectedPct, 5), 95)}%`,
                backgroundColor: confColor,
              },
            ]}
          >
            <Text style={styles.markerText}>{projected.toFixed(1)}</Text>
          </View>
        </View>

        <Text style={styles.boundLabel}>{ceiling.toFixed(1)}</Text>
      </View>

      <View style={styles.legendRow}>
        <Text style={styles.legendText}>Floor</Text>
        <View style={styles.confBadge}>
          <View style={[styles.confDot, { backgroundColor: confColor }]} />
          <Text style={styles.confText}>{Math.round(confidence)} conf</Text>
        </View>
        <Text style={styles.legendText}>Ceiling</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 12,
  },
  label: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  barRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  boundLabel: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    fontWeight: '600',
    width: 36,
    textAlign: 'center',
  },
  barContainer: {
    flex: 1,
    height: 8,
    backgroundColor: theme.colors.glassHigh,
    borderRadius: 4,
    position: 'relative',
    justifyContent: 'center',
  },
  rangeFill: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: '100%',
    backgroundColor: theme.colors.primary + '30',
    borderRadius: 4,
  },
  marker: {
    position: 'absolute',
    width: 4,
    height: 16,
    borderRadius: 2,
    top: -4,
    marginLeft: -2,
  },
  markerText: {
    position: 'absolute',
    top: -16,
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    width: 40,
    textAlign: 'center',
    left: -18,
  },
  legendRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 6,
    paddingHorizontal: 36,
  },
  legendText: {
    fontSize: 9,
    color: theme.colors.textTertiary,
  },
  confBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  confDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  confText: {
    fontSize: 9,
    color: theme.colors.textTertiary,
  },
});
