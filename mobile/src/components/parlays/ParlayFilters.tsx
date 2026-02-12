/**
 * Parlay Filters Component
 * Filter pre-built parlays by leg count
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { theme } from '../../constants/theme';

export type FilterOption = 'all' | '2-leg' | '3-leg' | '4+';

interface ParlayFiltersProps {
  selectedFilter: FilterOption;
  onFilterChange: (filter: FilterOption) => void;
  counts?: {
    all: number;
    '2-leg': number;
    '3-leg': number;
    '4+': number;
  };
}

export default function ParlayFilters({
  selectedFilter,
  onFilterChange,
  counts,
}: ParlayFiltersProps) {
  const filters: { value: FilterOption; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: '2-leg', label: '2-Leg' },
    { value: '3-leg', label: '3-Leg' },
    { value: '4+', label: '4+' },
  ];

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {filters.map((filter) => {
        const isSelected = selectedFilter === filter.value;
        const count = counts?.[filter.value];

        return (
          <TouchableOpacity
            key={filter.value}
            style={[
              styles.filterButton,
              isSelected && styles.filterButtonActive,
            ]}
            onPress={() => onFilterChange(filter.value)}
          >
            <Text
              style={[
                styles.filterText,
                isSelected && styles.filterTextActive,
              ]}
            >
              {filter.label}
            </Text>
            {count !== undefined && (
              <View style={[
                styles.countBadge,
                isSelected && styles.countBadgeActive,
              ]}>
                <Text style={[
                  styles.countText,
                  isSelected && styles.countTextActive,
                ]}>
                  {count}
                </Text>
              </View>
            )}
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: theme.colors.backgroundElevated,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    gap: 6,
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
  filterTextActive: {
    color: '#FFFFFF',
  },
  countBadge: {
    backgroundColor: theme.colors.backgroundCard,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    minWidth: 20,
    alignItems: 'center',
  },
  countBadgeActive: {
    backgroundColor: theme.colors.backgroundCard,
  },
  countText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: theme.colors.textSecondary,
  },
  countTextActive: {
    color: theme.colors.primary,
  },
});
