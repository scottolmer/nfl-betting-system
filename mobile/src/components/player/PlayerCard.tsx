/**
 * PlayerCard — Headshot, name, team, position.
 * Reusable across all three pillars.
 */

import React from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../../constants/theme';

interface PlayerCardProps {
  player: {
    name: string;
    team: string;
    position: string;
    headshot_url?: string | null;
  };
  subtitle?: string;
  rightContent?: React.ReactNode;
  onPress?: () => void;
  compact?: boolean;
}

function PlayerInitials({ name }: { name: string }) {
  const parts = name.split(' ');
  const initials = parts.length >= 2
    ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    : name.substring(0, 2).toUpperCase();

  return (
    <View style={styles.initialsCircle}>
      <Text style={styles.initialsText}>{initials}</Text>
    </View>
  );
}

export default function PlayerCard({ player, subtitle, rightContent, onPress, compact }: PlayerCardProps) {
  const Container = onPress ? TouchableOpacity : View;

  return (
    <Container
      style={[styles.card, compact && styles.cardCompact]}
      {...(onPress ? { onPress, activeOpacity: 0.7 } : {})}
    >
      {player.headshot_url ? (
        <Image
          source={{ uri: player.headshot_url }}
          style={[styles.headshot, compact && styles.headshotCompact]}
        />
      ) : (
        <PlayerInitials name={player.name} />
      )}
      <View style={styles.info}>
        <Text style={[styles.name, compact && styles.nameCompact]} numberOfLines={1}>
          {player.name}
        </Text>
        <Text style={styles.meta}>
          {player.team} · {player.position}
        </Text>
        {subtitle ? <Text style={styles.subtitle} numberOfLines={1}>{subtitle}</Text> : null}
      </View>
      {rightContent && <View style={styles.right}>{rightContent}</View>}
    </Container>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 12,
    marginBottom: 8,
  },
  cardCompact: {
    padding: 8,
    marginBottom: 4,
  },
  headshot: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: theme.colors.glassHigh,
    marginRight: 12,
  },
  headshotCompact: {
    width: 36,
    height: 36,
    borderRadius: 18,
    marginRight: 8,
  },
  initialsCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: theme.colors.glassHigh,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  initialsText: {
    color: theme.colors.textSecondary,
    fontSize: 16,
    fontWeight: '700',
  },
  info: {
    flex: 1,
  },
  name: {
    ...theme.typography.label,
    marginBottom: 2,
  },
  nameCompact: {
    fontSize: 13,
  },
  meta: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  subtitle: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  right: {
    marginLeft: 8,
    alignItems: 'flex-end',
  },
});
