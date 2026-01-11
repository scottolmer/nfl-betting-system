import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function BuildScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Parlay Builder</Text>
        <Text style={styles.headerSubtitle}>Build & Track Your Parlays</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderEmoji}>⚡</Text>
          <Text style={styles.placeholderTitle}>Parlay Builder Coming Soon</Text>
          <Text style={styles.placeholderDescription}>
            Create custom parlays with filters, save them, and track results.
          </Text>

          <View style={styles.featureList}>
            <Text style={styles.featureItem}>✅ Filter by teams, positions, confidence</Text>
            <Text style={styles.featureItem}>✅ Live combined confidence calculation</Text>
            <Text style={styles.featureItem}>✅ Line adjustment for Pick 6</Text>
            <Text style={styles.featureItem}>✅ Save unlimited parlays (Premium)</Text>
            <Text style={styles.featureItem}>✅ Auto-grading after games</Text>
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
