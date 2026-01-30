/**
 * Parlay Setup Step (Step 1)
 * Name your parlay and select sportsbook
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Sportsbook } from '../../types';
import InfoTooltip from '../common/InfoTooltip';

interface ParlaySetupStepProps {
  parlayName: string;
  onParlayNameChange: (name: string) => void;
  sportsbook: Sportsbook;
  onSportsbookChange: (sportsbook: Sportsbook) => void;
}

export default function ParlaySetupStep({
  parlayName,
  onParlayNameChange,
  sportsbook,
  onSportsbookChange,
}: ParlaySetupStepProps) {
  const sportsbooks: Sportsbook[] = [
    'DraftKings Pick 6',
    'FanDuel Pick 6',
    'Underdog Fantasy',
    'PrizePicks',
    'BetMGM',
    'Caesars',
    'ESPN Bet',
    'Other',
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Parlay Name</Text>
          <InfoTooltip tooltipKey="myParlays" iconSize={16} />
        </View>
        <Text style={styles.helpText}>
          Give your parlay a memorable name to easily find it later.
        </Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., Sunday Afternoon Slate"
          value={parlayName}
          onChangeText={onParlayNameChange}
          placeholderTextColor="#9CA3AF"
          autoFocus
        />
        <Text style={styles.exampleText}>
          Examples: "Week 17 Shootout", "QB Stack", "Monday Night Special"
        </Text>
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Select Sportsbook</Text>
          <InfoTooltip tooltipKey="sportsbook" iconSize={16} />
        </View>
        <Text style={styles.helpText}>
          Which platform will you be placing this parlay on?
        </Text>

        <View style={styles.sportsbooksGrid}>
          {sportsbooks.map((book) => (
            <TouchableOpacity
              key={book}
              style={[
                styles.sportsbookCard,
                sportsbook === book && styles.sportsbookCardSelected,
              ]}
              onPress={() => onSportsbookChange(book)}
            >
              {book === 'DraftKings Pick 6' && (
                <Text style={styles.recommendedBadge}>RECOMMENDED</Text>
              )}
              <Text
                style={[
                  styles.sportsbookText,
                  sportsbook === book && styles.sportsbookTextSelected,
                ]}
              >
                {book}
              </Text>
              {sportsbook === book && (
                <View style={styles.checkmarkContainer}>
                  <Text style={styles.checkmark}>✓</Text>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.infoBox}>
        <Text style={styles.infoIcon}>💡</Text>
        <View style={styles.infoContent}>
          <Text style={styles.infoTitle}>Why DraftKings Pick 6?</Text>
          <Text style={styles.infoText}>
            Pick 6 contests have better odds than traditional parlays and only require 2+ picks.
            Perfect for prop betting with guaranteed payouts.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  helpText: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
    lineHeight: 20,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    color: '#1F2937',
  },
  exampleText: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 8,
    fontStyle: 'italic',
  },
  sportsbooksGrid: {
    gap: 10,
  },
  sportsbookCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 16,
    position: 'relative',
  },
  sportsbookCardSelected: {
    borderColor: '#3B82F6',
    backgroundColor: '#EFF6FF',
  },
  recommendedBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    fontSize: 9,
    fontWeight: 'bold',
    color: '#F59E0B',
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  sportsbookText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4B5563',
  },
  sportsbookTextSelected: {
    color: '#3B82F6',
  },
  checkmarkContainer: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#3B82F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkmark: {
    fontSize: 14,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
    borderRadius: 8,
    padding: 16,
    marginTop: 8,
  },
  infoIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 13,
    color: '#4B5563',
    lineHeight: 18,
  },
});
