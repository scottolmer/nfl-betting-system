/**
 * MultiBookOddsTable — Book comparison table with best price highlighted.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';
import { BookOddsEntry } from '../../types';

interface MultiBookOddsTableProps {
  odds: BookOddsEntry[];
  direction?: 'OVER' | 'UNDER';
}

const BOOK_DISPLAY: Record<string, string> = {
  draftkings: 'DraftKings',
  fanduel: 'FanDuel',
  betmgm: 'BetMGM',
  caesars: 'Caesars',
  pointsbet: 'PointsBet',
  bet365: 'Bet365',
  bovada: 'Bovada',
  espnbet: 'ESPN Bet',
};

function formatOdds(price: number | null): string {
  if (price == null) return '--';
  return price > 0 ? `+${price}` : `${price}`;
}

export default function MultiBookOddsTable({ odds, direction }: MultiBookOddsTableProps) {
  if (!odds || odds.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No odds available</Text>
      </View>
    );
  }

  // Find best over and under prices
  const bestOver = odds.reduce<number | null>((best, o) => {
    if (o.over_price == null) return best;
    return best == null || o.over_price > best ? o.over_price : best;
  }, null);
  const bestUnder = odds.reduce<number | null>((best, o) => {
    if (o.under_price == null) return best;
    return best == null || o.under_price > best ? o.under_price : best;
  }, null);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Multi-Book Odds</Text>
      {/* Header */}
      <View style={styles.headerRow}>
        <Text style={[styles.headerCell, styles.bookCol]}>Book</Text>
        <Text style={[styles.headerCell, styles.lineCol]}>Line</Text>
        <Text style={[styles.headerCell, styles.priceCol]}>Over</Text>
        <Text style={[styles.headerCell, styles.priceCol]}>Under</Text>
      </View>
      {/* Rows */}
      {odds.map((o, i) => {
        const isOverBest = o.over_price === bestOver && bestOver != null;
        const isUnderBest = o.under_price === bestUnder && bestUnder != null;

        return (
          <View key={`${o.bookmaker}-${i}`} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
            <Text style={[styles.cell, styles.bookCol]} numberOfLines={1}>
              {BOOK_DISPLAY[o.bookmaker] || o.bookmaker}
            </Text>
            <Text style={[styles.cell, styles.lineCol]}>{o.line}</Text>
            <Text
              style={[
                styles.cell,
                styles.priceCol,
                isOverBest && styles.bestPrice,
                direction === 'OVER' && isOverBest && styles.bestPriceHighlight,
              ]}
            >
              {formatOdds(o.over_price)}
            </Text>
            <Text
              style={[
                styles.cell,
                styles.priceCol,
                isUnderBest && styles.bestPrice,
                direction === 'UNDER' && isUnderBest && styles.bestPriceHighlight,
              ]}
            >
              {formatOdds(o.under_price)}
            </Text>
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
    marginBottom: 10,
  },
  headerRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
    paddingBottom: 6,
    marginBottom: 4,
  },
  headerCell: {
    fontSize: 10,
    fontWeight: '700',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  row: {
    flexDirection: 'row',
    paddingVertical: 6,
  },
  rowAlt: {
    backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 4,
  },
  cell: {
    fontSize: 13,
    color: theme.colors.textPrimary,
    fontWeight: '500',
  },
  bookCol: {
    flex: 2,
  },
  lineCol: {
    flex: 1,
    textAlign: 'center',
  },
  priceCol: {
    flex: 1,
    textAlign: 'right',
  },
  bestPrice: {
    fontWeight: '800',
  },
  bestPriceHighlight: {
    color: theme.colors.success,
  },
  empty: {
    padding: 20,
    alignItems: 'center',
  },
  emptyText: {
    color: theme.colors.textTertiary,
    fontSize: 13,
  },
});
