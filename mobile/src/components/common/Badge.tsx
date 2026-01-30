/**
 * Badge Component
 * Reusable badge for status, risk levels, and featured items
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';

export type BadgeVariant = 'featured' | 'success' | 'warning' | 'danger' | 'info' | 'default';

interface BadgeProps {
  text: string;
  variant?: BadgeVariant;
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export default function Badge({
  text,
  variant = 'default',
  size = 'medium',
  style,
  textStyle,
}: BadgeProps) {
  const variantStyles = {
    featured: {
      backgroundColor: '#FCD34D',
      color: '#92400E',
    },
    success: {
      backgroundColor: '#22C55E',
      color: '#FFFFFF',
    },
    warning: {
      backgroundColor: '#F59E0B',
      color: '#FFFFFF',
    },
    danger: {
      backgroundColor: '#EF4444',
      color: '#FFFFFF',
    },
    info: {
      backgroundColor: '#3B82F6',
      color: '#FFFFFF',
    },
    default: {
      backgroundColor: '#6B7280',
      color: '#FFFFFF',
    },
  };

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
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
