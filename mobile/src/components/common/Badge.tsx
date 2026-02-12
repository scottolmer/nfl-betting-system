/**
 * Badge Component
 * Reusable badge for status, risk levels, and featured items — dark theme
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { theme } from '../../constants/theme';

export type BadgeVariant = 'featured' | 'success' | 'warning' | 'danger' | 'info' | 'default';

interface BadgeProps {
  text: string;
  variant?: BadgeVariant;
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

const variantStyles: Record<BadgeVariant, { backgroundColor: string; color: string }> = {
  featured: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    color: theme.colors.gold,
  },
  success: {
    backgroundColor: theme.colors.successMuted,
    color: theme.colors.success,
  },
  warning: {
    backgroundColor: theme.colors.warningMuted,
    color: theme.colors.warning,
  },
  danger: {
    backgroundColor: theme.colors.dangerMuted,
    color: theme.colors.danger,
  },
  info: {
    backgroundColor: theme.colors.primaryMuted,
    color: theme.colors.primary,
  },
  default: {
    backgroundColor: 'rgba(148, 163, 184, 0.12)',
    color: theme.colors.textSecondary,
  },
};

export default function Badge({
  text,
  variant = 'default',
  size = 'medium',
  style,
  textStyle,
}: BadgeProps) {
  const sizeStyles = {
    small: {
      paddingHorizontal: 8,
      paddingVertical: 3,
      fontSize: 10,
    },
    medium: {
      paddingHorizontal: 10,
      paddingVertical: 5,
      fontSize: 11,
    },
    large: {
      paddingHorizontal: 12,
      paddingVertical: 6,
      fontSize: 12,
    },
  };

  const variantStyle = variantStyles[variant];
  const sizeStyle = sizeStyles[size];

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: variantStyle.backgroundColor,
          paddingHorizontal: sizeStyle.paddingHorizontal,
          paddingVertical: sizeStyle.paddingVertical,
        },
        style,
      ]}
    >
      <Text
        style={[
          styles.text,
          {
            color: variantStyle.color,
            fontSize: sizeStyle.fontSize,
          },
          textStyle,
        ]}
      >
        {text}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  text: {
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
