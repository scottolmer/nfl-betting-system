
import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, LayoutAnimation } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import GlassCard from '../common/GlassCard';
import { ParlayGradeResponse } from '../../types';

interface ParlayGradeCardProps {
    gradeResult: ParlayGradeResponse;
    onApplySwap?: (swapIndex: number) => void;
}

export default function ParlayGradeCard({ gradeResult, onApplySwap }: ParlayGradeCardProps) {
    const [expanded, setExpanded] = useState(false);

    const {
        grade,
        adjusted_confidence,
        recommendation,
        analysis,
        risk_factors,
        value_edge,
        implied_probability,
        true_probability,
        suggestions,
    } = gradeResult;

    const isGood = ['A+', 'A', 'B'].includes(grade);
    const isBad = ['D', 'F'].includes(grade);

    const gradeColor = isGood
        ? theme.colors.success
        : isBad
            ? theme.colors.danger
            : theme.colors.gold;

    const toggleExpand = () => {
        LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
        setExpanded(!expanded);
    };

    return (
        <View style={styles.container}>
            {/* Main Grade Header */}
            <GlassCard glow={isGood} style={styles.card}>
                <View style={styles.header}>
                    <View>
                        <Text style={styles.title}>AI GRADE</Text>
                        <View style={styles.gradeRow}>
                            <Text style={[styles.gradeText, { color: gradeColor }]}>{grade}</Text>
                            <View style={styles.statBox}>
                                <Text style={styles.statValue}>{adjusted_confidence.toFixed(1)}%</Text>
                                <Text style={styles.statLabel}>Win Prob</Text>
                            </View>
                        </View>
                    </View>

                    <View style={styles.recommendationBox}>
                        <Text style={[styles.recText, { color: gradeColor }]}>{recommendation}</Text>
                    </View>
                </View>

                {/* Value Analysis */}
                <View style={styles.valueRow}>
                    <View style={styles.valueItem}>
                        <Text style={styles.valueLabel}>Implied</Text>
                        <Text style={styles.valueNum}>{implied_probability.toFixed(1)}%</Text>
                    </View>
                    <Ionicons name="arrow-forward" size={14} color={theme.colors.textTertiary} />
                    <View style={styles.valueItem}>
                        <Text style={styles.valueLabel}>True</Text>
                        <Text style={[styles.valueNum, { color: theme.colors.textPrimary }]}>
                            {true_probability.toFixed(1)}%
                        </Text>
                    </View>
                    <View style={[styles.edgeBadge, { backgroundColor: value_edge > 0 ? 'rgba(76, 175, 80, 0.2)' : 'rgba(244, 67, 54, 0.2)' }]}>
                        <Text style={[styles.edgeText, { color: value_edge > 0 ? theme.colors.success : theme.colors.danger }]}>
                            {value_edge > 0 ? '+' : ''}{value_edge.toFixed(1)}% Edge
                        </Text>
                    </View>
                </View>

                {/* Risk Factors (Always Visible if High Risk) */}
                {risk_factors.length > 0 && (
                    <View style={styles.risks}>
                        {risk_factors.map((risk, index) => (
                            <View key={index} style={styles.riskRow}>
                                <Ionicons name="warning" size={14} color={theme.colors.gold} />
                                <Text style={styles.riskText}>{risk}</Text>
                            </View>
                        ))}
                    </View>
                )}

                {/* Expandable Analysis */}
                <TouchableOpacity onPress={toggleExpand} style={styles.expandBtn}>
                    <Text style={styles.expandText}>{expanded ? 'Hide Analysis' : 'View Detailed Analysis'}</Text>
                    <Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={16} color={theme.colors.textSecondary} />
                </TouchableOpacity>

                {expanded && (
                    <View style={styles.details}>
                        <Text style={styles.analysisText}>{analysis}</Text>

                        {/* Smart Swaps */}
                        {suggestions.length > 0 && (
                            <View style={styles.swaps}>
                                <Text style={styles.swapsTitle}>AI SUGGESTIONS</Text>
                                {suggestions.map((suggestion, index) => (
                                    <TouchableOpacity
                                        key={index}
                                        style={styles.swapCard}
                                        onPress={() => onApplySwap && onApplySwap(index)}
                                    >
                                        <View style={styles.swapHeader}>
                                            <Ionicons name="swap-vertical" size={16} color={theme.colors.primary} />
                                            <Text style={styles.swapTitle}>Better Alternative Found</Text>
                                        </View>
                                        <Text style={styles.swapReason}>{suggestion.reason}</Text>
                                        <View style={styles.swapProp}>
                                            <Text style={styles.swapPropText}>
                                                Swap Leg {suggestion.original_leg_index + 1} with: {'\n'}
                                                <Text style={{ fontWeight: 'bold', color: theme.colors.textPrimary }}>
                                                    {suggestion.new_leg.player_name} {suggestion.new_leg.stat_type} {suggestion.new_leg.bet_type} {suggestion.new_leg.line}
                                                </Text>
                                            </Text>
                                        </View>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        )}
                    </View>
                )}
            </GlassCard>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        marginBottom: 16,
    },
    card: {
        padding: 16,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 12,
    },
    title: {
        ...theme.typography.caption,
        color: theme.colors.textSecondary,
        marginBottom: 4,
    },
    gradeRow: {
        flexDirection: 'row',
        alignItems: 'baseline',
        gap: 12,
    },
    gradeText: {
        fontSize: 42,
        fontWeight: '800',
        lineHeight: 48,
    },
    statBox: {
        justifyContent: 'center',
    },
    statValue: {
        fontSize: 18,
        fontWeight: '700',
        color: theme.colors.textPrimary,
    },
    statLabel: {
        fontSize: 10,
        color: theme.colors.textTertiary,
    },
    recommendationBox: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 12,
        backgroundColor: 'rgba(255,255,255,0.05)',
    },
    recText: {
        fontSize: 12,
        fontWeight: '700',
    },
    valueRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        marginBottom: 16,
        padding: 8,
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: 8,
    },
    valueItem: {
        alignItems: 'center',
    },
    valueLabel: {
        fontSize: 10,
        color: theme.colors.textTertiary,
    },
    valueNum: {
        fontSize: 12,
        fontWeight: '600',
        color: theme.colors.textSecondary,
    },
    edgeBadge: {
        marginLeft: 'auto',
        paddingHorizontal: 8,
        paddingVertical: 2,
        borderRadius: 4,
    },
    edgeText: {
        fontSize: 11,
        fontWeight: '700',
    },
    risks: {
        gap: 4,
        marginBottom: 12,
    },
    riskRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
    },
    riskText: {
        fontSize: 12,
        color: theme.colors.textSecondary,
        flex: 1,
    },
    expandBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        paddingVertical: 8,
        borderTopWidth: 1,
        borderTopColor: 'rgba(255,255,255,0.1)',
    },
    expandText: {
        fontSize: 12,
        color: theme.colors.textSecondary,
        fontWeight: '600',
    },
    details: {
        marginTop: 8,
    },
    analysisText: {
        fontSize: 13,
        color: theme.colors.textSecondary,
        lineHeight: 20,
        marginBottom: 16,
    },
    swaps: {
        gap: 8,
    },
    swapsTitle: {
        ...theme.typography.caption,
        marginBottom: 4,
    },
    swapCard: {
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        borderRadius: 8,
        padding: 10,
        borderWidth: 1,
        borderColor: 'rgba(33, 150, 243, 0.3)',
    },
    swapHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
        marginBottom: 4,
    },
    swapTitle: {
        fontSize: 12,
        fontWeight: '700',
        color: theme.colors.primary,
    },
    swapReason: {
        fontSize: 11,
        color: theme.colors.textSecondary,
        marginBottom: 4,
    },
    swapProp: {
        backgroundColor: 'rgba(0,0,0,0.2)',
        padding: 6,
        borderRadius: 4,
    },
    swapPropText: {
        fontSize: 11,
        color: theme.colors.textTertiary,
    },
});
