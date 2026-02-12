/**
 * FlexPlayOptimizer — Shows optimal flex pick designation.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';

interface FlexCandidate {
  player_name: string;
  team: string;
  position: string;
  stat_type: string;
  flex_score: number;
  correlation_impact: number;
}

interface FlexPlayOptimizerProps {
  flexPick: {
    player_name: string;
    team: string;
    position: string;
    stat_type: string;
    flex_score: number;
  } | null;
  reason: string;
  allCandidates?: FlexCandidate[];
}

export default function FlexPlayOptimizer({
  flexPick,
  reason,
  allCandidates,
}: FlexPlayOptimizerProps) {
  if (!flexPick) {
    return (
      <View style={styles.card}>
        <Text style={styles.title}>Flex Play</Text>
        <Text style={styles.noFlex}>{reason}</Text>
      </View>
    );
  }

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>Flex Play</Text>
        <Ionicons name="swap-horizontal" size={16} color={theme.colors.primary} />
      </View>

      {/* Recommended flex */}
      <View style={styles.recommendedRow}>
        <View style={styles.flexBadge}>
          <Text style={styles.flexLabel}>FLEX</Text>
        </View>
        <View style={styles.playerInfo}>
          <Text style={styles.playerName}>{flexPick.player_name}</Text>
          <Text style={styles.playerMeta}>
            {flexPick.team} · {flexPick.position} · {flexPick.stat_type}
          </Text>
        </View>
        <Text style={styles.flexScore}>{Math.round(flexPick.flex_score)}</Text>
      </View>

      <Text style={styles.reason}>{reason}</Text>

      {/* Other candidates */}
      {allCandidates && allCandidates.length > 1 && (
        <View style={styles.candidates}>
          <Text style={styles.candidatesLabel}>Other options</Text>
          {allCandidates.slice(1, 3).map((c, i) => (
            <View key={i} style={styles.candidateRow}>
              <Text style={styles.candidateName}>{c.player_name}</Text>
              <Text style={styles.candidateScore}>{Math.round(c.flex_score)}</Text>
            </View>
          ))}
        </View>
      )}
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  title: {
    ...theme.typography.caption,
  },
  recommendedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 10,
  },
  flexBadge: {
    backgroundColor: theme.colors.primary,
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  flexLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: '#fff',
    letterSpacing: 1,
  },
  playerInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  playerMeta: {
    fontSize: 11,
    color: theme.colors.textSecondary,
  },
  flexScore: {
    fontSize: 18,
    fontWeight: '800',
    color: theme.colors.success,
  },
  reason: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    lineHeight: 16,
    marginBottom: 8,
  },
  noFlex: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
  },
  candidates: {
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    paddingTop: 8,
    gap: 4,
  },
  candidatesLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  candidateRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  candidateName: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  candidateScore: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.textSecondary,
  },
});
