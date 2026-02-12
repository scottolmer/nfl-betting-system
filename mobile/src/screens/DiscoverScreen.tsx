/**
 * DiscoverScreen — "Market Pulse" Dashboard.
 * 
 * Replaces the old CardDemoScreen. Focuses on:
 * 1. Top Trends (Line Movers) — Horizontal scroll of significant line movements.
 * 2. Matchup Heatmap (Defense vs Position) — Visual grid showing favorable matchups.
 * 3. AI Insights Feed — Curated textual insights explaining the "why".
 */

import React, { useState } from 'react';
import {
    View,
    Text,
    ScrollView,
    StyleSheet,
    TouchableOpacity,
    Dimensions,
    FlatList,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import AnimatedCard from '../components/animated/AnimatedCard';

const { width } = Dimensions.get('window');
const CARD_WIDTH = width * 0.75;

// --- Mock Data ---

const TRENDS = [
    {
        id: '1',
        player: 'Breece Hall',
        team: 'NYJ',
        prop: 'Rush Yds',
        oldLine: 62.5,
        newLine: 68.5,
        type: 'up', // 'up' | 'down'
        insight: 'Sharp money flooding the over due to Rodgers injury news.',
    },
    {
        id: '2',
        player: 'Bijan Robinson',
        team: 'ATL',
        prop: 'Rec Yds',
        oldLine: 32.5,
        newLine: 28.5,
        type: 'down',
        insight: 'Heavy wind gusts (25mph) expected in Atlanta.',
    },
    {
        id: '3',
        player: 'CeeDee Lamb',
        team: 'DAL',
        prop: 'Receptions',
        oldLine: 6.5,
        newLine: 7.5,
        type: 'up',
        insight: 'Matchup upgrade: Eagles starting CB ruled out.',
    },
];

const MATCHUP_HEATMAP = [
    { position: 'QB', team: 'WAS', rank: 32, opponent: 'ARI' }, // WAS gives up most points to QB
    { position: 'WR1', team: 'PHI', rank: 31, opponent: 'DAL' },
    { position: 'RB', team: 'DEN', rank: 30, opponent: 'CLE' },
    { position: 'TE', team: 'CIN', rank: 29, opponent: 'PIT' },
];

const AI_INSIGHTS = [
    {
        id: '1',
        title: 'Touchdown Regression Alert',
        content: 'Jalen Hurts has 3 rushing TDs in the last 2 games despite only 4 redzone carries. Expect regression to the mean against a stout SF front seven.',
        type: 'fade', // 'target' | 'fade' | 'neutral'
    },
    {
        id: '2',
        title: 'Weather Impact: BUF vs KC',
        content: 'Snow accumulation is expected to hit 4 inches by kickoff. Historical data suggests a 15% drop in passing volume in these conditions. Look for James Cook overs.',
        type: 'target',
    },
    {
        id: '3',
        title: 'Volume Spike: Kyren Williams',
        content: 'With Cooper Kupp doubtful, Kyren Williams is projected for a 25% target share increase. His receiving line of 18.5 is likely too low.',
        type: 'target',
    },
];

// --- Components ---

const TrendCard = ({ item }: { item: typeof TRENDS[0] }) => (
    <View style={styles.trendCard}>
        <View style={styles.trendHeader}>
            <Text style={styles.trendPlayer}>{item.player}</Text>
            <Text style={styles.trendTeam}>{item.team}</Text>
        </View>
        <Text style={styles.trendProp}>{item.prop}</Text>

        <View style={styles.trendMovement}>
            <View>
                <Text style={styles.lineLabel}>Open</Text>
                <Text style={styles.oldLine}>{item.oldLine}</Text>
            </View>
            <Ionicons
                name="arrow-forward"
                size={16}
                color={theme.colors.textTertiary}
                style={{ marginHorizontal: 8 }}
            />
            <View>
                <Text style={styles.lineLabel}>Current</Text>
                <Text style={[
                    styles.newLine,
                    { color: item.type === 'up' ? theme.colors.success : theme.colors.danger }
                ]}>
                    {item.newLine}
                </Text>
            </View>
            <View style={styles.trendIconContainer}>
                <Ionicons
                    name={item.type === 'up' ? "trending-up" : "trending-down"}
                    size={20}
                    color={item.type === 'up' ? theme.colors.success : theme.colors.danger}
                />
            </View>
        </View>

        <Text style={styles.trendInsight} numberOfLines={2}>
            {item.insight}
        </Text>
    </View>
);

const MatchupRow = ({ item, index }: { item: typeof MATCHUP_HEATMAP[0], index: number }) => {
    // Color scale based on rank (32 is worst defense = best for offense = green)
    // Simple heuristic: >25 green, <10 red, else yellow/neutral
    let rankColor: string = theme.colors.textSecondary;
    if (item.rank >= 28) rankColor = theme.colors.success;
    else if (item.rank <= 5) rankColor = theme.colors.danger;
    else if (item.rank >= 20) rankColor = theme.colors.gold;

    return (
        <View style={[styles.matchupRow, index % 2 === 1 && styles.matchupRowAlt]}>
            <View style={styles.matchupColPositions}>
                <Text style={styles.matchupPos}>{item.position}</Text>
            </View>
            <View style={styles.matchupColTeam}>
                <Text style={styles.matchupTeam}>{item.opponent} vs {item.team}</Text>
                <Text style={styles.matchupContext}>Def Rank: {item.rank}</Text>
            </View>
            <View style={styles.matchupColGrade}>
                <View style={[styles.rankBadge, { backgroundColor: rankColor + '20', borderColor: rankColor }]}>
                    <Text style={[styles.rankText, { color: rankColor }]}>A+</Text>
                </View>
            </View>
        </View>
    );
};

const InsightCard = ({ item }: { item: typeof AI_INSIGHTS[0] }) => (
    <View style={styles.insightCard}>
        <View style={styles.insightHeader}>
            <Ionicons
                name={item.type === 'target' ? "rocket" : item.type === 'fade' ? "warning" : "information-circle"}
                size={18}
                color={item.type === 'target' ? theme.colors.success : item.type === 'fade' ? theme.colors.danger : theme.colors.primary}
            />
            <Text style={styles.insightTitle}>{item.title}</Text>
        </View>
        <Text style={styles.insightContent}>{item.content}</Text>
    </View>
);

export default function DiscoverScreen() {
    return (
        <View style={styles.container}>
            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>

                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.headerTitle}>Market Pulse</Text>
                    <Text style={styles.headerSubtitle}>Trends, movements, and AI insights</Text>
                </View>

                {/* Section 1: Line Movers (Carousel) */}
                <View style={styles.section}>
                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>Significant Line Moves</Text>
                        <TouchableOpacity><Text style={styles.seeAllText}>See All</Text></TouchableOpacity>
                    </View>
                    <FlatList
                        horizontal
                        data={TRENDS}
                        renderItem={({ item, index }) => (
                            <View style={{ marginRight: 12 }}>
                                <TrendCard item={item} />
                            </View>
                        )}
                        keyExtractor={item => item.id}
                        showsHorizontalScrollIndicator={false}
                        contentContainerStyle={styles.carouselContent}
                        decelerationRate="fast"
                        snapToInterval={CARD_WIDTH + 12}
                    />
                </View>

                {/* Section 2: Matchup Heatmap */}
                <View style={styles.section}>
                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>Exploitable Matchups</Text>
                        <TouchableOpacity><Text style={styles.seeAllText}>Full Grid</Text></TouchableOpacity>
                    </View>
                    <View style={styles.heatmapContainer}>
                        <View style={styles.heatmapHeaderRow}>
                            <Text style={[styles.heatmapHeaderLabel, { flex: 1 }]}>Pos</Text>
                            <Text style={[styles.heatmapHeaderLabel, { flex: 3 }]}>Matchup</Text>
                            <Text style={[styles.heatmapHeaderLabel, { flex: 1, textAlign: 'right' }]}>Grade</Text>
                        </View>
                        {MATCHUP_HEATMAP.map((item, index) => (
                            <MatchupRow key={index} item={item} index={index} />
                        ))}
                    </View>
                </View>

                {/* Section 3: AI Insights */}
                <View style={styles.section}>
                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>AI Strategy Feed</Text>
                    </View>
                    <View style={styles.insightsList}>
                        {AI_INSIGHTS.map((item, index) => (
                            <AnimatedCard key={item.id} index={index}>
                                <InsightCard item={item} />
                            </AnimatedCard>
                        ))}
                    </View>
                </View>

                <View style={{ height: 40 }} />
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: theme.colors.background,
    },
    scrollContent: {
        paddingBottom: 80,
    },
    header: {
        paddingTop: 60,
        paddingHorizontal: 20,
        paddingBottom: 20,
    },
    headerTitle: {
        ...theme.typography.h1,
        color: theme.colors.primary,
    },
    headerSubtitle: {
        fontSize: 14,
        color: theme.colors.textSecondary,
        marginTop: 4,
    },
    section: {
        marginBottom: 32,
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        marginBottom: 12,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '700',
        color: theme.colors.textPrimary,
    },
    seeAllText: {
        fontSize: 12,
        color: theme.colors.primary,
        fontWeight: '600',
    },

    // Carousel
    carouselContent: {
        paddingHorizontal: 20,
    },
    trendCard: {
        width: CARD_WIDTH,
        backgroundColor: theme.colors.backgroundCard,
        borderRadius: 16,
        padding: 16,
        borderWidth: 1,
        borderColor: theme.colors.glassBorder,
    },
    trendHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        marginBottom: 4,
    },
    trendPlayer: {
        fontSize: 16,
        fontWeight: '700',
        color: theme.colors.textPrimary,
    },
    trendTeam: {
        fontSize: 12,
        fontWeight: '700',
        color: theme.colors.textTertiary,
    },
    trendProp: {
        fontSize: 14,
        color: theme.colors.textSecondary,
        marginBottom: 12,
    },
    trendMovement: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(0,0,0,0.3)',
        borderRadius: 8,
        padding: 10,
        marginBottom: 12,
    },
    lineLabel: {
        fontSize: 10,
        color: theme.colors.textTertiary,
        textTransform: 'uppercase',
    },
    oldLine: {
        fontSize: 16,
        fontWeight: '600',
        color: theme.colors.textSecondary,
        textDecorationLine: 'line-through',
    },
    newLine: {
        fontSize: 18,
        fontWeight: '700',
    },
    trendIconContainer: {
        marginLeft: 'auto',
        backgroundColor: 'rgba(255,255,255,0.05)',
        padding: 4,
        borderRadius: 12,
    },
    trendInsight: {
        fontSize: 12,
        color: theme.colors.textSecondary,
        lineHeight: 18,
        fontStyle: 'italic',
    },

    // Heatmap
    heatmapContainer: {
        marginHorizontal: 20,
        backgroundColor: theme.colors.backgroundCard,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: theme.colors.glassBorder,
        overflow: 'hidden',
    },
    heatmapHeaderRow: {
        flexDirection: 'row',
        paddingVertical: 10,
        paddingHorizontal: 12,
        backgroundColor: 'rgba(255,255,255,0.03)',
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.glassBorder,
    },
    heatmapHeaderLabel: {
        fontSize: 11,
        fontWeight: '700',
        color: theme.colors.textTertiary,
        textTransform: 'uppercase',
    },
    matchupRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        paddingHorizontal: 12,
    },
    matchupRowAlt: {
        backgroundColor: 'rgba(255,255,255,0.015)',
    },
    matchupColPositions: {
        flex: 1,
    },
    matchupColTeam: {
        flex: 3,
    },
    matchupColGrade: {
        flex: 1,
        alignItems: 'flex-end',
    },
    matchupPos: {
        fontSize: 14,
        fontWeight: '700',
        color: theme.colors.textPrimary,
    },
    matchupTeam: {
        fontSize: 14,
        color: theme.colors.textSecondary,
        marginBottom: 2,
    },
    matchupContext: {
        fontSize: 10,
        color: theme.colors.textTertiary,
    },
    rankBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 6,
        borderWidth: 1,
    },
    rankText: {
        fontSize: 12,
        fontWeight: '800',
    },

    // Insights
    insightsList: {
        paddingHorizontal: 20,
        gap: 12,
    },
    insightCard: {
        backgroundColor: theme.colors.backgroundCard,
        borderRadius: 12,
        padding: 16,
        borderWidth: 1,
        borderColor: theme.colors.glassBorder,
    },
    insightHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
        gap: 8,
    },
    insightTitle: {
        fontSize: 14,
        fontWeight: '700',
        color: theme.colors.textPrimary,
    },
    insightContent: {
        fontSize: 13,
        color: theme.colors.textSecondary,
        lineHeight: 20,
    },
});
