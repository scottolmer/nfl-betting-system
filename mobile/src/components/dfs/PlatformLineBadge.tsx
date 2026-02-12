/**
 * PlatformLineBadge — Platform line vs sportsbook consensus comparison.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface PlatformLineBadgeProps {
  platformLine: number;
  consensusLine: number | null;
  platform?: string;
}

export default function PlatformLineBadge({
  platformLine,
  consensusLine,
  platform = 'PrizePicks',
}: PlatformLineBadgeProps) {
  const diff = consensusLine != null ? platformLine - consensusLine : null;
  const hasDiff = diff != null && Math.abs(diff) >= 0.5;

  return (
    <View style={styles.badge}>
      <View style={styles.lineRow}>
        <Text style={styles.platform}>{platform}</Text>
        <Text style={styles.line}>{platformLine}</Text>
      </View>

      {consensusLine != null && (
        <View style={styles.compRow}>
          <Text style={styles.compLabel}>Consensus</Text>
          <Text style={styles.compLine}>{consensusLine}</Text>
          {hasDiff && (
            <Text
              style={[
                styles.diffText,
                {
                  color: diff! > 0 ? theme.colors.danger : theme.colors.success,
                },
              ]}
            >
              {diff! > 0 ? '+' : ''}{diff!.toFixed(1)}
            </Text>
          )}
        </View>
      )}

      {hasDiff && (
        <Text style={styles.edgeHint}>
          {diff! > 0
            ? 'Platform line is higher — lean UNDER'
            : 'Platform line is lower — lean OVER'}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 10,
    marginBottom: 8,
  },
  lineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  platform: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  line: {
    fontSize: 16,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  compRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  compLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
  },
  compLine: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  diffText: {
    fontSize: 11,
    fontWeight: '800',
  },
  edgeHint: {
    fontSize: 10,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
    marginTop: 4,
  },
});
