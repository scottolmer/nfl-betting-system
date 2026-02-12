/**
 * FloatingParlayBar — Bottom bar showing current parlay picks,
 * combined confidence, and review button. Appears when picks > 0.
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { useParlay } from '../../contexts/ParlayContext';

interface FloatingParlayBarProps {
  onReview: () => void;
}

export default function FloatingParlayBar({ onReview }: FloatingParlayBarProps) {
  const { picks, maxPicks, combinedConfidence, clearPicks } = useParlay();

  if (picks.length === 0) return null;

  const isFull = picks.length >= maxPicks;
  const canReview = picks.length >= 2;

  return (
    <View style={styles.bar}>
      {/* Clear button */}
      <TouchableOpacity onPress={clearPicks} style={styles.clearBtn} activeOpacity={0.7}>
        <Ionicons name="close" size={16} color={theme.colors.textTertiary} />
      </TouchableOpacity>

      {/* Stats */}
      <View style={styles.stats}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {picks.length}/{maxPicks}
          </Text>
          <Text style={styles.statLabel}>Legs</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: theme.colors.primary }]}>
            {combinedConfidence}
          </Text>
          <Text style={styles.statLabel}>Combined</Text>
        </View>
      </View>

      {/* Review button */}
      <TouchableOpacity
        style={[styles.reviewBtn, canReview && styles.reviewBtnReady, isFull && styles.reviewBtnFull]}
        onPress={onReview}
        disabled={!canReview}
        activeOpacity={0.7}
      >
        <Ionicons name="checkmark-circle" size={18} color={canReview ? '#000' : '#fff'} />
        <Text style={[styles.reviewText, canReview && styles.reviewTextReady]}>
          Review
        </Text>
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
    backgroundColor: theme.colors.backgroundCard,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    paddingHorizontal: 12,
    paddingVertical: 10,
    paddingBottom: 28,
  },
  clearBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.backgroundElevated,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
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
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: theme.borderRadius.s,
    paddingHorizontal: 16,
    paddingVertical: 10,
    gap: 6,
    marginLeft: 8,
  },
  reviewBtnReady: {
    backgroundColor: theme.colors.primary,
  },
  reviewBtnFull: {
    backgroundColor: theme.colors.success,
  },
  reviewText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
  reviewTextReady: {
    color: '#000',
  },
});
