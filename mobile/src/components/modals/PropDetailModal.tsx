/**
 * Prop Detail Modal
 * Full prop analysis shown when a prop card is tapped — dark theme
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { theme } from '../../constants/theme';
import { PropAnalysis } from '../../types';
import InfoTooltip from '../common/InfoTooltip';

interface PropDetailModalProps {
  visible: boolean;
  prop: PropAnalysis | null;
  onClose: () => void;
}

export default function PropDetailModal({
  visible,
  prop,
  onClose,
}: PropDetailModalProps) {
  if (!prop) return null;

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return theme.colors.success;
    if (confidence >= 75) return theme.colors.warning;
    if (confidence >= 70) return theme.colors.primary;
    return theme.colors.textSecondary;
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 80) return 'Elite';
    if (confidence >= 75) return 'Strong';
    if (confidence >= 70) return 'Solid';
    return 'Moderate';
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeIcon}>{'\u2715'}</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Prop Analysis</Text>
          <View style={styles.placeholder} />
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Player Info */}
          <View style={styles.playerSection}>
            <Text style={styles.playerName}>{prop.player_name}</Text>
            <Text style={styles.matchup}>
              {prop.team} {prop.position} vs {prop.opponent}
            </Text>
          </View>

          {/* Prop Line */}
          <View style={styles.propLineSection}>
            <View style={styles.propLineRow}>
              <Text style={styles.statType}>{prop.stat_type}</Text>
              <Text style={[styles.betType, { color: prop.bet_type === 'OVER' ? theme.colors.success : theme.colors.danger }]}>
                {prop.bet_type}
              </Text>
              <Text style={styles.line}>{prop.line}</Text>
            </View>
          </View>

          {/* Confidence */}
          <View style={styles.confidenceSection}>
            <View style={styles.confidenceHeader}>
              <Text style={styles.sectionTitle}>Confidence</Text>
              <InfoTooltip tooltipKey="confidence" />
            </View>
            <View style={styles.confidenceCard}>
              <Text
                style={[
                  styles.confidenceScore,
                  { color: getConfidenceColor(prop.confidence) },
                ]}
              >
                {Math.round(prop.confidence)}%
              </Text>
              <Text style={styles.confidenceLabel}>
                {getConfidenceLabel(prop.confidence)}
              </Text>
            </View>
          </View>

          {/* Projection & Cushion */}
          {prop.projection && (
            <View style={styles.section}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Projection & Cushion</Text>
                <InfoTooltip tooltipKey="projection" />
              </View>
              <View style={styles.statsGrid}>
                <View style={styles.statCard}>
                  <Text style={styles.statLabel}>Projection</Text>
                  <Text style={styles.statValue}>
                    {prop.projection.toFixed(1)}
                  </Text>
                </View>
                {prop.cushion !== undefined && (
                  <View style={styles.statCard}>
                    <Text style={styles.statLabel}>Cushion</Text>
                    <Text
                      style={[
                        styles.statValue,
                        { color: prop.cushion > 0 ? theme.colors.success : theme.colors.danger },
                      ]}
                    >
                      {prop.cushion > 0 ? '+' : ''}{prop.cushion.toFixed(1)}
                    </Text>
                  </View>
                )}
              </View>
            </View>
          )}

          {/* Top Reasons */}
          {prop.top_reasons && prop.top_reasons.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Why This Prop?</Text>
              <View style={styles.reasonsList}>
                {prop.top_reasons.map((reason, index) => (
                  <View key={index} style={styles.reasonItem}>
                    <View style={styles.reasonBulletCircle}>
                      <Text style={styles.reasonBulletText}>{index + 1}</Text>
                    </View>
                    <Text style={styles.reasonText}>{reason}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* Agent Analyses */}
          {prop.agent_analyses && prop.agent_analyses.length > 0 && (
            <View style={styles.section}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>AI Agent Analyses</Text>
                <InfoTooltip tooltipKey="agentAnalyses" />
              </View>
              <View style={styles.agentsList}>
                {prop.agent_analyses.map((agent, index) => (
                  <View key={index} style={styles.agentCard}>
                    <View style={styles.agentHeader}>
                      <Text style={styles.agentName}>{agent.name}</Text>
                      <Text
                        style={[
                          styles.agentConfidence,
                          { color: getConfidenceColor(agent.confidence) },
                        ]}
                      >
                        {Math.round(agent.confidence)}%
                      </Text>
                    </View>
                    <Text style={styles.agentReasoning}>{agent.reasoning}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}
        </ScrollView>

        {/* Footer Actions */}
        <View style={styles.footer}>
          <TouchableOpacity style={styles.actionButton} onPress={onClose}>
            <Text style={styles.actionButtonText}>Add to Parlay</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
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
    paddingTop: 60,
    paddingBottom: 16,
    paddingHorizontal: 20,
    backgroundColor: theme.colors.backgroundCard,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  closeButton: {
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeIcon: {
    fontSize: 24,
    color: theme.colors.textSecondary,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  placeholder: {
    width: 32,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  playerSection: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 20,
    marginBottom: 12,
    alignItems: 'center',
  },
  playerName: {
    fontSize: 24,
    fontWeight: '800',
    color: theme.colors.textPrimary,
    marginBottom: 6,
    textAlign: 'center',
  },
  matchup: {
    fontSize: 15,
    color: theme.colors.textSecondary,
  },
  propLineSection: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 20,
    marginBottom: 12,
  },
  propLineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  statType: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  betType: {
    fontSize: 17,
    fontWeight: '800',
  },
  line: {
    fontSize: 20,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  section: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginBottom: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  confidenceSection: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    marginBottom: 12,
  },
  confidenceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  confidenceCard: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  confidenceScore: {
    fontSize: 36,
    fontWeight: '800',
    marginBottom: 4,
  },
  confidenceLabel: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 13,
    color: theme.colors.textTertiary,
    marginBottom: 6,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  reasonsList: {
    gap: 12,
  },
  reasonItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  reasonBulletCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: theme.colors.primaryMuted,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
    marginTop: 2,
  },
  reasonBulletText: {
    fontSize: 11,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  reasonText: {
    flex: 1,
    fontSize: 15,
    color: theme.colors.textSecondary,
    lineHeight: 22,
  },
  agentsList: {
    gap: 12,
  },
  agentCard: {
    backgroundColor: theme.colors.backgroundElevated,
    borderRadius: 8,
    padding: 12,
  },
  agentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  agentName: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  agentConfidence: {
    fontSize: 15,
    fontWeight: '800',
  },
  agentReasoning: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  footer: {
    padding: 16,
    paddingBottom: 32,
    backgroundColor: theme.colors.backgroundCard,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  actionButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 16,
    borderRadius: theme.borderRadius.s,
    alignItems: 'center',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#000',
  },
});
