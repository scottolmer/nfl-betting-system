import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function MyBetsScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Bets</Text>
        <Text style={styles.headerSubtitle}>Track Your Performance</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderEmoji}>📊</Text>
          <Text style={styles.placeholderTitle}>Bet Tracking Coming Soon</Text>
          <Text style={styles.placeholderDescription}>
            Automatically track your parlay results and analyze performance.
          </Text>

          <View style={styles.featureList}>
            <Text style={styles.featureItem}>✅ Auto-graded results (Sunday night)</Text>
            <Text style={styles.featureItem}>✅ "Why it hit/miss" analysis</Text>
            <Text style={styles.featureItem}>✅ Win rate by confidence tier</Text>
            <Text style={styles.featureItem}>✅ Agent accuracy tracking</Text>
            <Text style={styles.featureItem}>✅ ROI and bankroll management</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#1F2937',
    padding: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  content: {
    padding: 20,
  },
  placeholderContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  placeholderEmoji: {
    fontSize: 64,
    marginBottom: 16,
  },
  placeholderTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  placeholderDescription: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
  },
  featureList: {
    alignSelf: 'stretch',
  },
  featureItem: {
    fontSize: 15,
    color: '#4B5563',
    marginBottom: 8,
  },
});
