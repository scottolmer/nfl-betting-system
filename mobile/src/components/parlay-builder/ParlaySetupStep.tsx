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
import { theme } from '../../constants/theme';

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
          placeholderTextColor={theme.colors.textTertiary}
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
    backgroundColor: theme.colors.backgroundElevated,
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
    color: theme.colors.textPrimary,
  },
  helpText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 12,
    lineHeight: 20,
  },
  input: {
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    color: theme.colors.textPrimary,
  },
  exampleText: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    marginTop: 8,
    fontStyle: 'italic',
  },
  sportsbooksGrid: {
    gap: 10,
  },
  sportsbookCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 2,
    borderColor: theme.colors.glassBorder,
    borderRadius: 12,
    padding: 16,
    position: 'relative',
  },
  sportsbookCardSelected: {
    borderColor: theme.colors.primary,
    backgroundColor: theme.colors.primaryMuted,
  },
  recommendedBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    fontSize: 9,
    fontWeight: 'bold',
    color: theme.colors.gold,
    backgroundColor: theme.colors.warningMuted,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  sportsbookText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  sportsbookTextSelected: {
    color: theme.colors.primary,
  },
  checkmarkContainer: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: theme.colors.primary,
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
    backgroundColor: theme.colors.primaryMuted,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
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
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  infoText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
  },
});
