/**
 * AnimatedCard — Fade-in + slide-up entrance animation wrapper.
 * Uses React Native's built-in Animated API.
 */

import React, { useEffect, useRef } from 'react';
import { Animated, ViewStyle } from 'react-native';

interface AnimatedCardProps {
  children: React.ReactNode;
  index?: number;
  style?: ViewStyle;
}

export default function AnimatedCard({ children, index = 0, style }: AnimatedCardProps) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(16)).current;

  useEffect(() => {
    const delay = index * 60;
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 400,
        delay,
        useNativeDriver: true,
      }),
      Animated.spring(translateY, {
        toValue: 0,
        delay,
        useNativeDriver: true,
        damping: 15,
        stiffness: 120,
      }),
    ]).start();
  }, []);

  return (
    <Animated.View
      style={[
        style,
        { opacity, transform: [{ translateY }] },
      ]}
    >
      {children}
    </Animated.View>
  );
}
