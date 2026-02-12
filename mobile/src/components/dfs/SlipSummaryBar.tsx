/**
 * SlipSummaryBar — Floating bar showing pick count, correlation score, confidence.
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';

interface SlipSummaryBarProps {
  pickCount: number;
  maxPicks: number;
  correlationRisk: 'low' | 'medium' | 'high';
  adjustedConfidence: number;
  onReview: () => void;
}

function getRiskColor(risk: string): string {
  switch (risk) {
    case 'low': return theme.colors.success;
    case 'medium': return theme.colors.gold;
    case 'high': return theme.colors.danger;
    default: return theme.colors.textSecondary;
  }
}

export default function SlipSummaryBar({
  pickCount,
  maxPicks,
  correlationRisk,
  adjustedConfidence,
  onReview,
}: SlipSummaryBarProps) {
  const riskColor = getRiskColor(correlationRisk);
  const isFull = pickCount >= maxPicks;

  return (
    <View style={styles.bar}>
      <View style={styles.stats}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{pickCount}/{maxPicks}</Text>
          <Text style={styles.statLabel}>Picks</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: riskColor }]}>
            {correlationRisk.toUpperCase()}
          </Text>
          <Text style={styles.statLabel}>Correlation</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{Math.round(adjustedConfidence)}</Text>
          <Text style={styles.statLabel}>Confidence</Text>
        </View>
      </View>

      <TouchableOpacity
        style={[styles.reviewBtn, isFull && styles.reviewBtnReady]}
        onPress={onReview}
        disabled={pickCount < 2}
        activeOpacity={0.7}
      >
        <Ionicons name="checkmark-circle" size={18} color="#fff" />
        <Text style={styles.reviewText}>Review</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundDark,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    paddingHorizontal: 16,
    paddingVertical: 10,
    paddingBottom: 28,
  },
  stats: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  statLabel: {
    fontSize: 9,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginTop: 1,
  },
  divider: {
    width: 1,
    height: 24,
    backgroundColor: theme.colors.glassBorder,
  },
  reviewBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassHigh,
    borderRadius: theme.borderRadius.s,
    paddingHorizontal: 16,
    paddingVertical: 10,
    gap: 6,
    marginLeft: 12,
  },
  reviewBtnReady: {
    backgroundColor: theme.colors.primary,
  },
  reviewText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
});
