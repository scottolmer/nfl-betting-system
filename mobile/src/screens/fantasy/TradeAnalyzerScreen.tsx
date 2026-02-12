/**
 * TradeAnalyzerScreen — Give/Get panels, ROS projection comparison, accept/decline verdict.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';

interface TradePlayer {
  player_id: number;
  player_name: string;
  team: string;
  position: string;
  fantasy_points: number;
  ros_value: number;
  confidence: number;
}

interface TradeResult {
  give: TradePlayer[];
  get: TradePlayer[];
  give_ros_total: number;
  get_ros_total: number;
  ros_diff: number;
  ros_diff_pct: number;
  verdict: 'ACCEPT' | 'CONSIDER' | 'DECLINE';
  verdict_reason: string;
  weeks_remaining: number;
}

export default function TradeAnalyzerScreen({ route, navigation }: any) {
  const { week, scoring } = route.params;
  const [giveSearch, setGiveSearch] = useState('');
  const [getSearch, setGetSearch] = useState('');
  const [giveIds, setGiveIds] = useState<number[]>([]);
  const [getIds, setGetIds] = useState<number[]>([]);
  const [giveNames, setGiveNames] = useState<string[]>([]);
  const [getNames, setGetNames] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchSide, setSearchSide] = useState<'give' | 'get'>('give');
  const [result, setResult] = useState<TradeResult | null>(null);
  const [loading, setLoading] = useState(false);

  const searchPlayers = async (query: string, side: 'give' | 'get') => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    setSearchSide(side);
    try {
      const resp = await apiService['client'].get('/api/players/search', {
        params: { q: query, limit: 5 },
      });
      setSearchResults(resp.data);
    } catch {
      setSearchResults([]);
    }
  };

  const addPlayer = (player: any) => {
    if (searchSide === 'give') {
      if (!giveIds.includes(player.id)) {
        setGiveIds([...giveIds, player.id]);
        setGiveNames([...giveNames, player.name]);
      }
      setGiveSearch('');
    } else {
      if (!getIds.includes(player.id)) {
        setGetIds([...getIds, player.id]);
        setGetNames([...getNames, player.name]);
      }
      setGetSearch('');
    }
    setSearchResults([]);
  };

  const removePlayer = (side: 'give' | 'get', index: number) => {
    if (side === 'give') {
      setGiveIds(giveIds.filter((_, i) => i !== index));
      setGiveNames(giveNames.filter((_, i) => i !== index));
    } else {
      setGetIds(getIds.filter((_, i) => i !== index));
      setGetNames(getNames.filter((_, i) => i !== index));
    }
    setResult(null);
  };

  const analyzeTrade = async () => {
    if (giveIds.length === 0 || getIds.length === 0) return;
    setLoading(true);
    try {
      const resp = await apiService['client'].post('/api/fantasy/trade-analyzer', {
        give_player_ids: giveIds,
        get_player_ids: getIds,
        week,
        weeks_remaining: 4,
        scoring,
      });
      setResult(resp.data);
    } catch (err) {
      console.error('Error analyzing trade:', err);
    } finally {
      setLoading(false);
    }
  };

  const verdictColor =
    result?.verdict === 'ACCEPT'
      ? theme.colors.success
      : result?.verdict === 'DECLINE'
      ? theme.colors.danger
      : theme.colors.warning;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Trade Analyzer</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Give panel */}
        <View style={styles.tradePanel}>
          <View style={styles.panelHeader}>
            <Ionicons name="arrow-up-circle" size={18} color={theme.colors.danger} />
            <Text style={styles.panelTitle}>You Give</Text>
          </View>
          {giveNames.map((name, i) => (
            <View key={i} style={styles.playerChip}>
              <Text style={styles.chipText}>{name}</Text>
              <TouchableOpacity onPress={() => removePlayer('give', i)}>
                <Ionicons name="close-circle" size={16} color={theme.colors.textTertiary} />
              </TouchableOpacity>
            </View>
          ))}
          <View style={styles.searchRow}>
            <TextInput
              style={styles.searchInput}
              placeholder="Add player..."
              placeholderTextColor={theme.colors.textTertiary}
              value={giveSearch}
              onChangeText={(text) => {
                setGiveSearch(text);
                searchPlayers(text, 'give');
              }}
            />
          </View>
          {searchSide === 'give' && searchResults.length > 0 && (
            <View style={styles.dropdown}>
              {searchResults.map((p) => (
                <TouchableOpacity key={p.id} style={styles.dropdownItem} onPress={() => addPlayer(p)}>
                  <Text style={styles.dropdownName}>{p.name}</Text>
                  <Text style={styles.dropdownMeta}>{p.team} · {p.position}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        {/* Swap icon */}
        <View style={styles.swapRow}>
          <Ionicons name="swap-vertical" size={24} color={theme.colors.primary} />
        </View>

        {/* Get panel */}
        <View style={styles.tradePanel}>
          <View style={styles.panelHeader}>
            <Ionicons name="arrow-down-circle" size={18} color={theme.colors.success} />
            <Text style={styles.panelTitle}>You Get</Text>
          </View>
          {getNames.map((name, i) => (
            <View key={i} style={styles.playerChip}>
              <Text style={styles.chipText}>{name}</Text>
              <TouchableOpacity onPress={() => removePlayer('get', i)}>
                <Ionicons name="close-circle" size={16} color={theme.colors.textTertiary} />
              </TouchableOpacity>
            </View>
          ))}
          <View style={styles.searchRow}>
            <TextInput
              style={styles.searchInput}
              placeholder="Add player..."
              placeholderTextColor={theme.colors.textTertiary}
              value={getSearch}
              onChangeText={(text) => {
                setGetSearch(text);
                searchPlayers(text, 'get');
              }}
            />
          </View>
          {searchSide === 'get' && searchResults.length > 0 && (
            <View style={styles.dropdown}>
              {searchResults.map((p) => (
                <TouchableOpacity key={p.id} style={styles.dropdownItem} onPress={() => addPlayer(p)}>
                  <Text style={styles.dropdownName}>{p.name}</Text>
                  <Text style={styles.dropdownMeta}>{p.team} · {p.position}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        {/* Analyze button */}
        <TouchableOpacity
          style={[styles.analyzeBtn, (giveIds.length === 0 || getIds.length === 0) && styles.analyzeBtnDisabled]}
          onPress={analyzeTrade}
          disabled={giveIds.length === 0 || getIds.length === 0 || loading}
          activeOpacity={0.8}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="analytics" size={18} color="#fff" />
              <Text style={styles.analyzeBtnText}>Analyze Trade</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Result */}
        {result && (
          <View style={styles.resultCard}>
            <View style={[styles.verdictBadge, { backgroundColor: verdictColor + '20' }]}>
              <Ionicons
                name={
                  result.verdict === 'ACCEPT' ? 'checkmark-circle' :
                  result.verdict === 'DECLINE' ? 'close-circle' : 'help-circle'
                }
                size={24}
                color={verdictColor}
              />
              <Text style={[styles.verdictText, { color: verdictColor }]}>{result.verdict}</Text>
            </View>

            <Text style={styles.verdictReason}>{result.verdict_reason}</Text>

            <View style={styles.comparisonRow}>
              <View style={styles.compCol}>
                <Text style={styles.compLabel}>You Give</Text>
                <Text style={styles.compValue}>{result.give_ros_total.toFixed(1)}</Text>
                <Text style={styles.compUnit}>ROS pts</Text>
              </View>
              <View style={styles.compCol}>
                <Text style={[styles.compDiff, { color: verdictColor }]}>
                  {result.ros_diff >= 0 ? '+' : ''}{result.ros_diff.toFixed(1)}
                </Text>
                <Text style={styles.compDiffPct}>
                  ({result.ros_diff_pct >= 0 ? '+' : ''}{result.ros_diff_pct.toFixed(1)}%)
                </Text>
              </View>
              <View style={styles.compCol}>
                <Text style={styles.compLabel}>You Get</Text>
                <Text style={styles.compValue}>{result.get_ros_total.toFixed(1)}</Text>
                <Text style={styles.compUnit}>ROS pts</Text>
              </View>
            </View>

            <Text style={styles.weeksNote}>
              Based on {result.weeks_remaining} weeks remaining · {result.scoring?.toUpperCase()} scoring
            </Text>
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
    paddingTop: 12,
    paddingHorizontal: 12,
    paddingBottom: 8,
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
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  tradePanel: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
  },
  panelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 10,
  },
  panelTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  playerChip: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: theme.colors.glassHigh,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginBottom: 6,
  },
  chipText: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  searchRow: {
    marginTop: 4,
  },
  searchInput: {
    backgroundColor: theme.colors.glassInput,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingHorizontal: 12,
    height: 36,
    color: theme.colors.textPrimary,
    fontSize: 13,
  },
  dropdown: {
    backgroundColor: theme.colors.glassHigh,
    borderRadius: theme.borderRadius.s,
    marginTop: 4,
    overflow: 'hidden',
  },
  dropdownItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  dropdownName: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  dropdownMeta: {
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  swapRow: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  analyzeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.m,
    paddingVertical: 14,
    marginTop: 16,
    gap: 8,
  },
  analyzeBtnDisabled: {
    opacity: 0.5,
  },
  analyzeBtnText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#fff',
  },
  resultCard: {
    backgroundColor: theme.colors.glassLow,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 18,
    marginTop: 16,
    alignItems: 'center',
  },
  verdictBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8,
    marginBottom: 10,
  },
  verdictText: {
    fontSize: 18,
    fontWeight: '800',
  },
  verdictReason: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 18,
    marginBottom: 16,
  },
  comparisonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 12,
  },
  compCol: {
    alignItems: 'center',
    flex: 1,
  },
  compLabel: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  compValue: {
    fontSize: 20,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  compUnit: {
    fontSize: 10,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  compDiff: {
    fontSize: 22,
    fontWeight: '800',
  },
  compDiffPct: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  weeksNote: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    textAlign: 'center',
  },
});
