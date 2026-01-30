/**
 * Results Screen
 * Track betting performance (coming soon)
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import ComingSoonCard from '../components/results/ComingSoonCard';
import InfoTooltip from '../components/common/InfoTooltip';

export default function ResultsScreen({ navigation }: any) {
  const handleNavigateToMyParlays = () => {
    navigation.navigate('My Parlays');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.headerTitle}>Results</Text>
            <Text style={styles.headerSubtitle}>Track Your Performance</Text>
          </View>
          <InfoTooltip tooltipKey="hitRate" iconSize={20} iconColor="#9CA3AF" />
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <ComingSoonCard onNavigateToMyParlays={handleNavigateToMyParlays} />
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
    paddingTop: 60,
    paddingBottom: 16,
    paddingHorizontal: 20,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  content: {
    paddingBottom: 20,
  },
});
