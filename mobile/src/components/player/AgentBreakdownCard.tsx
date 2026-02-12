/**
 * AgentBreakdownCard — Color-coded agent signals with reasoning.
 * Shows each agent's score, weight, and direction.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface AgentData {
  score: number;
  weight: number;
  direction: string;
}

interface AgentBreakdownCardProps {
  breakdown: Record<string, AgentData>;
}

const AGENT_LABELS: Record<string, string> = {
  Injury: 'Injury',
  DVOA: 'DVOA',
  Variance: 'Variance',
  GameScript: 'Game Script',
  Volume: 'Volume',
  Matchup: 'Matchup',
};

function getBarColor(score: number, direction: string): string {
  if (direction === 'AVOID') return theme.colors.textTertiary;
  if (score >= 70) return theme.colors.success;
  if (score >= 55) return theme.colors.primary;
  if (score >= 45) return theme.colors.textSecondary;
  return theme.colors.danger;
}

function getDirectionLabel(direction: string): string {
  if (direction === 'OVER') return 'OV';
  if (direction === 'UNDER') return 'UN';
  return '--';
}

export default function AgentBreakdownCard({ breakdown }: AgentBreakdownCardProps) {
  if (!breakdown || Object.keys(breakdown).length === 0) return null;

  // Sort by weight descending so most impactful agents show first
  const sorted = Object.entries(breakdown).sort(
    ([, a], [, b]) => b.weight - a.weight,
  );

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Agent Breakdown</Text>
      {sorted.map(([name, data]) => {
        const barWidth = Math.min(Math.max(data.score, 5), 100);
        const color = getBarColor(data.score, data.direction);

        return (
          <View key={name} style={styles.row}>
            <View style={styles.labelCol}>
              <Text style={styles.agentName}>{AGENT_LABELS[name] || name}</Text>
              <Text style={styles.weight}>w:{data.weight.toFixed(1)}</Text>
            </View>
            <View style={styles.barContainer}>
              <View style={[styles.bar, { width: `${barWidth}%`, backgroundColor: color }]} />
            </View>
            <View style={styles.scoreCol}>
              <Text style={[styles.score, { color }]}>{Math.round(data.score)}</Text>
              <Text style={[styles.direction, { color }]}>
                {getDirectionLabel(data.direction)}
              </Text>
            </View>
          </View>
        );
      })}
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
    marginBottom: 12,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  labelCol: {
    width: 80,
  },
  agentName: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  weight: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
  barContainer: {
    flex: 1,
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 3,
    marginHorizontal: 8,
    overflow: 'hidden',
  },
  bar: {
    height: 6,
    borderRadius: 3,
  },
  scoreCol: {
    width: 40,
    alignItems: 'flex-end',
  },
  score: {
    fontSize: 14,
    fontWeight: '700',
  },
  direction: {
    fontSize: 10,
    fontWeight: '600',
  },
});
