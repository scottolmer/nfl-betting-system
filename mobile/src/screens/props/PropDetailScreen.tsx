/**
 * PropDetailScreen — Player card + multi-book odds + line chart + agent breakdown + bet sizing.
 */

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { PropAnalysis, BookOddsEntry, LineMovementEntry } from '../../types';
import { playerService } from '../../services/playerService';
import PlayerCard from '../../components/player/PlayerCard';
import AgentBreakdownCard from '../../components/player/AgentBreakdownCard';
import MultiBookOddsTable from '../../components/odds/MultiBookOddsTable';
import LineMovementChart from '../../components/odds/LineMovementChart';
import BetSizeSuggestion from '../../components/betting/BetSizeSuggestion';

interface PropDetailParams {
  prop: PropAnalysis;
  week: number;
}

export default function PropDetailScreen({ route, navigation }: any) {
  const { prop, week } = route.params as PropDetailParams;
  const [odds, setOdds] = useState<BookOddsEntry[]>([]);
  const [movements, setMovements] = useState<LineMovementEntry[]>([]);
  const [loadingOdds, setLoadingOdds] = useState(true);

  useEffect(() => {
    loadOddsData();
  }, []);

  const loadOddsData = async () => {
    try {
      // These will work once players are synced and have IDs
      // For now, we load gracefully even if data is empty
      setOdds([]);
      setMovements([]);
    } catch (err) {
      console.error('Error loading odds:', err);
    } finally {
      setLoadingOdds(false);
    }
  };

  const getConfidenceColor = (c: number) => {
    if (c >= 70) return theme.colors.success;
    if (c >= 60) return theme.colors.primary;
    return theme.colors.textSecondary;
  };

  // Mock edge calculation for display (real version comes from backend)
  const edgePct = Math.max(0, (prop.confidence - 52.4) * 0.8);
  const suggestedUnits = edgePct > 5 ? 2.0 : edgePct > 2 ? 1.0 : 0.5;
  const riskLevel: 'low' | 'medium' | 'high' = suggestedUnits <= 1 ? 'low' : suggestedUnits <= 2 ? 'medium' : 'high';

  // Transform agent_analyses array to Record format if needed
  const agentBreakdown: Record<string, { score: number; weight: number; direction: string }> =
    prop.agent_analyses
      ? Object.fromEntries(
          prop.agent_analyses.map((a) => [a.name, { score: a.confidence, weight: a.weight, direction: 'OVER' }]),
        )
      : {};

  return (
    <View style={styles.container}>
      {/* Header with back button */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Prop Detail</Text>
        <View style={styles.backBtn} />
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Player card */}
        <PlayerCard
          player={{
            name: prop.player_name,
            team: prop.team,
            position: prop.position,
          }}
          subtitle={`vs ${prop.opponent}`}
          rightContent={
            <View style={styles.confidenceBadge}>
              <Text style={[styles.confidenceNum, { color: getConfidenceColor(prop.confidence) }]}>
                {Math.round(prop.confidence)}
              </Text>
            </View>
          }
        />

        {/* Prop line card */}
        <View style={styles.propLineCard}>
          <View style={styles.propLineRow}>
            <Text style={styles.statType}>{prop.stat_type}</Text>
            <View style={styles.lineBox}>
              <Text style={[styles.betType, { color: prop.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger }]}>
                {prop.bet_type}
              </Text>
              <Text style={styles.lineValue}>{prop.line}</Text>
            </View>
          </View>
          {prop.projection != null && (
            <View style={styles.projectionRow}>
              <Text style={styles.projLabel}>Projection</Text>
              <Text style={styles.projValue}>{prop.projection.toFixed(1)}</Text>
              {prop.cushion != null && (
                <Text style={[styles.cushion, { color: prop.cushion > 0 ? theme.colors.success : theme.colors.danger }]}>
                  {prop.cushion > 0 ? '+' : ''}{prop.cushion.toFixed(1)}
                </Text>
              )}
            </View>
          )}
        </View>

        {/* Bet sizing */}
        <BetSizeSuggestion
          confidence={prop.confidence}
          edgePct={edgePct}
          suggestedUnits={suggestedUnits}
          riskLevel={riskLevel}
        />

        {/* Agent Breakdown */}
        <AgentBreakdownCard breakdown={agentBreakdown} />

        {/* Multi-book odds */}
        {loadingOdds ? (
          <ActivityIndicator color={theme.colors.primary} style={{ marginVertical: 20 }} />
        ) : (
          <>
            <MultiBookOddsTable odds={odds} direction={prop.bet_type as 'OVER' | 'UNDER'} />
            <LineMovementChart movements={movements} currentLine={prop.line} />
          </>
        )}

        {/* Top reasons */}
        {prop.top_reasons && prop.top_reasons.length > 0 && (
          <View style={styles.reasonsCard}>
            <Text style={styles.reasonsTitle}>Top Reasons</Text>
            {prop.top_reasons.map((reason, i) => (
              <View key={i} style={styles.reasonRow}>
                <Text style={styles.reasonBullet}>{i + 1}</Text>
                <Text style={styles.reasonText}>{reason}</Text>
              </View>
            ))}
          </View>
        )}
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
  confidenceBadge: {
    alignItems: 'center',
  },
  confidenceNum: {
    fontSize: 28,
    fontWeight: '800',
  },
  propLineCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
  },
  propLineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statType: {
    ...theme.typography.h3,
  },
  lineBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  betType: {
    fontSize: 14,
    fontWeight: '800',
  },
  lineValue: {
    fontSize: 22,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  projectionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    gap: 8,
  },
  projLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  projValue: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  cushion: {
    fontSize: 12,
    fontWeight: '700',
  },
  reasonsCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 12,
  },
  reasonsTitle: {
    ...theme.typography.caption,
    marginBottom: 10,
  },
  reasonRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
    gap: 8,
  },
  reasonBullet: {
    fontSize: 11,
    fontWeight: '800',
    color: theme.colors.primary,
    width: 16,
    textAlign: 'center',
  },
  reasonText: {
    flex: 1,
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
  },
});
