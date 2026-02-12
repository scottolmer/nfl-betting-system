import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { theme } from '../constants/theme';

export default function MyBetsScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Bets</Text>
        <Text style={styles.headerSubtitle}>Track Your Performance</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderTitle}>Bet Tracking Coming Soon</Text>
          <Text style={styles.placeholderDescription}>
            Automatically track your parlay results and analyze performance.
          </Text>

          <View style={styles.featureList}>
            <Text style={styles.featureItem}>Auto-graded results (Sunday night)</Text>
            <Text style={styles.featureItem}>"Why it hit/miss" analysis</Text>
            <Text style={styles.featureItem}>Win rate by confidence tier</Text>
            <Text style={styles.featureItem}>Agent accuracy tracking</Text>
            <Text style={styles.featureItem}>ROI and bankroll management</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    backgroundColor: theme.colors.backgroundCard,
    padding: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: theme.colors.primary,
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  content: {
    padding: 20,
  },
  placeholderContainer: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 24,
    alignItems: 'center',
    ...theme.shadows.card,
  },
  placeholderTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 8,
    textAlign: 'center',
  },
  placeholderDescription: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 24,
  },
  featureList: {
    alignSelf: 'stretch',
  },
  featureItem: {
    fontSize: 15,
    color: theme.colors.textSecondary,
    marginBottom: 8,
  },
});
