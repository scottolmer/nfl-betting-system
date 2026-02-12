/**
 * CardDemoScreen — Visual showcase of PlayerCard V2 with real Week 13 data.
 * Shows all three variants: compact, standard, and hero.
 */

import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { theme } from '../constants/theme';
import PlayerCard from '../components/player/PlayerCard';
import ConfidenceGauge from '../components/charts/ConfidenceGauge';
import AnimatedCard from '../components/animated/AnimatedCard';

// Real Week 13 data
const DEMO_PROPS = [
  {
    player: { name: 'Saquon Barkley', team: 'PHI', position: 'RB' },
    confidence: 82,
    propData: {
      statType: 'Rush Attempts',
      betType: 'UNDER' as const,
      line: 17.5,
      projection: 15.2,
      cushion: -2.3,
      last5: [21, 14, 18, 12, 16],
      average: 16.2,
      trendValues: [22, 19, 21, 14, 18, 12, 16],
    },
  },
  {
    player: { name: 'CJ Stroud', team: 'HOU', position: 'QB' },
    confidence: 78,
    propData: {
      statType: 'Rush Yds',
      betType: 'UNDER' as const,
      line: 14.5,
      projection: 8.3,
      cushion: -6.2,
      last5: [12, 5, 18, 3, 9],
      average: 9.4,
      trendValues: [15, 12, 5, 18, 3, 9],
    },
  },
  {
    player: { name: 'DeVonta Smith', team: 'PHI', position: 'WR' },
    confidence: 76,
    propData: {
      statType: 'Rec Yds',
      betType: 'UNDER' as const,
      line: 54.5,
      projection: 48.1,
      cushion: -6.4,
      last5: [62, 45, 38, 71, 55],
      average: 54.2,
      trendValues: [78, 55, 62, 45, 38, 71, 55],
    },
  },
  {
    player: { name: 'Aaron Rodgers', team: 'PIT', position: 'QB' },
    confidence: 83,
    propData: {
      statType: 'Rush Yds',
      betType: 'UNDER' as const,
      line: 0.5,
      projection: -1.2,
      cushion: -1.7,
      last5: [0, -2, 3, 0, 1],
      average: 0.4,
      trendValues: [5, 2, 0, -2, 3, 0, 1],
    },
  },
  {
    player: { name: 'Daniel Jones', team: 'IND', position: 'QB' },
    confidence: 81,
    propData: {
      statType: 'Rush Yds',
      betType: 'UNDER' as const,
      line: 13.5,
      projection: 9.8,
      cushion: -3.7,
      last5: [8, 15, 4, 11, 7],
      average: 9.0,
      trendValues: [18, 12, 8, 15, 4, 11, 7],
    },
  },
  {
    player: { name: 'Jaxson Dart', team: 'NYG', position: 'QB' },
    confidence: 65,
    propData: {
      statType: 'Pass Yds',
      betType: 'OVER' as const,
      line: 215.5,
      projection: 232.4,
      cushion: 16.9,
      last5: [245, 198, 220, 255, 210],
      average: 225.6,
      trendValues: [180, 210, 245, 198, 220, 255, 210],
    },
  },
];

export default function CardDemoScreen() {
  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Player Cards</Text>
          <Text style={styles.headerSub}>Week 13 Data Preview</Text>
        </View>

        {/* HERO Variant */}
        <Text style={styles.sectionLabel}>HERO VARIANT</Text>
        <AnimatedCard index={0}>
          <PlayerCard
            player={DEMO_PROPS[0].player}
            confidence={DEMO_PROPS[0].confidence}
            propData={DEMO_PROPS[0].propData}
            variant="hero"
          />
        </AnimatedCard>

        {/* STANDARD Variant */}
        <Text style={styles.sectionLabel}>STANDARD VARIANT</Text>
        {DEMO_PROPS.slice(1, 4).map((prop, i) => (
          <AnimatedCard key={prop.player.name} index={i + 1}>
            <PlayerCard
              player={prop.player}
              confidence={prop.confidence}
              propData={prop.propData}
              variant="standard"
              onPress={() => {}}
            />
          </AnimatedCard>
        ))}

        {/* COMPACT Variant */}
        <Text style={styles.sectionLabel}>COMPACT VARIANT</Text>
        {DEMO_PROPS.map((prop, i) => (
          <AnimatedCard key={`compact-${prop.player.name}`} index={i + 4}>
            <PlayerCard
              player={prop.player}
              confidence={prop.confidence}
              propData={prop.propData}
              variant="compact"
              subtitle={`${prop.propData.statType} ${prop.propData.betType} ${prop.propData.line}`}
              onPress={() => {}}
              rightContent={
                <ConfidenceGauge score={prop.confidence} size="sm" showLabel={false} />
              }
            />
          </AnimatedCard>
        ))}

        {/* Confidence Gauge Showcase */}
        <Text style={styles.sectionLabel}>CONFIDENCE GAUGES</Text>
        <View style={styles.gaugeRow}>
          <View style={styles.gaugeItem}>
            <ConfidenceGauge score={83} size="lg" />
            <Text style={styles.gaugeLabel}>Elite</Text>
          </View>
          <View style={styles.gaugeItem}>
            <ConfidenceGauge score={72} size="lg" />
            <Text style={styles.gaugeLabel}>Solid</Text>
          </View>
          <View style={styles.gaugeItem}>
            <ConfidenceGauge score={55} size="lg" />
            <Text style={styles.gaugeLabel}>Low</Text>
          </View>
        </View>

        <View style={{ height: 80 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scroll: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    ...theme.typography.h1,
    color: theme.colors.primary,
  },
  headerSub: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  sectionLabel: {
    ...theme.typography.caption,
    marginTop: 20,
    marginBottom: 10,
  },
  gaugeRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: theme.borderRadius.m,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 20,
  },
  gaugeItem: {
    alignItems: 'center',
  },
  gaugeLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 8,
    fontWeight: '600',
  },
});
