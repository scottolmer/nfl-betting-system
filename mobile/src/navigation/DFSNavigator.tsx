/**
 * DFSNavigator — Placeholder stack for DFS mode (Sprint 3).
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';

function DFSComingSoon() {
  return (
    <View style={styles.container}>
      <Ionicons name="construct-outline" size={48} color={theme.colors.textTertiary} />
      <Text style={styles.title}>DFS Mode</Text>
      <Text style={styles.subtitle}>Coming Soon</Text>
      <Text style={styles.description}>
        Build optimized DFS slips with correlation scoring, flex play optimization,
        and platform line comparisons. Powered by the same engine.
      </Text>
    </View>
  );
}

export default function DFSNavigator() {
  return <DFSComingSoon />;
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
