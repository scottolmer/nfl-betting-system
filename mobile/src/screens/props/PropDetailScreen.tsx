/**
 * PropDetailScreen V2 — Cohesive single-scroll with all chart components.
 * Hero PlayerCard, Historical Stats, large ConfidenceGauge, Agent Breakdown V2,
 * Line Movement Chart V2, Multi-Book Odds V2.
 */

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { PropAnalysis, BookOddsEntry, LineMovementEntry } from '../../types';
import { apiService } from '../../services/api';
import PlayerCard from '../../components/player/PlayerCard';
import AgentBreakdownCard from '../../components/player/AgentBreakdownCard';
import MultiBookOddsTable from '../../components/odds/MultiBookOddsTable';
import LineMovementChartV2 from '../../components/charts/LineMovementChartV2';
import BetSizeSuggestion from '../../components/betting/BetSizeSuggestion';
import ConfidenceGauge from '../../components/charts/ConfidenceGauge';
import HitRateBarChart from '../../components/charts/HitRateBarChart';
import MiniSparkline from '../../components/charts/MiniSparkline';
import GlassCard from '../../components/common/GlassCard';
import AnimatedCard from '../../components/animated/AnimatedCard';
import { useParlay } from '../../contexts/ParlayContext';

interface PropDetailParams {
  prop: PropAnalysis;
  week: number;
}

interface HistoryData {
  values: number[];
  average: number | null;
  total_games: number;
  line?: number;
  over_count?: number;
  under_count?: number;
  hit_rate_pct?: number;
}

