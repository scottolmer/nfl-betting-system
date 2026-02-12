/**
 * GameSlateCard — Full slate overview card, color-coded by implied total.
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';

interface GameSlateItem {
  home_team: string;
  implied_total?: number | null;
  pace?: string;
  dome?: boolean;
}

interface GameSlateCardProps {
  games: GameSlateItem[];
  week: number;
}

function getTotalColor(total: number | null | undefined): string {
  if (!total) return theme.colors.textTertiary;
  if (total >= 50) return '#22C55E';   // High scoring
  if (total >= 44) return '#3B82F6';   // Average
  return '#EF4444';                     // Low scoring
}

function getPaceIcon(pace: string | undefined): string {
  if (pace === 'fast') return 'flash';
  if (pace === 'slow') return 'time';
  return 'speedometer';
}

export default function GameSlateCard({ games, week }: GameSlateCardProps) {
  if (!games || games.length === 0) {
    return null;
  }

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Ionicons name="american-football" size={16} color={theme.colors.primary} />
        <Text style={styles.title}>Week {week} Slate</Text>
        <Text style={styles.gameCount}>{games.length} games</Text>
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {games.map((game, i) => {
          const totalColor = getTotalColor(game.implied_total);
          return (
            <View key={i} style={styles.gameChip}>
              <Text style={styles.teamText}>{game.home_team}</Text>
              {game.implied_total ? (
                <Text style={[styles.totalText, { color: totalColor }]}>
                  {game.implied_total.toFixed(0)}
                </Text>
              ) : (
                <Text style={styles.noTotal}>—</Text>
              )}
              <View style={styles.chipIcons}>
                {game.dome && (
                  <Ionicons name="home" size={9} color={theme.colors.textTertiary} />
                )}
                <Ionicons
                  name={getPaceIcon(game.pace) as any}
                  size={9}
                  color={
                    game.pace === 'fast'
                      ? theme.colors.success
                      : game.pace === 'slow'
                      ? theme.colors.danger
                      : theme.colors.textTertiary
                  }
                />
              </View>
            </View>
          );
        })}
      </ScrollView>

      {/* Legend */}
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#22C55E' }]} />
          <Text style={styles.legendText}>50+</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#3B82F6' }]} />
          <Text style={styles.legendText}>44-49</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#EF4444' }]} />
          <Text style={styles.legendText}>&lt;44</Text>
        </View>
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
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 10,
  },
  title: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    flex: 1,
  },
  gameCount: {
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  scrollContent: {
    gap: 8,
    paddingVertical: 2,
  },
  gameChip: {
    backgroundColor: theme.colors.glassHigh,
    borderRadius: 8,
    padding: 8,
    alignItems: 'center',
    minWidth: 56,
  },
  teamText: {
    fontSize: 11,
    fontWeight: '800',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  totalText: {
    fontSize: 16,
    fontWeight: '800',
  },
  noTotal: {
    fontSize: 14,
    color: theme.colors.textTertiary,
  },
  chipIcons: {
    flexDirection: 'row',
    gap: 4,
    marginTop: 3,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 14,
    marginTop: 10,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  legendText: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
});
