/**
 * Help Banner Component
 * Dismissible contextual help banner shown on screens
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { bannerPreferences } from '../../services/userPreferences';
import { theme } from '../../constants/theme';

interface HelpBannerProps {
  bannerId: string;
  icon?: string;
  title: string;
  items?: string[];
  onDismiss?: () => void;
}

export default function HelpBanner({
  bannerId,
  icon = '💡',
  title,
  items = [],
  onDismiss,
}: HelpBannerProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    checkBannerStatus();
  }, [bannerId]);

  const checkBannerStatus = async () => {
    const isDismissed = await bannerPreferences.isBannerDismissed(bannerId);
    setVisible(!isDismissed);
  };

  const handleDismiss = async () => {
    await bannerPreferences.dismissBanner(bannerId);
    setVisible(false);
    if (onDismiss) {
      onDismiss();
    }
  };

  const handleDontShowAgain = async () => {
    await bannerPreferences.dismissBanner(bannerId);
    setVisible(false);
    if (onDismiss) {
      onDismiss();
    }
  };

  if (!visible) return null;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.icon}>{icon}</Text>
        <Text style={styles.title}>{title}</Text>
      </View>

      {items.length > 0 && (
        <View style={styles.itemsList}>
          {items.map((item, index) => (
            <Text key={index} style={styles.item}>
              {index + 1}. {item}
            </Text>
          ))}
        </View>
      )}

      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.dismissButton}
          onPress={handleDontShowAgain}
        >
          <Text style={styles.dismissText}>Don't show again</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.gotItButton} onPress={handleDismiss}>
          <Text style={styles.gotItText}>Got it</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.primaryMuted,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
    borderRadius: 8,
    padding: 16,
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  icon: {
    fontSize: 20,
    marginRight: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
    flex: 1,
  },
  itemsList: {
    marginBottom: 16,
    gap: 8,
  },
  item: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
  },
  dismissButton: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  dismissText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  gotItButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
  },
  gotItText: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
