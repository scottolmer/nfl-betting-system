/**
 * AgentReasoningCard — "Why this pick?" with top 3 agent drivers.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface AgentDriver {
  name: string;
  score: number;
  weight: number;
  direction: string;
}

interface AgentReasoningCardProps {
  playerName: string;
  drivers: AgentDriver[];
}

const AGENT_DESCRIPTIONS: Record<string, string> = {
  Injury: 'Player and key teammate health status',
  DVOA: 'Team offensive/defensive efficiency metrics',
  Variance: 'Historical prop reliability (inverted signal)',
  GameScript: 'Game flow context from total and spread (inverted)',
  Volume: 'Player usage: snap share, targets, touches',
  Matchup: 'Position-specific defensive matchup quality',
};

function getScoreColor(score: number): string {
  if (score >= 70) return theme.colors.success;
  if (score >= 55) return theme.colors.primary;
  if (score >= 45) return theme.colors.textSecondary;
  return theme.colors.danger;
}

export default function AgentReasoningCard({ playerName, drivers }: AgentReasoningCardProps) {
  const topDrivers = drivers
    .sort((a, b) => b.weight * Math.abs(b.score - 50) - a.weight * Math.abs(a.score - 50))
    .slice(0, 3);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Why {playerName}?</Text>

      {topDrivers.map((driver, i) => (
        <View key={driver.name} style={styles.driverRow}>
          <View style={styles.rankCircle}>
            <Text style={styles.rank}>{i + 1}</Text>
          </View>
          <View style={styles.driverInfo}>
            <View style={styles.driverHeader}>
              <Text style={styles.driverName}>{driver.name}</Text>
              <Text style={[styles.driverScore, { color: getScoreColor(driver.score) }]}>
                {Math.round(driver.score)}
              </Text>
            </View>
            <Text style={styles.driverDesc}>
              {AGENT_DESCRIPTIONS[driver.name] || 'Analysis signal'}
            </Text>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
  },
  title: {
    ...theme.typography.caption,
    marginBottom: 10,
  },
  driverRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
    gap: 10,
  },
  rankCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: theme.colors.glassHigh,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 2,
  },
  rank: {
    fontSize: 11,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  driverInfo: {
    flex: 1,
  },
  driverHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  driverName: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  driverScore: {
    fontSize: 14,
    fontWeight: '800',
  },
  driverDesc: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 1,
  },
});
