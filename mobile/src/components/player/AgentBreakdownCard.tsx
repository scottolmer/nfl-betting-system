/**
 * AgentBreakdownCard V3 — Shows each agent's score, direction, reasoning,
 * and an AI summary at the bottom.
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import GlassCard from '../common/GlassCard';

interface AgentData {
  score: number;
  weight: number;
  direction: string;
  rationale?: string[];
}

interface AgentBreakdownCardProps {
  breakdown: Record<string, AgentData>;
  edgeExplanation?: string;
  topReasons?: string[];
}

const AGENT_META: Record<string, { label: string; icon: string; desc: string }> = {
  Injury: { label: 'Injury', icon: 'medkit', desc: 'Player health & availability impact' },
  DVOA: { label: 'DVOA', icon: 'stats-chart', desc: 'Efficiency metrics & EPA analysis' },
  Variance: { label: 'Variance', icon: 'pulse', desc: 'Statistical consistency & volatility' },
  GameScript: { label: 'Game Script', icon: 'game-controller', desc: 'Pace, game flow & situational factors' },
  Volume: { label: 'Volume', icon: 'bar-chart', desc: 'Usage rate, targets & snap share' },
  Matchup: { label: 'Matchup', icon: 'shield-half', desc: 'Defensive matchup & positional advantage' },
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

function cleanRationale(text: string): string {
  // Strip emoji prefixes for cleaner display
  return text.replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE00}-\u{FEFF}]\s*/u, '').trim();
}

function buildSummary(
  sorted: [string, AgentData][],
  agreementPct: number,
  majorityDirection: string,
): string {
  const bullish = sorted.filter(([, d]) => d.score >= 60 && d.direction !== 'AVOID');
  const bearish = sorted.filter(([, d]) => d.score < 45 && d.direction !== 'AVOID');

  const topDriver = sorted[0];
  const driverLabel = AGENT_META[topDriver[0]]?.label || topDriver[0];
  const driverScore = Math.round(topDriver[1].score);

  let summary = '';

  if (agreementPct >= 80) {
    summary += `High consensus (${agreementPct}% agree on ${majorityDirection}). `;
    summary += 'When most agents agree, the line is often already priced in - proceed with caution. ';
  } else if (agreementPct <= 50) {
    summary += `Split signal (${agreementPct}% agreement). `;
    summary += 'Agent disagreement can indicate hidden value the market hasn\'t fully captured. ';
  } else {
    summary += `Moderate consensus (${agreementPct}% lean ${majorityDirection}). `;
  }

  summary += `${driverLabel} is the strongest signal at ${driverScore}. `;

  if (bullish.length >= 4) {
    summary += 'Multiple agents strongly favor this prop.';
  } else if (bearish.length >= 3) {
    summary += 'Several agents show concern - consider the risk.';
  } else if (bullish.length > 0 && bearish.length > 0) {
    const bullNames = bullish.map(([n]) => AGENT_META[n]?.label || n).join(', ');
    const bearNames = bearish.map(([n]) => AGENT_META[n]?.label || n).join(', ');
    summary += `${bullNames} bullish; ${bearNames} cautious.`;
  }

  return summary;
}

