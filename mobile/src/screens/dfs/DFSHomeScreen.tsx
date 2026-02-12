/**
 * DFSHomeScreen — Platform selector, "Build Slip" CTA, suggested slips, active slips.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';

const PLATFORMS = [
  { key: 'prizepicks', label: 'PrizePicks', icon: 'trophy' as const },
  { key: 'underdog', label: 'Underdog', icon: 'paw' as const },
];

export default function DFSHomeScreen({ navigation }: any) {
  const [platform, setPlatform] = useState('prizepicks');
  const [currentWeek] = useState(17);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>DFS</Text>
        <Text style={styles.headerSubtitle}>Week {currentWeek}</Text>
      </View>

      {/* Platform Selector */}
      <View style={styles.platformRow}>
        {PLATFORMS.map((p) => (
          <TouchableOpacity
            key={p.key}
            style={[styles.platformCard, platform === p.key && styles.platformCardActive]}
            onPress={() => setPlatform(p.key)}
            activeOpacity={0.7}
          >
            <Ionicons
              name={p.icon}
              size={20}
              color={platform === p.key ? '#fff' : theme.colors.textSecondary}
            />
            <Text style={[styles.platformLabel, platform === p.key && styles.platformLabelActive]}>
              {p.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Build Slip CTA */}
      <TouchableOpacity
        style={styles.buildSlipCTA}
        onPress={() => navigation.navigate('SlipBuilder', { platform, week: currentWeek })}
        activeOpacity={0.8}
      >
        <View style={styles.ctaLeft}>
          <Ionicons name="add-circle" size={28} color="#fff" />
          <View>
            <Text style={styles.ctaTitle}>Build a Slip</Text>
            <Text style={styles.ctaSubtitle}>
              Pick players with real-time correlation scoring
            </Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={20} color="rgba(255,255,255,0.6)" />
      </TouchableOpacity>

      {/* Suggested Slips */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Suggested Slips</Text>
        <TouchableOpacity
          onPress={() => navigation.navigate('SuggestedSlips', { platform, week: currentWeek })}
        >
          <Text style={styles.seeAll}>See All</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.suggestedCard}
        onPress={() => navigation.navigate('SuggestedSlips', { platform, week: currentWeek })}
        activeOpacity={0.7}
      >
        <View style={styles.suggestedHeader}>
          <Ionicons name="flash" size={18} color={theme.colors.gold} />
          <Text style={styles.suggestedTitle}>Engine-Generated Slips</Text>
        </View>
        <Text style={styles.suggestedDesc}>
          Optimized for highest confidence with lowest correlation risk.
          Our engine builds slips using the same 6-agent analysis that
          achieves 55.7% win rate.
        </Text>
        <View style={styles.suggestedFooter}>
          <Text style={styles.suggestedCTA}>View Suggestions</Text>
          <Ionicons name="arrow-forward" size={14} color={theme.colors.primary} />
        </View>
      </TouchableOpacity>

      {/* Quick Stats */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>How It Works</Text>
      </View>

      <View style={styles.featureGrid}>
        {[
          { icon: 'search', title: 'Browse Players', desc: 'Search by name, team, or position' },
          { icon: 'git-compare', title: 'Correlation Check', desc: 'Real-time risk scoring as you build' },
          { icon: 'swap-horizontal', title: 'Flex Optimizer', desc: 'Auto-suggest the optimal flex pick' },
          { icon: 'analytics', title: 'Line Comparison', desc: 'Platform vs sportsbook consensus' },
        ].map((f, i) => (
          <View key={i} style={styles.featureItem}>
            <Ionicons name={f.icon as any} size={20} color={theme.colors.primary} />
            <Text style={styles.featureTitle}>{f.title}</Text>
            <Text style={styles.featureDesc}>{f.desc}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    paddingBottom: 40,
  },
  header: {
    paddingTop: 16,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  headerTitle: {
    ...theme.typography.h1,
  },
  headerSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  platformRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 10,
    marginBottom: 16,
  },
  platformCard: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingVertical: 14,
  },
  platformCardActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  platformLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textSecondary,
  },
  platformLabelActive: {
    color: '#fff',
  },
  buildSlipCTA: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.m,
    padding: 18,
    marginHorizontal: 16,
    marginBottom: 20,
  },
  ctaLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  ctaTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#fff',
  },
  ctaSubtitle: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 2,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  sectionTitle: {
    ...theme.typography.h3,
  },
  seeAll: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  suggestedCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 20,
  },
  suggestedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  suggestedTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  suggestedDesc: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
    marginBottom: 10,
  },
  suggestedFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  suggestedCTA: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  featureGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 10,
  },
  featureItem: {
    width: '47%',
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
  },
  featureTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginTop: 8,
    marginBottom: 2,
  },
  featureDesc: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    lineHeight: 15,
  },
});
