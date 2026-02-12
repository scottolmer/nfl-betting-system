/**
 * AgentBreakdownCard V2 — Wider gradient-filled bars, score badges with colored
 * circular backgrounds, "Agreement Level" indicator.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';
import GlassCard from '../common/GlassCard';

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

function getScoreBgColor(score: number, direction: string): string {
  if (direction === 'AVOID') return 'rgba(71, 85, 105, 0.2)';
  if (score >= 70) return theme.colors.successMuted;
  if (score >= 55) return theme.colors.primaryMuted;
  if (score >= 45) return 'rgba(148, 163, 184, 0.12)';
  return theme.colors.dangerMuted;
}

function getDirectionLabel(direction: string): string {
  if (direction === 'OVER') return 'OV';
  if (direction === 'UNDER') return 'UN';
  return '--';
}

export default function AgentBreakdownCard({ breakdown }: AgentBreakdownCardProps) {
  if (!breakdown || Object.keys(breakdown).length === 0) return null;

  const sorted = Object.entries(breakdown).sort(
    ([, a], [, b]) => b.weight - a.weight,
  );

  // Agreement level calculation
  const directions = sorted.map(([, d]) => d.direction).filter(d => d !== 'AVOID');
  const overCount = directions.filter(d => d === 'OVER').length;
  const underCount = directions.filter(d => d === 'UNDER').length;
  const agreementPct = directions.length > 0
    ? Math.round((Math.max(overCount, underCount) / directions.length) * 100)
    : 0;
  const isHighAgreement = agreementPct > 80;

  return (
    <GlassCard>
      {/* Header with agreement indicator */}
      <View style={styles.headerRow}>
        <Text style={styles.title}>AGENT BREAKDOWN</Text>
        <View style={[styles.agreementBadge, isHighAgreement && styles.agreementWarning]}>
          <Text style={[styles.agreementText, isHighAgreement && styles.agreementTextWarning]}>
            {agreementPct}% agree
          </Text>
        </View>
      </View>

      {sorted.map(([name, data]) => {
        const barWidth = Math.min(Math.max(data.score, 5), 100);
        const color = getBarColor(data.score, data.direction);
        const scoreBg = getScoreBgColor(data.score, data.direction);

        return (
          <View key={name} style={styles.row}>
            <View style={styles.labelCol}>
              <Text style={styles.agentName}>{AGENT_LABELS[name] || name}</Text>
              <Text style={styles.weight}>w:{data.weight.toFixed(1)}</Text>
            </View>
            <View style={styles.barContainer}>
              <View style={[styles.bar, { width: `${barWidth}%`, backgroundColor: color }]} />
            </View>
            <View style={[styles.scoreBadge, { backgroundColor: scoreBg }]}>
              <Text style={[styles.score, { color }]}>{Math.round(data.score)}</Text>
            </View>
            <Text style={[styles.direction, { color }]}>
              {getDirectionLabel(data.direction)}
            </Text>
          </View>
        );
      })}
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  title: {
    ...theme.typography.caption,
  },
  agreementBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
    backgroundColor: theme.colors.primaryMuted,
  },
  agreementWarning: {
    backgroundColor: theme.colors.warningMuted,
  },
  agreementText: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  agreementTextWarning: {
    color: theme.colors.warning,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
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
    height: 10,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 5,
    marginHorizontal: 8,
    overflow: 'hidden',
  },
  bar: {
    height: 10,
    borderRadius: 5,
  },
  scoreBadge: {
    width: 34,
    height: 26,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 6,
  },
  score: {
    fontSize: 13,
    fontWeight: '800',
  },
  direction: {
    fontSize: 10,
    fontWeight: '700',
    width: 20,
    textAlign: 'center',
  },
});
