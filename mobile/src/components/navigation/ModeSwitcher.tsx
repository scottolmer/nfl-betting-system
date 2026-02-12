/**
 * ModeSwitcher V2 — DFS / Props / Fantasy toggle with animated sliding indicator.
 * Active tab: cyan bg. Animated spring indicator bar.
 */

import React, { useRef, useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Animated, LayoutChangeEvent } from 'react-native';
import { theme } from '../../constants/theme';
import { useMode } from '../../contexts/ModeContext';
import { AppMode } from '../../types';

const MODES: { key: AppMode; label: string }[] = [
  { key: 'props', label: 'Props' },
  { key: 'fantasy', label: 'Fantasy' },
];

interface ModeSwitcherProps {
  onModeChange?: (mode: AppMode) => void;
}

export default function ModeSwitcher({ onModeChange }: ModeSwitcherProps) {
  const { mode, setMode } = useMode();
  const indicatorX = useRef(new Animated.Value(0)).current;
  const [measuredTabWidth, setMeasuredTabWidth] = useState(0);

  const handleTabLayout = (event: LayoutChangeEvent, index: number) => {
    const { width } = event.nativeEvent.layout;
    if (measuredTabWidth === 0) {
      setMeasuredTabWidth(width);
      // Set initial position without animation
      const activeIndex = MODES.findIndex((m) => m.key === mode);
      indicatorX.setValue(activeIndex * width);
    }
  };

  const handleTabPress = (key: AppMode, index: number) => {
    setMode(key);
    onModeChange?.(key);
    Animated.spring(indicatorX, {
      toValue: index * measuredTabWidth,
      damping: theme.animation.spring.damping,
      stiffness: theme.animation.spring.stiffness,
      useNativeDriver: true,
    }).start();
  };

  // Update indicator when mode changes externally
  useEffect(() => {
    if (measuredTabWidth > 0) {
      const activeIndex = MODES.findIndex((m) => m.key === mode);
      Animated.spring(indicatorX, {
        toValue: activeIndex * measuredTabWidth,
        damping: theme.animation.spring.damping,
        stiffness: theme.animation.spring.stiffness,
        useNativeDriver: true,
      }).start();
    }
  }, [mode, measuredTabWidth]);

  return (
    <View style={styles.container}>
      {/* Animated indicator */}
      <Animated.View
        style={[
          styles.indicator,
          {
            transform: [{ translateX: indicatorX }],
            width: measuredTabWidth || '50%',
          },
        ]}
      />

      {MODES.map(({ key, label }, index) => {
        const isActive = mode === key;
        return (
          <TouchableOpacity
            key={key}
            style={styles.tab}
            onPress={() => handleTabPress(key, index)}
            onLayout={(e) => handleTabLayout(e, index)}
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
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: theme.borderRadius.pill,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 3,
    marginHorizontal: 60,
    position: 'relative',
  },
  indicator: {
    position: 'absolute',
    top: 3,
    left: 3,
    bottom: 3,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.pill,
  },
  tab: {
    flex: 1,
    paddingVertical: 7,
    borderRadius: theme.borderRadius.pill,
    alignItems: 'center',
    zIndex: 1,
  },
  tabText: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textSecondary,
  },
  tabTextActive: {
    color: '#000',
  },
});
