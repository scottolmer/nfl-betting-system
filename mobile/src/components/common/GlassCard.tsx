/**
 * GlassCard — Reusable card with glassmorphism styling.
 * backgroundCard bg, glassBorder, borderRadius.m, card shadow.
 * Optional `glow` prop adds cyan border + shadow.
 */

import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { theme } from '../../constants/theme';

interface GlassCardProps {
  children: React.ReactNode;
  glow?: boolean;
  style?: ViewStyle;
  noPadding?: boolean;
  intensity?: number;
}

function GlassCard({ children, glow, style, noPadding }: GlassCardProps) {
  return (
    <View
      style={[
        styles.card,
        glow && styles.cardGlow,
        noPadding && styles.noPadding,
        style,
      ]}
    >
      {children}
    </View>
  );
}

export default React.memo(GlassCard);

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
    ...theme.shadows.card,
  },
  cardGlow: {
    borderColor: theme.colors.glassBorderActive,
    ...theme.shadows.glow,
  },
  noPadding: {
    padding: 0,
  },
});
