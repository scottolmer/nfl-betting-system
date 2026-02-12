/**
 * ParlayDetailScreen — Shows full AI-generated parlay with each leg as a
 * tappable card that navigates to PropDetail for deep analysis.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { Parlay, ParlayLeg } from '../../types';
import GlassCard from '../../components/common/GlassCard';
import AnimatedCard from '../../components/animated/AnimatedCard';

function getRiskColor(risk: string): string {
  switch (risk) {
    case 'LOW': return theme.colors.success;
    case 'MEDIUM': return theme.colors.gold;
    case 'HIGH': return theme.colors.danger;
    default: return theme.colors.textSecondary;
  }
}

function getConfidenceColor(conf: number): string {
  if (conf >= 70) return theme.colors.success;
  if (conf >= 60) return theme.colors.primary;
  if (conf >= 50) return theme.colors.gold;
  return theme.colors.danger;
}

export default function ParlayDetailScreen({ route, navigation }: any) {
  const { parlay, week } = route.params as { parlay: Parlay; week: number };
  const [activeTab, setActiveTab] = useState(0);
  const riskColor = getRiskColor(parlay.risk_level);

  const handleLegPress = (leg: ParlayLeg) => {
    // Build a PropAnalysis-compatible object from the parlay leg
    navigation.navigate('PropDetail', {
      prop: {
        player_name: leg.player_name,
        team: leg.team,
        position: inferPosition(leg.stat_type),
        stat_type: leg.stat_type,
        bet_type: leg.bet_type,
        line: leg.line,
        opponent: leg.opponent,
        confidence: leg.confidence,
        agent_breakdown: {},
        top_reasons: [],
      },
      week,
    });
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Parlay Detail</Text>
        <View style={styles.backBtn} />
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Summary card */}
        <AnimatedCard index={0}>
          <GlassCard glow={parlay.combined_confidence >= 70}>
            <View style={styles.summaryRow}>
              <View style={styles.summaryItem}>
                <Text style={[styles.summaryValue, { color: getConfidenceColor(parlay.combined_confidence) }]}>
                  {Math.round(parlay.combined_confidence)}
                </Text>
                <Text style={styles.summaryLabel}>Combined</Text>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Text style={styles.summaryValue}>{parlay.leg_count}</Text>
                <Text style={styles.summaryLabel}>Legs</Text>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <View style={styles.riskRow}>
                  <View style={[styles.riskDot, { backgroundColor: riskColor }]} />
                  <Text style={[styles.summaryValue, { color: riskColor, fontSize: 16 }]}>
                    {parlay.risk_level}
                  </Text>
                </View>
                <Text style={styles.summaryLabel}>Risk</Text>
              </View>
            </View>
          </GlassCard>
        </AnimatedCard>

        {/* Rationale */}
        {parlay.rationale && (
          <AnimatedCard index={1}>
            <GlassCard>
              <View style={styles.rationaleRow}>
                <Ionicons name="bulb" size={16} color={theme.colors.gold} />
                <Text style={styles.rationaleTitle}>AI Reasoning</Text>
              </View>
              <Text style={styles.rationaleText}>{parlay.rationale}</Text>
            </GlassCard>
          </AnimatedCard>
        )}

        {/* Player tabs */}
        <View style={styles.tabsContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabsScroll}>
            {parlay.legs.map((leg, i) => {
              const isActive = activeTab === i;
              return (
                <TouchableOpacity
                  key={i}
                  style={[styles.tab, isActive && styles.tabActive]}
                  onPress={() => setActiveTab(i)}
                  activeOpacity={0.7}
                >
                  <Text style={[styles.tabName, isActive && styles.tabNameActive]} numberOfLines={1}>
                    {formatName(leg.player_name)}
                  </Text>
                  <Text style={[styles.tabConf, isActive && styles.tabConfActive]}>
                    {Math.round(leg.confidence)}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        </View>

        {/* Active leg detail */}
        {parlay.legs[activeTab] && (
          <AnimatedCard index={2} key={activeTab}>
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={() => handleLegPress(parlay.legs[activeTab])}
            >
              <GlassCard>
                <LegDetail leg={parlay.legs[activeTab]} />
                <View style={styles.viewDetailRow}>
                  <Text style={styles.viewDetailText}>View full analysis</Text>
                  <Ionicons name="arrow-forward" size={14} color={theme.colors.primary} />
                </View>
              </GlassCard>
            </TouchableOpacity>
          </AnimatedCard>
        )}

        {/* All legs overview */}
        <Text style={styles.sectionLabel}>ALL LEGS</Text>
        {parlay.legs.map((leg, i) => (
          <AnimatedCard index={3 + i} key={i}>
            <TouchableOpacity activeOpacity={0.8} onPress={() => handleLegPress(leg)}>
              <GlassCard>
                <View style={styles.legRow}>
                  <View style={styles.legLeft}>
                    <Text style={styles.legNumber}>{i + 1}</Text>
                  </View>
                  <View style={styles.legMiddle}>
                    <Text style={styles.legPlayer} numberOfLines={1}>
                      {leg.player_name}
                    </Text>
                    <Text style={styles.legMeta}>
                      {leg.team} vs {leg.opponent}
                    </Text>
                    <View style={styles.legPropRow}>
                      <View style={[styles.directionBadge, {
                        backgroundColor: leg.bet_type === 'OVER' ? theme.colors.successMuted : theme.colors.dangerMuted,
                      }]}>
                        <Text style={[styles.directionText, {
                          color: leg.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger,
                        }]}>
                          {leg.bet_type}
                        </Text>
                      </View>
                      <Text style={styles.legStatLine}>
                        {leg.stat_type} {leg.line}
                      </Text>
                    </View>
                  </View>
                  <View style={styles.legRight}>
                    <Text style={[styles.legConfidence, { color: getConfidenceColor(leg.confidence) }]}>
                      {Math.round(leg.confidence)}
                    </Text>
                    <Ionicons name="chevron-forward" size={14} color={theme.colors.textTertiary} />
                  </View>
                </View>
              </GlassCard>
            </TouchableOpacity>
          </AnimatedCard>
        ))}
      </ScrollView>
    </View>
  );
}

/** Expanded detail for the active tab's leg */
function LegDetail({ leg }: { leg: ParlayLeg }) {
  const confColor = getConfidenceColor(leg.confidence);

  return (
    <View>
      <View style={styles.detailHeader}>
        <View>
          <Text style={styles.detailName}>{leg.player_name}</Text>
          <Text style={styles.detailTeam}>{leg.team} vs {leg.opponent}</Text>
        </View>
        <View style={styles.detailConfBox}>
          <Text style={[styles.detailConfScore, { color: confColor }]}>
            {Math.round(leg.confidence)}
          </Text>
          <Text style={styles.detailConfLabel}>CONF</Text>
        </View>
      </View>

      <View style={styles.detailPropRow}>
        <View style={styles.detailStatBox}>
          <Text style={styles.detailStatLabel}>STAT</Text>
          <Text style={styles.detailStatValue}>{leg.stat_type}</Text>
        </View>
        <View style={styles.detailStatBox}>
          <Text style={styles.detailStatLabel}>LINE</Text>
          <Text style={styles.detailStatValue}>{leg.line}</Text>
        </View>
        <View style={styles.detailStatBox}>
          <Text style={styles.detailStatLabel}>DIRECTION</Text>
          <View style={[styles.directionBadgeLg, {
            backgroundColor: leg.bet_type === 'OVER' ? theme.colors.successMuted : theme.colors.dangerMuted,
          }]}>
            <Text style={[styles.directionTextLg, {
              color: leg.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger,
            }]}>
              {leg.bet_type}
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
}

function formatName(name: string): string {
  return name
    .split(' ')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function inferPosition(statType: string): string {
  const s = statType.toLowerCase();
  if (s.includes('pass') || s.includes('completion')) return 'QB';
  if (s.includes('rush')) return 'RB';
  if (s.includes('rec') || s.includes('reception')) return 'WR';
  return 'FLEX';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 56,
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    ...theme.typography.h3,
  },
  scroll: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  // Summary
  summaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 22,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  summaryLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
    marginTop: 2,
  },
  summaryDivider: {
    width: 1,
    height: 28,
    backgroundColor: theme.colors.glassBorder,
  },
  riskRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  riskDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  // Rationale
  rationaleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  rationaleTitle: {
    ...theme.typography.caption,
  },
  rationaleText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  // Player tabs
  tabsContainer: {
    marginTop: 16,
    marginBottom: 12,
  },
  tabsScroll: {
    gap: 8,
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundCard,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    borderRadius: theme.borderRadius.pill,
    paddingHorizontal: 14,
    paddingVertical: 8,
    gap: 6,
  },
  tabActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  tabName: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    maxWidth: 120,
    textTransform: 'capitalize',
  },
  tabNameActive: {
    color: '#000',
  },
  tabConf: {
    fontSize: 12,
    fontWeight: '800',
    color: theme.colors.textTertiary,
  },
  tabConfActive: {
    color: 'rgba(0,0,0,0.5)',
  },
  // View detail link
  viewDetailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    marginTop: 14,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  viewDetailText: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  // Leg detail
  detailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 14,
  },
  detailName: {
    fontSize: 18,
    fontWeight: '800',
    color: theme.colors.textPrimary,
    textTransform: 'capitalize',
  },
  detailTeam: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  detailConfBox: {
    alignItems: 'center',
  },
  detailConfScore: {
    fontSize: 28,
    fontWeight: '800',
  },
  detailConfLabel: {
    fontSize: 9,
    fontWeight: '600',
    color: theme.colors.textTertiary,
    letterSpacing: 0.5,
  },
  detailPropRow: {
    flexDirection: 'row',
    gap: 12,
  },
  detailStatBox: {
    flex: 1,
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: theme.borderRadius.s,
    padding: 10,
    alignItems: 'center',
  },
  detailStatLabel: {
    fontSize: 9,
    fontWeight: '600',
    color: theme.colors.textTertiary,
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  detailStatValue: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  directionBadgeLg: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 6,
  },
  directionTextLg: {
    fontSize: 13,
    fontWeight: '800',
  },
  // Section
  sectionLabel: {
    ...theme.typography.caption,
    marginTop: 20,
    marginBottom: 10,
  },
  // Leg list rows
  legRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  legLeft: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: theme.colors.backgroundElevated,
    justifyContent: 'center',
    alignItems: 'center',
  },
  legNumber: {
    fontSize: 13,
    fontWeight: '800',
    color: theme.colors.textSecondary,
  },
  legMiddle: {
    flex: 1,
  },
  legPlayer: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    textTransform: 'capitalize',
  },
  legMeta: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 1,
  },
  legPropRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 4,
  },
  directionBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  directionText: {
    fontSize: 10,
    fontWeight: '800',
  },
  legStatLine: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  legRight: {
    alignItems: 'center',
    gap: 2,
  },
  legConfidence: {
    fontSize: 18,
    fontWeight: '800',
  },
});
