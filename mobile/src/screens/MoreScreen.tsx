import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import HelpSection from '../components/more/HelpSection';
import TutorialModal from '../components/modals/TutorialModal';
import { onboardingPreferences, sportsbookPreferences } from '../services/userPreferences';
import { theme } from '../constants/theme';

const SPORTSBOOKS = [
  { id: 'auto', label: 'Auto (Median Line)', desc: 'Uses median line across all books' },
  { id: 'draftkings', label: 'DraftKings', desc: 'DraftKings Sportsbook lines' },
  { id: 'fanduel', label: 'FanDuel', desc: 'FanDuel Sportsbook lines' },
  { id: 'betmgm', label: 'BetMGM', desc: 'BetMGM Sportsbook lines' },
  { id: 'caesars', label: 'Caesars', desc: 'Caesars Sportsbook lines' },
  { id: 'espnbet', label: 'ESPN Bet', desc: 'ESPN Bet lines' },
];

export default function MoreScreen() {
  const [showTutorial, setShowTutorial] = useState(false);
  const [selectedBook, setSelectedBook] = useState('auto');
  const [showBookPicker, setShowBookPicker] = useState(false);

  useEffect(() => {
    sportsbookPreferences.getPreferredSportsbook().then((book) => {
      if (book) setSelectedBook(book);
    });
  }, []);

  const handleViewTutorial = () => {
    setShowTutorial(true);
  };

  const handleResetTutorial = async () => {
    Alert.alert(
      'Reset Tutorial',
      'The onboarding tutorial will be shown the next time you launch the app.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          onPress: async () => {
            await onboardingPreferences.resetOnboarding();
            Alert.alert('Success', 'Tutorial reset! It will appear on next launch.');
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Tutorial Modal */}
      <TutorialModal visible={showTutorial} onClose={() => setShowTutorial(false)} />

      <View style={styles.header}>
        <Text style={styles.headerTitle}>More</Text>
        <Text style={styles.headerSubtitle}>Settings & Info</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Help & Learning Section */}
        <HelpSection
          onViewTutorial={handleViewTutorial}
          onResetTutorial={handleResetTutorial}
        />

        {/* App Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App Info</Text>
          <View style={styles.infoCardsContainer}>
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>Version</Text>
              <Text style={styles.infoValue}>1.0.0 (MVP)</Text>
            </View>
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>Backend</Text>
              <Text style={styles.infoValue}>FastAPI + 9-Agent System</Text>
            </View>
          </View>
        </View>

        {/* Sportsbook Preference */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sportsbook</Text>
          <View style={styles.menuItemsContainer}>
            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => setShowBookPicker(!showBookPicker)}
            >
              <View style={styles.menuItemLeft}>
                <Ionicons name="book-outline" size={18} color={theme.colors.primary} />
                <View style={styles.menuItemContent}>
                  <Text style={styles.menuItemText}>Preferred Sportsbook</Text>
                  <Text style={styles.menuItemDesc}>
                    Props use lines from your preferred book
                  </Text>
                </View>
              </View>
              <View style={styles.menuItemRight}>
                <Text style={styles.selectedBookLabel}>
                  {SPORTSBOOKS.find(b => b.id === selectedBook)?.label || 'Auto'}
                </Text>
                <Ionicons
                  name={showBookPicker ? 'chevron-up' : 'chevron-down'}
                  size={16}
                  color={theme.colors.textTertiary}
                />
              </View>
            </TouchableOpacity>

            {showBookPicker && SPORTSBOOKS.map((book) => (
              <TouchableOpacity
                key={book.id}
                style={[
                  styles.bookOption,
                  selectedBook === book.id && styles.bookOptionSelected,
                ]}
                onPress={async () => {
                  setSelectedBook(book.id);
                  await sportsbookPreferences.setPreferredSportsbook(book.id);
                  setShowBookPicker(false);
                }}
              >
                <View style={styles.bookOptionLeft}>
                  <View style={[
                    styles.radioOuter,
                    selectedBook === book.id && styles.radioOuterSelected,
                  ]}>
                    {selectedBook === book.id && <View style={styles.radioInner} />}
                  </View>
                  <View>
                    <Text style={[
                      styles.bookOptionLabel,
                      selectedBook === book.id && styles.bookOptionLabelSelected,
                    ]}>
                      {book.label}
                    </Text>
                    <Text style={styles.bookOptionDesc}>{book.desc}</Text>
                  </View>
                </View>
                {selectedBook === book.id && (
                  <Ionicons name="checkmark-circle" size={18} color={theme.colors.primary} />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Coming Soon Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Coming Soon</Text>
          <View style={styles.menuItemsContainer}>
            <TouchableOpacity style={styles.menuItem}>
              <View style={styles.menuItemLeft}>
                <Ionicons name="options-outline" size={18} color={theme.colors.textTertiary} />
                <Text style={styles.menuItemText}>Agent Customization</Text>
              </View>
              <Text style={styles.menuItemArrow}>></Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.menuItem}>
              <View style={styles.menuItemLeft}>
                <Ionicons name="analytics-outline" size={18} color={theme.colors.textTertiary} />
                <Text style={styles.menuItemText}>System Performance</Text>
              </View>
              <Text style={styles.menuItemArrow}>></Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.menuItem}>
              <View style={styles.menuItemLeft}>
                <Ionicons name="notifications-outline" size={18} color={theme.colors.textTertiary} />
                <Text style={styles.menuItemText}>Notifications</Text>
              </View>
              <Text style={styles.menuItemArrow}>></Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <View style={styles.aboutCard}>
            <Text style={styles.aboutText}>
              NFL Betting Analysis App uses a 9-agent system to analyze player props and
              generate high-confidence parlays. Built with React Native and FastAPI.
            </Text>
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Made with ⚡ by AI-powered prop analysis
          </Text>
        </View>
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
    backgroundColor: theme.colors.backgroundCard,
    padding: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: theme.colors.textTertiary,
  },
  content: {
    padding: 20,
    paddingTop: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.textPrimary,
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  infoCardsContainer: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 12,
    marginHorizontal: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  infoCard: {
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  infoLabel: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  menuItemsContainer: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 12,
    marginHorizontal: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  menuItem: {
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  menuItemContent: {
    flex: 1,
  },
  menuItemRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  menuItemText: {
    fontSize: 16,
    color: theme.colors.textPrimary,
  },
  menuItemDesc: {
    fontSize: 12,
    color: theme.colors.textTertiary,
    marginTop: 2,
  },
  menuItemArrow: {
    fontSize: 18,
    color: theme.colors.textTertiary,
  },
  selectedBookLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  bookOption: {
    padding: 14,
    paddingLeft: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
  },
  bookOptionSelected: {
    backgroundColor: 'rgba(10, 226, 163, 0.06)',
  },
  bookOptionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  radioOuter: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: theme.colors.textTertiary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioOuterSelected: {
    borderColor: theme.colors.primary,
  },
  radioInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.colors.primary,
  },
  bookOptionLabel: {
    fontSize: 15,
    color: theme.colors.textPrimary,
  },
  bookOptionLabelSelected: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  bookOptionDesc: {
    fontSize: 11,
    color: theme.colors.textTertiary,
    marginTop: 1,
  },
  aboutCard: {
    backgroundColor: theme.colors.backgroundCard,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  aboutText: {
    fontSize: 15,
    color: theme.colors.textSecondary,
    lineHeight: 22,
  },
  footer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 13,
    color: theme.colors.textTertiary,
  },
});
