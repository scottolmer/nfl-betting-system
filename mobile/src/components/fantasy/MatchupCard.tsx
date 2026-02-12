/**
 * MatchupCard — Your projected total vs opponent, win probability.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';

interface MatchupCardProps {
  userTotal: number;
  opponentTotal: number;
  winProbability: number;
  week: number;
  opponentName?: string;
}

export default function MatchupCard({
  userTotal,
  opponentTotal,
  winProbability,
  week,
  opponentName,
}: MatchupCardProps) {
  const margin = userTotal - opponentTotal;
  const isWinning = margin > 0;
  const marginColor = isWinning ? theme.colors.success : theme.colors.danger;

  const probColor =
    winProbability >= 60
      ? theme.colors.success
      : winProbability >= 45
      ? theme.colors.warning
      : theme.colors.danger;

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.label}>Week {week} Matchup</Text>
        <View style={[styles.probBadge, { backgroundColor: probColor + '20' }]}>
          <Text style={[styles.probText, { color: probColor }]}>
            {Math.round(winProbability)}% Win
          </Text>
        </View>
      </View>

      <View style={styles.matchupRow}>
        {/* Your team */}
        <View style={styles.teamCol}>
          <Text style={styles.teamLabel}>You</Text>
          <Text style={styles.teamScore}>{userTotal.toFixed(1)}</Text>
          <Text style={styles.teamUnit}>proj pts</Text>
        </View>

        {/* VS divider */}
        <View style={styles.vsCol}>
          <Text style={styles.vsText}>VS</Text>
          <View style={[styles.marginBadge, { backgroundColor: marginColor + '20' }]}>
            <Ionicons
              name={isWinning ? 'arrow-up' : 'arrow-down'}
              size={10}
              color={marginColor}
            />
            <Text style={[styles.marginText, { color: marginColor }]}>
              {Math.abs(margin).toFixed(1)}
            </Text>
          </View>
        </View>

        {/* Opponent */}
        <View style={styles.teamCol}>
          <Text style={styles.teamLabel}>{opponentName || 'Opponent'}</Text>
          <Text style={[styles.teamScore, styles.oppScore]}>{opponentTotal.toFixed(1)}</Text>
          <Text style={styles.teamUnit}>proj pts</Text>
        </View>
      </View>

      {/* Win probability bar */}
      <View style={styles.probBar}>
        <View style={[styles.probFill, { width: `${winProbability}%`, backgroundColor: probColor }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginBottom: 12,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  label: {
    ...theme.typography.caption,
  },
  probBadge: {
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  probText: {
    fontSize: 12,
    fontWeight: '700',
  },
  matchupRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  teamCol: {
    flex: 1,
    alignItems: 'center',
  },
  teamLabel: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  teamScore: {
    fontSize: 28,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  oppScore: {
    color: theme.colors.textSecondary,
  },
  teamUnit: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  vsCol: {
    alignItems: 'center',
    paddingHorizontal: 12,
  },
  vsText: {
    fontSize: 12,
    fontWeight: '800',
    color: theme.colors.textTertiary,
    marginBottom: 6,
  },
  marginBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
    gap: 3,
  },
  marginText: {
    fontSize: 11,
    fontWeight: '700',
  },
  probBar: {
    height: 4,
    backgroundColor: theme.colors.glassHigh,
    borderRadius: 2,
    overflow: 'hidden',
  },
  probFill: {
    height: '100%',
    borderRadius: 2,
  },
});
