/**
 * ModeSwitcher — DFS / Props / Fantasy toggle at top of app.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';
import { useMode } from '../../contexts/ModeContext';
import { AppMode } from '../../types';

const MODES: { key: AppMode; label: string }[] = [
  { key: 'dfs', label: 'DFS' },
  { key: 'props', label: 'Props' },
  { key: 'fantasy', label: 'Fantasy' },
];

export default function ModeSwitcher() {
  const { mode, setMode } = useMode();

  return (
    <View style={styles.container}>
      {MODES.map(({ key, label }) => {
        const isActive = mode === key;
        return (
          <TouchableOpacity
            key={key}
            style={[styles.tab, isActive && styles.tabActive]}
            onPress={() => setMode(key)}
            activeOpacity={0.7}
          >
            <Text style={[styles.tabText, isActive && styles.tabTextActive]}>
              {label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.pill,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 3,
    marginHorizontal: 60,
  },
  tab: {
    flex: 1,
    paddingVertical: 6,
    borderRadius: theme.borderRadius.pill,
    alignItems: 'center',
  },
  tabActive: {
    backgroundColor: theme.colors.primary,
  },
  tabText: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textSecondary,
  },
  tabTextActive: {
    color: '#fff',
  },
});
