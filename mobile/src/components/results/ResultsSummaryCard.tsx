/**
 * Results Summary Card
 * Displays overall performance metrics — dark theme with glassmorphism
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface ResultsSummaryCardProps {
  totalGraded: number;
  wins: number;
  losses: number;
  winRate: number;
  avgConfidence: number;
  pending: number;
}

export default function ResultsSummaryCard({
  totalGraded,
  wins,
  losses,
  winRate,
  avgConfidence,
  pending,
}: ResultsSummaryCardProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Performance Summary</Text>

      {totalGraded === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No graded parlays yet</Text>
          <Text style={styles.emptySubtext}>
            Mark parlays as "Placed" and they'll be graded after games complete
          </Text>
        </View>
      ) : (
        <>
          <View style={styles.mainStats}>
            <View style={styles.statCard}>
              <Text style={[styles.statValue, { color: winRate >= 55 ? theme.colors.success : winRate >= 50 ? theme.colors.primary : theme.colors.danger }]}>
                {winRate.toFixed(1)}%
              </Text>
              <Text style={styles.statLabel}>Win Rate</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{totalGraded}</Text>
              <Text style={styles.statLabel}>Total Graded</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{avgConfidence.toFixed(1)}%</Text>
              <Text style={styles.statLabel}>Avg Confidence</Text>
            </View>
          </View>

          <View style={styles.breakdown}>
            <View style={styles.breakdownRow}>
              <View style={[styles.statusBadge, styles.wonBadge]}>
                <Text style={[styles.statusText, { color: theme.colors.success }]}>WON</Text>
              </View>
              <Text style={styles.breakdownValue}>{wins}</Text>
            </View>

            <View style={styles.breakdownRow}>
              <View style={[styles.statusBadge, styles.lostBadge]}>
                <Text style={[styles.statusText, { color: theme.colors.danger }]}>LOST</Text>
              </View>
              <Text style={styles.breakdownValue}>{losses}</Text>
            </View>

            {pending > 0 && (
              <View style={styles.breakdownRow}>
                <View style={[styles.statusBadge, styles.pendingBadge]}>
                  <Text style={[styles.statusText, { color: theme.colors.warning }]}>PENDING</Text>
                </View>
                <Text style={styles.breakdownValue}>{pending}</Text>
              </View>
            )}
          </View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    ...theme.shadows.card,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    marginBottom: 16,
  },
  emptyState: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: theme.colors.textTertiary,
    textAlign: 'center',
  },
  mainStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: theme.borderRadius.s,
    marginHorizontal: 4,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '800',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  breakdown: {
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    paddingTop: 12,
  },
  breakdownRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  wonBadge: {
    backgroundColor: theme.colors.successMuted,
  },
  lostBadge: {
    backgroundColor: theme.colors.dangerMuted,
  },
  pendingBadge: {
    backgroundColor: theme.colors.warningMuted,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  breakdownValue: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
});
