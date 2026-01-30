/**
 * Position Performance
 * Shows hit rate by player position
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface PositionStat {
  position: string;
  total_legs: number;
  legs_hit: number;
  hit_rate: number;
}

interface PositionPerformanceProps {
  positionStats: PositionStat[];
}

export default function PositionPerformance({ positionStats }: PositionPerformanceProps) {
  const sortedStats = [...positionStats].sort((a, b) => b.hit_rate - a.hit_rate);

  const getBarColor = (hitRate: number): string => {
    if (hitRate >= 75) return '#10B981';
    if (hitRate >= 65) return '#F59E0B';
    return '#EF4444';
  };

  const getPositionIcon = (position: string): string => {
    const icons: Record<string, string> = {
      QB: '🎯',
      RB: '🏃',
      WR: '⚡',
      TE: '💪',
    };
    return icons[position] || '🏈';
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Performance by Position</Text>
      <Text style={styles.subtitle}>Hit rate for each position</Text>

      {sortedStats.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Not enough data yet</Text>
        </View>
      ) : (
        <View style={styles.stats}>
          {sortedStats.map((stat, index) => (
            <View key={index} style={styles.statRow}>
              <View style={styles.statInfo}>
                <View style={styles.positionHeader}>
                  <Text style={styles.icon}>{getPositionIcon(stat.position)}</Text>
                  <Text style={styles.position}>{stat.position}</Text>
                </View>
                <Text style={styles.legsCount}>
                  {stat.legs_hit}/{stat.total_legs} legs hit
                </Text>
              </View>

              <View style={styles.barContainer}>
                <View
                  style={[
                    styles.bar,
                    {
                      width: `${stat.hit_rate}%`,
                      backgroundColor: getBarColor(stat.hit_rate),
                    },
                  ]}
                />
                <Text style={styles.hitRate}>{stat.hit_rate.toFixed(0)}%</Text>
              </View>
            </View>
          ))}
        </View>
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
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 16,
  },
  emptyState: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  stats: {
    gap: 12,
  },
  statRow: {
    marginBottom: 12,
  },
  statInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  positionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  icon: {
    fontSize: 18,
  },
  position: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  legsCount: {
    fontSize: 13,
    color: '#6B7280',
  },
  barContainer: {
    position: 'relative',
    height: 24,
    backgroundColor: '#F3F4F6',
    borderRadius: 4,
    overflow: 'hidden',
    justifyContent: 'center',
  },
  bar: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    borderRadius: 4,
  },
  hitRate: {
    position: 'absolute',
    right: 8,
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937',
  },
});
