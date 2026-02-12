/**
 * RosterSlot — Position label + player mini-card + projection.
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../../constants/theme';

interface RosterSlotProps {
  slot: string; // QB, RB, WR, TE, FLEX, K, DEF, BN
  playerName?: string;
  team?: string;
  position?: string;
  fantasyPoints?: number;
  confidence?: number;
  floor?: number;
  ceiling?: number;
  verdict?: 'START' | 'SIT' | 'FLEX';
  onPress?: () => void;
  empty?: boolean;
}

const SLOT_COLORS: Record<string, string> = {
  QB: '#FF6B6B',
  RB: '#4ECDC4',
  WR: '#45B7D1',
  TE: '#FFA07A',
  FLEX: '#9B59B6',
  K: '#95A5A6',
  DEF: '#2C3E50',
  BN: theme.colors.textTertiary,
};

export default function RosterSlot({
  slot,
  playerName,
  team,
  position,
  fantasyPoints,
  confidence,
  floor,
  ceiling,
  verdict,
  onPress,
  empty,
}: RosterSlotProps) {
  const slotColor = SLOT_COLORS[slot] || theme.colors.textTertiary;

  const verdictColor =
    verdict === 'START'
      ? theme.colors.success
      : verdict === 'SIT'
      ? theme.colors.danger
      : theme.colors.warning;

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
      disabled={!onPress}
    >
      {/* Slot badge */}
      <View style={[styles.slotBadge, { backgroundColor: slotColor + '30' }]}>
        <Text style={[styles.slotText, { color: slotColor }]}>{slot}</Text>
      </View>

      {/* Player info */}
      <View style={styles.playerInfo}>
        {empty ? (
          <Text style={styles.emptyText}>Empty</Text>
        ) : (
          <>
            <Text style={styles.playerName} numberOfLines={1}>
              {playerName || 'Unknown'}
            </Text>
            <Text style={styles.playerMeta}>
              {team} · {position}
            </Text>
          </>
        )}
      </View>

      {/* Projection + verdict */}
      {!empty && (
        <View style={styles.rightSection}>
          <Text style={styles.fantasyPoints}>
            {fantasyPoints != null ? fantasyPoints.toFixed(1) : '—'}
          </Text>
          {floor != null && ceiling != null && (
            <Text style={styles.range}>
              {floor.toFixed(0)}–{ceiling.toFixed(0)}
            </Text>
          )}
          {verdict && (
            <View style={[styles.verdictBadge, { backgroundColor: verdictColor + '20' }]}>
              <Text style={[styles.verdictText, { color: verdictColor }]}>{verdict}</Text>
            </View>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 10,
    marginBottom: 6,
    gap: 10,
  },
  slotBadge: {
    width: 40,
    height: 28,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
  },
  slotText: {
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.5,
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
    color: theme.colors.textTertiary,
    marginTop: 1,
  },
  emptyText: {
    fontSize: 13,
    color: theme.colors.textTertiary,
    fontStyle: 'italic',
  },
  rightSection: {
    alignItems: 'flex-end',
  },
  fantasyPoints: {
    fontSize: 16,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  range: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    marginTop: 1,
  },
  verdictBadge: {
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 1,
    marginTop: 3,
  },
  verdictText: {
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
});
