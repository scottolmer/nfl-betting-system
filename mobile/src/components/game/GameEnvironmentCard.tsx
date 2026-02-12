/**
 * GameEnvironmentCard — Implied total, spread, pace context.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface GameEnvironmentProps {
  homeTeam: string;
  awayTeam: string;
  impliedTotal?: number;
  spread?: number;
  spreadFavor?: string;  // team abbreviation
  weather?: string;
  dome?: boolean;
}

function Pill({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <View style={styles.pill}>
      <Text style={styles.pillLabel}>{label}</Text>
      <Text style={[styles.pillValue, color ? { color } : null]}>{value}</Text>
    </View>
  );
}

function getTotalColor(total: number): string {
  if (total >= 50) return theme.colors.success;
  if (total >= 44) return theme.colors.primary;
  return theme.colors.danger;
}

export default function GameEnvironmentCard({
  homeTeam,
  awayTeam,
  impliedTotal,
  spread,
  spreadFavor,
  weather,
  dome,
}: GameEnvironmentProps) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>Game Environment</Text>
      <Text style={styles.matchup}>
        {awayTeam} @ {homeTeam}
      </Text>

      <View style={styles.pillRow}>
        {impliedTotal != null && (
          <Pill
            label="Total"
            value={impliedTotal.toString()}
            color={getTotalColor(impliedTotal)}
          />
        )}
        {spread != null && spreadFavor && (
          <Pill
            label="Spread"
            value={`${spreadFavor} ${spread > 0 ? '-' : '+'}${Math.abs(spread)}`}
          />
        )}
        {dome != null && (
          <Pill label="Venue" value={dome ? 'Dome' : 'Outdoor'} />
        )}
        {weather && !dome && (
          <Pill label="Weather" value={weather} />
        )}
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
    padding: 14,
    marginBottom: 12,
  },
  title: {
    ...theme.typography.caption,
    marginBottom: 4,
  },
  matchup: {
    fontSize: 15,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 10,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  pill: {
    backgroundColor: theme.colors.glassHigh,
    borderRadius: theme.borderRadius.s,
    paddingHorizontal: 10,
    paddingVertical: 6,
    alignItems: 'center',
  },
  pillLabel: {
    fontSize: 9,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  pillValue: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
});
