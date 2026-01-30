/**
 * Results Summary Card
 * Displays overall performance metrics
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

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
              <Text style={styles.statValue}>{winRate.toFixed(1)}%</Text>
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
                <Text style={styles.statusText}>WON</Text>
              </View>
              <Text style={styles.breakdownValue}>{wins}</Text>
            </View>

            <View style={styles.breakdownRow}>
              <View style={[styles.statusBadge, styles.lostBadge]}>
                <Text style={styles.statusText}>LOST</Text>
              </View>
              <Text style={styles.breakdownValue}>{losses}</Text>
            </View>

            {pending > 0 && (
              <View style={styles.breakdownRow}>
                <View style={[styles.statusBadge, styles.pendingBadge]}>
                  <Text style={styles.statusText}>PENDING</Text>
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
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16,
  },
  emptyState: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#6B7280',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
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
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    marginHorizontal: 4,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  breakdown: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
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
    backgroundColor: '#D1FAE5',
  },
  lostBadge: {
    backgroundColor: '#FEE2E2',
  },
  pendingBadge: {
    backgroundColor: '#FEF3C7',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  breakdownValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
});
