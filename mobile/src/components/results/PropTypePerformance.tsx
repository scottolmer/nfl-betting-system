/**
 * Prop Type Performance
 * Shows hit rate by prop type
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface PropTypeStat {
  prop_type: string;
  total_legs: number;
  legs_hit: number;
  hit_rate: number;
}

interface PropTypePerformanceProps {
  propTypeStats: PropTypeStat[];
}

export default function PropTypePerformance({ propTypeStats }: PropTypePerformanceProps) {
  const sortedStats = [...propTypeStats].sort((a, b) => b.hit_rate - a.hit_rate);

  const getBarColor = (hitRate: number): string => {
    if (hitRate >= 75) return theme.colors.success;
    if (hitRate >= 65) return theme.colors.warning;
    return theme.colors.danger;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Performance by Prop Type</Text>
      <Text style={styles.subtitle}>Hit rate for each prop type</Text>

      {sortedStats.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Not enough data yet</Text>
        </View>
      ) : (
        <View style={styles.stats}>
          {sortedStats.map((stat, index) => (
            <View key={index} style={styles.statRow}>
              <View style={styles.statInfo}>
                <Text style={styles.propType}>{stat.prop_type}</Text>
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
    backgroundColor: theme.colors.backgroundCard,
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
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginBottom: 16,
  },
  emptyState: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: theme.colors.textTertiary,
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
  propType: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  legsCount: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  barContainer: {
    position: 'relative',
    height: 24,
    backgroundColor: theme.colors.backgroundElevated,
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
    color: theme.colors.textPrimary,
  },
});
