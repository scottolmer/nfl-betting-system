/**
 * FantasyNavigator — Placeholder stack for Fantasy mode (Sprint 4).
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';

function FantasyComingSoon() {
  return (
    <View style={styles.container}>
      <Ionicons name="trophy-outline" size={48} color={theme.colors.textTertiary} />
      <Text style={styles.title}>Fantasy Mode</Text>
      <Text style={styles.subtitle}>Coming Soon</Text>
      <Text style={styles.description}>
        Import your Sleeper roster, get start/sit advice, waiver wire rankings,
        matchup heatmaps, and trade analysis — all powered by the same engine.
      </Text>
    </View>
  );
}

export default function FantasyNavigator() {
  return <FantasyComingSoon />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    paddingHorizontal: 40,
  },
  title: {
    ...theme.typography.h2,
    marginTop: 16,
  },
  subtitle: {
    fontSize: 14,
    color: theme.colors.primary,
    fontWeight: '700',
    marginTop: 4,
    marginBottom: 12,
  },
  description: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
});