export default function PropDetailScreen({ route, navigation }: any) {
  const { prop, week } = route.params as PropDetailParams;
  const { togglePick, isPicked } = useParlay();
  const selected = isPicked(prop);
  const [odds, setOdds] = useState<BookOddsEntry[]>([]);
  const [movements, setMovements] = useState<LineMovementEntry[]>([]);
  const [loadingOdds, setLoadingOdds] = useState(true);
  const [history, setHistory] = useState<HistoryData | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    loadOddsData();
    loadHistory();
  }, []);

  const loadOddsData = async () => {
    try {
      setLoadingOdds(true);
      const rawOdds = await apiService.getOdds({
        week,
        player_name: prop.player_name,
        stat_type: prop.stat_type,
      });

      // Group by bookmaker
      const bookMap = new Map<string, BookOddsEntry>();

      rawOdds.forEach((o) => {
        const bookKey = o.book.toLowerCase();
        if (!bookMap.has(bookKey)) {
          bookMap.set(bookKey, {
            id: Math.random(), // Dummy ID
            player_id: 0,
            week,
            stat_type: prop.stat_type,
            bookmaker: o.book,
            line: o.line,
            over_price: null,
            under_price: null,
            fetched_at: o.timestamp,
          });
        }

        const entry = bookMap.get(bookKey)!;
        if (o.side === 'over') {
          entry.over_price = o.price;
        } else if (o.side === 'under') {
          entry.under_price = o.price;
        }
        // Update line if needed (take latest?)
        entry.line = o.line;
      });

      setOdds(Array.from(bookMap.values()));
      setMovements([]); // Line movements not yet implemented in this simplified view
    } catch (err) {
      console.error('Error loading odds:', err);
    } finally {
      setLoadingOdds(false);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await apiService.getPlayerHistory({
        player_name: prop.player_name,
        stat_type: prop.stat_type,
        week,
        line: prop.line,
      });
      if (data.values.length > 0) {
        setHistory(data);
      }
    } catch (err) {
      console.error('Error loading history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const edgePct = Math.max(0, (prop.confidence - 52.4) * 0.8);
  const suggestedUnits = edgePct > 5 ? 2.0 : edgePct > 2 ? 1.0 : 0.5;
  const riskLevel: 'low' | 'medium' | 'high' = suggestedUnits <= 1 ? 'low' : suggestedUnits <= 2 ? 'medium' : 'high';

  const agentBreakdown = prop.agent_breakdown || {};

  const isHighConf = prop.confidence >= 70;

  // Split history values into last5 / last10
  const last5 = history ? history.values.slice(-5) : [];
  const last10 = history ? history.values.slice(-10) : [];

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Prop Detail</Text>
        <TouchableOpacity
          onPress={() => togglePick(prop)}
          style={[styles.parlayBtn, selected && styles.parlayBtnActive]}
          activeOpacity={0.7}
        >
          <Ionicons
            name={selected ? 'checkmark' : 'add'}
            size={18}
            color={selected ? '#000' : theme.colors.primary}
          />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Hero Player Card with full prop data */}
        <AnimatedCard index={0}>
          <PlayerCard
            player={{
              name: prop.player_name,
              team: prop.team,
              position: prop.position,
              headshot_url: prop.headshot_url,
            }}
            subtitle={`vs ${prop.opponent}`}
            variant="hero"
            confidence={prop.confidence}
            propData={{
              statType: prop.stat_type,
              betType: prop.bet_type,
              line: prop.line,
              projection: prop.projection,
              cushion: prop.cushion,
              last5: last5.length > 0 ? last5 : undefined,
              last10: last10.length > 5 ? last10 : undefined,
              trendValues: history && history.values.length >= 3 ? history.values : undefined,
              average: history?.average ?? undefined,
            }}
          />
        </AnimatedCard>

        {/* Historical Stats Section */}
        {loadingHistory ? (
          <ActivityIndicator color={theme.colors.primary} style={{ marginVertical: 12 }} />
        ) : history && history.values.length > 0 ? (
          <AnimatedCard index={1}>
            <GlassCard>
              <Text style={styles.sectionTitle}>GAME LOG</Text>

              {/* Hit rate summary */}
              {history.hit_rate_pct != null && (
                <View style={styles.hitRateSummary}>
                  <View style={styles.hitRateItem}>
                    <Text style={styles.hitRateValue}>{history.total_games}</Text>
                    <Text style={styles.hitRateLabel}>Games</Text>
                  </View>
                  <View style={styles.hitRateItem}>
                    <Text style={[styles.hitRateValue, { color: theme.colors.success }]}>
                      {history.over_count}
                    </Text>
                    <Text style={styles.hitRateLabel}>Over</Text>
                  </View>
                  <View style={styles.hitRateItem}>
                    <Text style={[styles.hitRateValue, { color: theme.colors.danger }]}>
                      {history.under_count}
                    </Text>
                    <Text style={styles.hitRateLabel}>Under</Text>
                  </View>
                  <View style={styles.hitRateItem}>
                    <Text style={[styles.hitRateValue, {
                      color: (history.hit_rate_pct ?? 0) >= 60 ? theme.colors.success
                        : (history.hit_rate_pct ?? 0) >= 40 ? theme.colors.warning
                          : theme.colors.danger
                    }]}>
                      {history.hit_rate_pct}%
                    </Text>
                    <Text style={styles.hitRateLabel}>Hit Rate</Text>
                  </View>
                  {history.average != null && (
                    <View style={styles.hitRateItem}>
                      <Text style={styles.hitRateValue}>{history.average}</Text>
                      <Text style={styles.hitRateLabel}>Avg</Text>
                    </View>
                  )}
                </View>
              )}

              {/* Bar chart - last 5 games */}
              {last5.length > 0 && (
                <View style={styles.chartSection}>
                  <HitRateBarChart
                    values={last5}
                    line={prop.line}
                    label={`Last ${last5.length}`}
                    height={56}
                  />
                </View>
              )}

              {/* Bar chart - last 10 games */}
              {last10.length > 5 && (
                <View style={styles.chartSection}>
                  <HitRateBarChart
                    values={last10}
                    line={prop.line}
                    label={`Last ${last10.length}`}
                    height={44}
                  />
                </View>
              )}

              {/* Trend sparkline */}
              {history.values.length >= 3 && (
                <View style={styles.sparklineSection}>
                  <Text style={styles.sparklineLabel}>Trend</Text>
                  <MiniSparkline
                    values={history.values}
                    threshold={prop.line}
                    width={200}
                    height={36}
                  />
                </View>
              )}

              {/* Individual game values */}
              <View style={styles.gameValues}>
                {history.values.map((val, i) => {
                  const isOver = val > prop.line;
                  return (
                    <View
                      key={i}
                      style={[styles.gameValueChip, {
                        backgroundColor: isOver ? theme.colors.successMuted : theme.colors.dangerMuted,
                        borderColor: isOver ? theme.colors.success : theme.colors.danger,
                      }]}
                    >
                      <Text style={[styles.gameValueText, {
                        color: isOver ? theme.colors.success : theme.colors.danger,
                      }]}>
                        {val}
                      </Text>
                    </View>
                  );
                })}
              </View>
            </GlassCard>
          </AnimatedCard>
        ) : null}

        {/* Prop line card with glow */}
        <AnimatedCard index={2}>
          <GlassCard glow={isHighConf}>
            <View style={styles.propLineRow}>
              <View>
                <Text style={styles.statType}>{prop.stat_type}</Text>
                {prop.projection != null && (
                  <View style={styles.projRow}>
                    <Text style={styles.projLabel}>Proj:</Text>
                    <Text style={styles.projValue}>{prop.projection.toFixed(1)}</Text>
                    {prop.cushion != null && (
                      <Text style={[styles.cushionText, { color: prop.cushion > 0 ? theme.colors.success : theme.colors.danger }]}>
                        ({prop.cushion > 0 ? '+' : ''}{prop.cushion.toFixed(1)})
                      </Text>
                    )}
                  </View>
                )}
              </View>
              <View style={styles.lineBox}>
                <View style={[styles.betTypeBadge, {
                  backgroundColor: prop.bet_type === 'OVER' ? theme.colors.successMuted : theme.colors.dangerMuted,
                }]}>
                  <Text style={[styles.betTypeText, {
                    color: prop.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger,
                  }]}>
                    {prop.bet_type}
                  </Text>
                </View>
                <Text style={styles.lineValue}>{prop.line}</Text>
              </View>
            </View>

            {/* Show source book + other available lines */}
            {prop.bookmaker && (
              <View style={styles.bookSourceRow}>
                <Ionicons name="book-outline" size={12} color={theme.colors.textTertiary} />
                <Text style={styles.bookSourceText}>
                  Line from {prop.bookmaker}
                </Text>
              </View>
            )}
            {prop.all_books && prop.all_books.length > 1 && (
              <View style={styles.allBooksRow}>
                {prop.all_books.map((book, i) => (
                  <View key={i} style={[
                    styles.bookChip,
                    book.line === prop.line && styles.bookChipActive,
                  ]}>
                    <Text style={[
                      styles.bookChipText,
                      book.line === prop.line && styles.bookChipTextActive,
                    ]}>
                      {book.bookmaker}: {book.line}
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </GlassCard>
        </AnimatedCard>

        {/* Large centered Confidence Gauge */}
        <AnimatedCard index={3}>
          <GlassCard>
            <View style={styles.gaugeCenter}>
              <ConfidenceGauge score={prop.confidence} size="lg" />
            </View>
          </GlassCard>
        </AnimatedCard>

        {/* Bet sizing */}
        <AnimatedCard index={4}>
          <BetSizeSuggestion
            confidence={prop.confidence}
            edgePct={edgePct}
            suggestedUnits={suggestedUnits}
            riskLevel={riskLevel}
          />
        </AnimatedCard>

        {/* Agent Breakdown */}
        <AnimatedCard index={5}>
          <AgentBreakdownCard
            breakdown={agentBreakdown}
            edgeExplanation={prop.edge_explanation}
            topReasons={prop.top_reasons}
          />
        </AnimatedCard>

        {/* Multi-book odds + line movement */}
        {loadingOdds ? (
          <ActivityIndicator color={theme.colors.primary} style={{ marginVertical: 20 }} />
        ) : (
          <>
            <AnimatedCard index={6}>
              <MultiBookOddsTable odds={odds} direction={prop.bet_type as 'OVER' | 'UNDER'} />
            </AnimatedCard>
            <AnimatedCard index={7}>
              <LineMovementChartV2 movements={movements} currentLine={prop.line} />
            </AnimatedCard>
          </>
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
  parlayBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1.5,
    borderColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  parlayBtnActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
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
  // Section title
  sectionTitle: {
    ...theme.typography.caption,
    marginBottom: 12,
  },
  // Hit rate summary row
  hitRateSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 14,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  hitRateItem: {
    alignItems: 'center',
  },
  hitRateValue: {
    fontSize: 18,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  hitRateLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginTop: 2,
  },
  // Chart sections
  chartSection: {
    marginBottom: 10,
    alignItems: 'center',
  },
  sparklineSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginTop: 6,
    marginBottom: 10,
  },
  sparklineLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    textTransform: 'uppercase',
  },
  // Game values chips
  gameValues: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 8,
    justifyContent: 'center',
  },
  gameValueChip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
  },
  gameValueText: {
    fontSize: 12,
    fontWeight: '700',
  },
  // Prop line
  propLineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statType: {
    ...theme.typography.h3,
  },
  lineBox: {
    alignItems: 'flex-end',
    gap: 4,
  },
  betTypeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
  },
  betTypeText: {
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  lineValue: {
    ...theme.typography.scoreLG,
  },
  bookSourceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 10,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  bookSourceText: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    textTransform: 'capitalize',
  },
  allBooksRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 8,
  },
  bookChip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
  },
  bookChipActive: {
    borderColor: theme.colors.primary,
    backgroundColor: theme.colors.primaryMuted,
  },
  bookChipText: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    textTransform: 'capitalize',
  },
  bookChipTextActive: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  projRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
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
  cushionText: {
    fontSize: 12,
    fontWeight: '700',
  },
  // Gauge
  gaugeCenter: {
    alignItems: 'center',
    paddingVertical: 8,
  },
});
