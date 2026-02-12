/**
 * DFSHomeScreen V2 — Cyan accent migration, gradient CTA, GlassCard usage.
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
import GlassCard from '../../components/common/GlassCard';
import AnimatedCard from '../../components/animated/AnimatedCard';

const PLATFORMS = [
  { key: 'prizepicks', label: 'PrizePicks', icon: 'trophy' as const },
  { key: 'underdog', label: 'Underdog', icon: 'paw' as const },
];

export default function DFSHomeScreen({ navigation }: any) {
  const [platform, setPlatform] = useState('prizepicks');
  const [currentWeek] = useState(13);

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
              color={platform === p.key ? '#000' : theme.colors.textSecondary}
            />
            <Text style={[styles.platformLabel, platform === p.key && styles.platformLabelActive]}>
              {p.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Build Parlay CTA */}
      <AnimatedCard index={0}>
        <TouchableOpacity
          style={styles.buildSlipCTA}
          onPress={() => navigation.navigate('SlipBuilder', { platform, week: currentWeek })}
          activeOpacity={0.8}
        >
          <View style={styles.ctaLeft}>
            <View style={styles.ctaIconCircle}>
              <Ionicons name="add" size={22} color="#000" />
            </View>
            <View>
              <Text style={styles.ctaTitle}>Build a Parlay</Text>
              <Text style={styles.ctaSubtitle}>
                Pick players with real-time correlation scoring
              </Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={20} color="rgba(0,0,0,0.4)" />
        </TouchableOpacity>
      </AnimatedCard>

      {/* Suggested Slips */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Suggested Parlays</Text>
        <TouchableOpacity
          onPress={() => navigation.navigate('SuggestedSlips', { platform, week: currentWeek })}
        >
          <Text style={styles.seeAll}>See All</Text>
        </TouchableOpacity>
      </View>

      <AnimatedCard index={1}>
        <GlassCard>
          <View style={styles.suggestedHeader}>
            <Ionicons name="flash" size={18} color={theme.colors.gold} />
            <Text style={styles.suggestedTitle}>Engine-Generated Parlays</Text>
          </View>
          <Text style={styles.suggestedDesc}>
            Optimized for highest confidence with lowest correlation risk.
            Our engine builds parlays using the same 6-agent analysis that
            achieves 55.7% win rate.
          </Text>
          <TouchableOpacity
            style={styles.suggestedFooter}
            onPress={() => navigation.navigate('SuggestedSlips', { platform, week: currentWeek })}
          >
            <Text style={styles.suggestedCTA}>View Suggestions</Text>
            <Ionicons name="arrow-forward" size={14} color={theme.colors.primary} />
          </TouchableOpacity>
        </GlassCard>
      </AnimatedCard>

      {/* How It Works */}
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
          <AnimatedCard key={i} index={i + 2}>
            <GlassCard style={styles.featureItem}>
              <View style={styles.featureIconCircle}>
                <Ionicons name={f.icon as any} size={18} color={theme.colors.primary} />
              </View>
              <Text style={styles.featureTitle}>{f.title}</Text>
              <Text style={styles.featureDesc}>{f.desc}</Text>
            </GlassCard>
          </AnimatedCard>
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
    color: theme.colors.primary,
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
    backgroundColor: theme.colors.backgroundCard,
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
    color: '#000',
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
    ...theme.shadows.glow,
  },
  ctaLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  ctaIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(0,0,0,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  ctaTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#000',
  },
  ctaSubtitle: {
    fontSize: 12,
    color: 'rgba(0,0,0,0.5)',
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
    width: '100%',
    marginBottom: 0,
  },
  featureIconCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.primaryMuted,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  featureDesc: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    lineHeight: 15,
  },
});
