/**
 * HeatmapCell — Single matchup cell with color gradient by DVOA/confidence.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../constants/theme';

interface HeatmapCellProps {
  statType: string;
  projection: number | null;
  confidence: number | null;
  matchupGrade: 'favorable' | 'neutral' | 'unfavorable';
  colorValue: number; // 0-100, maps to red→yellow→green
  compact?: boolean;
}

function getHeatColor(value: number): string {
  // 0 = red (bad matchup), 50 = yellow, 100 = green (good matchup)
  if (value >= 70) return '#22C55E';  // green
  if (value >= 55) return '#84CC16';  // lime
  if (value >= 45) return '#EAB308';  // yellow
  if (value >= 30) return '#F97316';  // orange
  return '#EF4444';                    // red
}

function formatStatType(stat: string): string {
  const labels: Record<string, string> = {
    pass_yds: 'PASS',
    rush_yds: 'RUSH',
    rec_yds: 'REC',
    receptions: 'REC',
    pass_tds: 'TD',
    rush_tds: 'TD',
    rec_tds: 'TD',
  };
  return labels[stat] || stat.toUpperCase().slice(0, 4);
}

export default function HeatmapCell({
  statType,
  projection,
  confidence,
  matchupGrade,
  colorValue,
  compact,
}: HeatmapCellProps) {
  const bgColor = getHeatColor(colorValue);

  if (compact) {
    return (
      <View style={[styles.compactCell, { backgroundColor: bgColor + '25' }]}>
        <Text style={[styles.compactLabel, { color: bgColor }]}>
          {formatStatType(statType)}
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.cell, { backgroundColor: bgColor + '15', borderColor: bgColor + '30' }]}>
      <Text style={styles.statLabel}>{formatStatType(statType)}</Text>
      <Text style={[styles.projection, { color: bgColor }]}>
        {projection != null ? projection.toFixed(1) : '—'}
      </Text>
      <Text style={styles.gradeText}>
        {matchupGrade === 'favorable' ? 'Good' : matchupGrade === 'unfavorable' ? 'Bad' : 'Avg'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  cell: {
    width: 70,
    height: 70,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 4,
  },
  statLabel: {
    fontSize: 9,
    fontWeight: '700',
    color: theme.colors.textTertiary,
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  projection: {
    fontSize: 16,
    fontWeight: '800',
  },
  gradeText: {
    fontSize: 8,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  compactCell: {
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  compactLabel: {
    fontSize: 10,
    fontWeight: '700',
  },
});
