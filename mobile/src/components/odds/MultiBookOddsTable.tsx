/**
 * MultiBookOddsTable V2 — Card-per-book rows instead of striped table.
 * Best price gets cyan glow border + "BEST" badge.
 * Over/under prices green/red colored.
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

  const bestOver = odds.reduce<number | null>((best, o) => {
    if (o.over_price == null) return best;
    return best == null || o.over_price > best ? o.over_price : best;
  }, null);
  const bestUnder = odds.reduce<number | null>((best, o) => {
    if (o.under_price == null) return best;
    return best == null || o.under_price > best ? o.under_price : best;
  }, null);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>MULTI-BOOK ODDS</Text>
      {odds.map((o, i) => {
        const isOverBest = o.over_price === bestOver && bestOver != null;
        const isUnderBest = o.under_price === bestUnder && bestUnder != null;
        const isBestForDirection =
          (direction === 'OVER' && isOverBest) || (direction === 'UNDER' && isUnderBest);

        return (
          <View
            key={`${o.bookmaker}-${i}`}
            style={[styles.bookCard, isBestForDirection && styles.bookCardBest]}
          >
            <View style={styles.bookHeader}>
              <Text style={styles.bookName}>
                {BOOK_DISPLAY[o.bookmaker] || o.bookmaker}
              </Text>
              {isBestForDirection && (
                <View style={styles.bestBadge}>
                  <Text style={styles.bestText}>BEST</Text>
                </View>
              )}
            </View>
            <View style={styles.pricesRow}>
              <View style={styles.lineBox}>
                <Text style={styles.lineLabel}>Line</Text>
                <Text style={styles.lineValue}>{o.line}</Text>
              </View>
              <View style={styles.priceBox}>
                <Text style={styles.priceLabel}>Over</Text>
                <Text
                  style={[
                    styles.priceValue,
                    { color: theme.colors.success },
                    isOverBest && styles.bestPriceValue,
                  ]}
                >
                  {formatOdds(o.over_price)}
                </Text>
              </View>
              <View style={styles.priceBox}>
                <Text style={styles.priceLabel}>Under</Text>
                <Text
                  style={[
                    styles.priceValue,
                    { color: theme.colors.danger },
                    isUnderBest && styles.bestPriceValue,
                  ]}
                >
                  {formatOdds(o.under_price)}
                </Text>
              </View>
            </View>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 12,
  },
  title: {
    ...theme.typography.caption,
    marginBottom: 10,
  },
  bookCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 12,
    marginBottom: 8,
  },
  bookCardBest: {
    borderColor: theme.colors.glassBorderActive,
    ...theme.shadows.glow,
  },
  bookHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  bookName: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  bestBadge: {
    backgroundColor: theme.colors.primaryMuted,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  bestText: {
    fontSize: 9,
    fontWeight: '800',
    color: theme.colors.primary,
    letterSpacing: 0.5,
  },
  pricesRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  lineBox: {
    alignItems: 'center',
    flex: 1,
  },
  priceBox: {
    alignItems: 'center',
    flex: 1,
  },
  lineLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  priceLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  lineValue: {
    fontSize: 16,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  priceValue: {
    fontSize: 16,
    fontWeight: '700',
  },
  bestPriceValue: {
    fontWeight: '800',
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