export default function AgentBreakdownCard({ breakdown, edgeExplanation, topReasons }: AgentBreakdownCardProps) {
  if (!breakdown || Object.keys(breakdown).length === 0) return null;

  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const sorted = Object.entries(breakdown).sort(
    ([, a], [, b]) => (b.score * b.weight) - (a.score * a.weight),
  );

  // Agreement level
  const directions = sorted.map(([, d]) => d.direction).filter(d => d !== 'AVOID');
  const overCount = directions.filter(d => d === 'OVER').length;
  const underCount = directions.filter(d => d === 'UNDER').length;
  const agreementPct = directions.length > 0
    ? Math.round((Math.max(overCount, underCount) / directions.length) * 100)
    : 0;
  const majorityDirection = overCount >= underCount ? 'OVER' : 'UNDER';
  const isHighAgreement = agreementPct > 80;

  const summary = buildSummary(sorted, agreementPct, majorityDirection);

  return (
    <GlassCard>
      {/* Header */}
      <View style={styles.headerRow}>
        <Text style={styles.title}>AGENT BREAKDOWN</Text>
        <View style={[styles.agreementBadge, isHighAgreement && styles.agreementWarning]}>
          <Text style={[styles.agreementText, isHighAgreement && styles.agreementTextWarning]}>
            {agreementPct}% agree
          </Text>
        </View>
      </View>

      {/* Agent rows */}
      {sorted.map(([name, data]) => {
        const barWidth = Math.min(Math.max(data.score, 5), 100);
        const color = getBarColor(data.score, data.direction);
        const scoreBg = getScoreBgColor(data.score, data.direction);
        const meta = AGENT_META[name] || { label: name, icon: 'help-circle', desc: '' };
        const isExpanded = expandedAgent === name;
        const hasRationale = data.rationale && data.rationale.length > 0;

        return (
          <View key={name}>
            <TouchableOpacity
              activeOpacity={0.7}
              onPress={() => setExpandedAgent(isExpanded ? null : name)}
              style={styles.row}
            >
              {/* Icon */}
              <View style={[styles.iconCircle, { backgroundColor: scoreBg }]}>
                <Ionicons name={meta.icon as any} size={14} color={color} />
              </View>

              {/* Name + bar */}
              <View style={styles.midCol}>
                <View style={styles.nameRow}>
                  <Text style={styles.agentName}>{meta.label}</Text>
                  <Text style={styles.weight}>w:{data.weight.toFixed(1)}</Text>
                </View>
                <View style={styles.barContainer}>
                  <View style={[styles.bar, { width: `${barWidth}%`, backgroundColor: color }]} />
                </View>
              </View>

              {/* Score badge */}
              <View style={[styles.scoreBadge, { backgroundColor: scoreBg }]}>
                <Text style={[styles.score, { color }]}>{Math.round(data.score)}</Text>
              </View>

              {/* Direction */}
              <Text style={[styles.direction, { color }]}>
                {data.direction === 'OVER' ? 'OV' : data.direction === 'UNDER' ? 'UN' : '--'}
              </Text>

              {/* Expand indicator */}
              <Ionicons
                name={isExpanded ? 'chevron-up' : 'chevron-down'}
                size={14}
                color={theme.colors.textTertiary}
              />
            </TouchableOpacity>

            {/* Expanded reasoning */}
            {isExpanded && (
              <View style={styles.reasoningBox}>
                {hasRationale ? (
                  data.rationale!.map((reason, i) => (
                    <View key={i} style={styles.reasonRow}>
                      <View style={[styles.reasonDot, { backgroundColor: color }]} />
                      <Text style={styles.reasonText}>{cleanRationale(reason)}</Text>
                    </View>
                  ))
                ) : (
                  <Text style={styles.noReasoning}>{meta.desc}</Text>
                )}
              </View>
            )}
          </View>
        );
      })}

      {/* AI Summary */}
      <View style={styles.summaryBox}>
        <View style={styles.summaryHeader}>
          <Ionicons name="bulb" size={14} color={theme.colors.gold} />
          <Text style={styles.summaryLabel}>AI SUMMARY</Text>
        </View>
        <Text style={styles.summaryText}>{summary}</Text>
      </View>

      {/* Top Reasons */}
      {topReasons && topReasons.length > 0 && (
        <View style={styles.reasonsBox}>
          <Text style={styles.reasonsTitle}>TOP REASONS</Text>
          {topReasons.map((reason, i) => (
            <View key={i} style={styles.topReasonRow}>
              <View style={styles.reasonBulletCircle}>
                <Text style={styles.reasonNumber}>{i + 1}</Text>
              </View>
              <Text style={styles.topReasonText}>{reason}</Text>
            </View>
          ))}
        </View>
      )}
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  topReasonRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
    gap: 10,
  },
  reasonBulletCircle: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: theme.colors.primaryMuted,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 1,
  },
  reasonNumber: {
    fontSize: 10,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  topReasonText: {
    flex: 1,
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 19,
  },
  reasonsBox: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  reasonsTitle: {
    ...theme.typography.caption,
    marginBottom: 12,
  },
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
  // Agent row
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    gap: 8,
  },
  iconCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  midCol: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 4,
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
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  bar: {
    height: 6,
    borderRadius: 3,
  },
  scoreBadge: {
    width: 34,
    height: 26,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
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
  // Expanded reasoning
  reasoningBox: {
    marginLeft: 36,
    marginBottom: 12,
    paddingLeft: 12,
    borderLeftWidth: 2,
    borderLeftColor: theme.colors.glassBorder,
  },
  reasonRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 5,
    gap: 8,
  },
  reasonDot: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
    marginTop: 5,
  },
  reasonText: {
    flex: 1,
    fontSize: 12,
    color: theme.colors.textSecondary,
    lineHeight: 17,
  },
  noReasoning: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
  },
  // Summary
  summaryBox: {
    marginTop: 8,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  summaryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.gold,
    letterSpacing: 0.5,
  },
  summaryText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 19,
  },
});
