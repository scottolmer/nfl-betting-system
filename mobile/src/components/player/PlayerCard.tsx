/**
 * PlayerCard V2 — Data-rich card with embedded charts.
 * Three variants: compact (list item), standard (with chart), hero (detail screen)
 * High confidence (>=70): cyan glow border + shadow
 */

import React from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../../constants/theme';
import HitRateBarChart from '../charts/HitRateBarChart';
import MiniSparkline from '../charts/MiniSparkline';
import ConfidenceGauge from '../charts/ConfidenceGauge';

interface PropData {
  statType: string;
  betType: 'OVER' | 'UNDER';
  line: number;
  projection?: number;
  cushion?: number;
  last5?: number[];
  last10?: number[];
  last20?: number[];
  average?: number;
  trendValues?: number[];
}

interface PlayerCardProps {
  player: {
    name: string;
    team: string;
    position: string;
    headshot_url?: string | null;
  };
  subtitle?: string;
  rightContent?: React.ReactNode;
  onPress?: () => void;
  compact?: boolean;
  variant?: 'compact' | 'standard' | 'hero';
  confidence?: number;
  propData?: PropData;
}

function PlayerInitials({ name, size }: { name: string; size: number }) {
  const parts = name.split(' ');
  const initials = parts.length >= 2
    ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    : name.substring(0, 2).toUpperCase();

  return (
    <View style={[styles.initialsCircle, { width: size, height: size, borderRadius: size / 2 }]}>
      <Text style={[styles.initialsText, { fontSize: size * 0.35 }]}>{initials}</Text>
    </View>
  );
}

function PlayerCard({
  player,
  subtitle,
  rightContent,
  onPress,
  compact,
  variant: variantProp,
  confidence,
  propData,
}: PlayerCardProps) {
  const variant = variantProp || (compact ? 'compact' : 'standard');
  const Container = onPress ? TouchableOpacity : View;
  const isHighConf = confidence != null && confidence >= 70;
  const avatarSize = variant === 'compact' ? 36 : variant === 'hero' ? 56 : 44;

  return (
    <Container
      style={[
        styles.card,
        variant === 'compact' && styles.cardCompact,
        variant === 'hero' && styles.cardHero,
        isHighConf && styles.cardGlow,
      ]}
      {...(onPress ? { onPress, activeOpacity: 0.7 } : {})}
    >
      {/* Top row: Avatar + Info + Right content/gauge */}
      <View style={styles.topRow}>
        {player.headshot_url ? (
          <Image
            source={{ uri: player.headshot_url }}
            style={[styles.headshot, { width: avatarSize, height: avatarSize, borderRadius: avatarSize / 2 }]}
          />
        ) : (
          <PlayerInitials name={player.name} size={avatarSize} />
        )}
        <View style={styles.info}>
          <Text style={[styles.name, variant === 'compact' && styles.nameCompact]} numberOfLines={1}>
            {player.name}
          </Text>
          <Text style={styles.meta}>
            {player.team} {'\u00B7'} {player.position}
            {propData?.betType ? ` vs ` : ''}
          </Text>
          {subtitle ? <Text style={styles.subtitle} numberOfLines={1}>{subtitle}</Text> : null}
        </View>
        {/* Confidence gauge or custom right content */}
        {confidence != null && variant !== 'compact' && !rightContent ? (
          <ConfidenceGauge score={confidence} size={variant === 'hero' ? 'md' : 'sm'} />
        ) : rightContent ? (
          <View style={styles.right}>{rightContent}</View>
        ) : null}
      </View>

      {/* Prop line section (standard + hero) */}
      {propData && variant !== 'compact' && (
        <View style={styles.propSection}>
          <View style={styles.propLineRow}>
            <Text style={styles.statType}>{propData.statType}</Text>
            <View style={styles.propLineRight}>
              <Text style={[styles.betType, { color: propData.betType === 'OVER' ? theme.colors.success : theme.colors.danger }]}>
                {propData.betType}
              </Text>
              <Text style={styles.lineValue}>{propData.line}</Text>
            </View>
          </View>
          {propData.projection != null && (
            <View style={styles.projRow}>
              <Text style={styles.projLabel}>Proj:</Text>
              <Text style={styles.projValue}>{propData.projection.toFixed(1)}</Text>
              {propData.cushion != null && (
                <Text style={[styles.cushion, { color: propData.cushion > 0 ? theme.colors.success : theme.colors.danger }]}>
                  ({propData.cushion > 0 ? '+' : ''}{propData.cushion.toFixed(1)})
                </Text>
              )}
            </View>
          )}
        </View>
      )}

      {/* Chart section (standard + hero, when data available) */}
      {propData?.last5 && propData.last5.length > 0 && variant !== 'compact' && (
        <View style={styles.chartSection}>
          <HitRateBarChart
            values={propData.last5}
            line={propData.line}
            label="L5"
            height={variant === 'hero' ? 56 : 44}
          />
          {/* Sparkline trend */}
          {propData.trendValues && propData.trendValues.length >= 3 && (
            <View style={styles.sparklineRow}>
              <MiniSparkline
                values={propData.trendValues}
                threshold={propData.line}
                width={80}
                height={28}
              />
              {propData.average != null && (
                <Text style={styles.avgLabel}>Avg: {propData.average.toFixed(1)}</Text>
              )}
            </View>
          )}
        </View>
      )}

      {/* Hero: full L5/L10/L20 */}
      {variant === 'hero' && propData?.last10 && propData.last10.length > 0 && (
        <View style={styles.multiPeriod}>
          <HitRateBarChart values={propData.last10} line={propData.line} label="L10" height={44} />
        </View>
      )}
    </Container>
  );
}

export default React.memo(PlayerCard);

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 14,
    marginBottom: 8,
    ...theme.shadows.card,
  },
  cardCompact: {
    padding: 10,
    marginBottom: 6,
  },
  cardHero: {
    padding: 18,
    marginBottom: 14,
  },
  cardGlow: {
    borderColor: theme.colors.glassBorderActive,
    ...theme.shadows.glow,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headshot: {
    backgroundColor: theme.colors.backgroundElevated,
    marginRight: 12,
  },
  initialsCircle: {
    backgroundColor: theme.colors.backgroundElevated,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
  },
  initialsText: {
    color: theme.colors.primary,
    fontWeight: '700',
  },
  info: {
    flex: 1,
  },
  name: {
    ...theme.typography.label,
    marginBottom: 2,
  },
  nameCompact: {
    fontSize: 13,
  },
  meta: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  subtitle: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  right: {
    marginLeft: 8,
    alignItems: 'flex-end',
  },
  // Prop line section
  propSection: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
  },
  propLineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statType: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  propLineRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  betType: {
    fontSize: 12,
    fontWeight: '800',
  },
  lineValue: {
    fontSize: 18,
    fontWeight: '800',
    color: theme.colors.textPrimary,
  },
  projRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
  },
  projLabel: {
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  projValue: {
    fontSize: 12,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  cushion: {
    fontSize: 11,
    fontWeight: '700',
  },
  // Chart section
  chartSection: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    alignItems: 'center',
  },
  sparklineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 8,
  },
  avgLabel: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  multiPeriod: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: theme.colors.glassBorder,
    alignItems: 'center',
  },
});
