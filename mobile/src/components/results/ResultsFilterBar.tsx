/**
 * Results Filter Bar
 * Filter results by week, status, and confidence
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

export interface ResultsFilters {
  week?: number;
  status?: 'all' | 'won' | 'lost' | 'pending';
  minConfidence?: number;
}

interface ResultsFilterBarProps {
  filters: ResultsFilters;
  onFilterChange: (filters: ResultsFilters) => void;
  availableWeeks: number[];
}

export default function ResultsFilterBar({
  filters,
  onFilterChange,
  availableWeeks,
}: ResultsFilterBarProps) {
  const statusOptions = [
    { value: 'all', label: 'All' },
    { value: 'won', label: 'Won' },
    { value: 'lost', label: 'Lost' },
    { value: 'pending', label: 'Pending' },
  ];

  const confidenceOptions = [
    { value: undefined, label: 'All Confidence' },
    { value: 80, label: '80%+' },
    { value: 75, label: '75%+' },
    { value: 70, label: '70%+' },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionLabel}>Week</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.optionsContainer}
        >
          <TouchableOpacity
            style={[styles.option, filters.week === undefined && styles.optionActive]}
            onPress={() => onFilterChange({ ...filters, week: undefined })}
          >
            <Text
              style={[
                styles.optionText,
                filters.week === undefined && styles.optionTextActive,
              ]}
            >
              All Weeks
            </Text>
          </TouchableOpacity>

          {availableWeeks.map(week => (
            <TouchableOpacity
              key={week}
              style={[styles.option, filters.week === week && styles.optionActive]}
              onPress={() => onFilterChange({ ...filters, week })}
            >
              <Text
                style={[
                  styles.optionText,
                  filters.week === week && styles.optionTextActive,
                ]}
              >
                Week {week}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>Status</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.optionsContainer}
        >
          {statusOptions.map(option => (
            <TouchableOpacity
              key={option.value}
              style={[
                styles.option,
                (filters.status || 'all') === option.value && styles.optionActive,
              ]}
              onPress={() =>
                onFilterChange({
                  ...filters,
                  status: option.value as ResultsFilters['status'],
                })
              }
            >
              <Text
                style={[
                  styles.optionText,
                  (filters.status || 'all') === option.value && styles.optionTextActive,
                ]}
              >
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionLabel}>Confidence</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.optionsContainer}
        >
          {confidenceOptions.map(option => (
            <TouchableOpacity
              key={option.value || 'all'}
              style={[
                styles.option,
                filters.minConfidence === option.value && styles.optionActive,
              ]}
              onPress={() =>
                onFilterChange({ ...filters, minConfidence: option.value })
              }
            >
              <Text
                style={[
                  styles.optionText,
                  filters.minConfidence === option.value && styles.optionTextActive,
                ]}
              >
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    paddingVertical: 12,
  },
  section: {
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  sectionLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  optionsContainer: {
    gap: 8,
  },
  option: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  optionActive: {
    backgroundColor: '#3B82F6',
    borderColor: '#2563EB',
  },
  optionText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#4B5563',
  },
  optionTextActive: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
