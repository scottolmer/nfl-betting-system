/**
 * PlayerSearchBar — Universal debounced search across all modes.
 * Shows dropdown results with player cards.
 */

import React, { useState, useCallback, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Keyboard,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';

interface SearchResult {
  id: number;
  name: string;
  team: string;
  position: string;
  headshot_url?: string;
}

interface PlayerSearchBarProps {
  onSelectPlayer: (player: SearchResult) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

export default function PlayerSearchBar({
  onSelectPlayer,
  placeholder = 'Search any player...',
  autoFocus = false,
}: PlayerSearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleSearch = useCallback(
    (text: string) => {
      setQuery(text);

      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      if (text.length < 2) {
        setResults([]);
        setShowResults(false);
        return;
      }

      debounceRef.current = setTimeout(async () => {
        setSearching(true);
        try {
          const resp = await apiService['client'].get('/api/players/search', {
            params: { q: text, limit: 8 },
          });
          setResults(resp.data);
          setShowResults(true);
        } catch {
          setResults([]);
        } finally {
          setSearching(false);
        }
      }, 300);
    },
    [],
  );

  const handleSelect = (player: SearchResult) => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    Keyboard.dismiss();
    onSelectPlayer(player);
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setShowResults(false);
  };

  const getInitials = (name: string) => {
    const parts = name.split(' ');
    return parts.length >= 2
      ? `${parts[0][0]}${parts[parts.length - 1][0]}`
      : name.slice(0, 2);
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputRow}>
        <Ionicons name="search" size={16} color={theme.colors.textTertiary} />
        <TextInput
          style={styles.input}
          placeholder={placeholder}
          placeholderTextColor={theme.colors.textTertiary}
          value={query}
          onChangeText={handleSearch}
          autoFocus={autoFocus}
          returnKeyType="search"
        />
        {query.length > 0 && (
          <TouchableOpacity onPress={handleClear}>
            <Ionicons name="close-circle" size={16} color={theme.colors.textTertiary} />
          </TouchableOpacity>
        )}
      </View>

      {/* Results dropdown */}
      {showResults && results.length > 0 && (
        <View style={styles.dropdown}>
          <FlatList
            data={results}
            keyExtractor={(item) => `${item.id}`}
            keyboardShouldPersistTaps="handled"
            style={styles.resultsList}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.resultItem}
                onPress={() => handleSelect(item)}
                activeOpacity={0.7}
              >
                <View style={styles.avatar}>
                  <Text style={styles.avatarText}>{getInitials(item.name)}</Text>
                </View>
                <View style={styles.resultInfo}>
                  <Text style={styles.resultName}>{item.name}</Text>
                  <Text style={styles.resultMeta}>{item.team} · {item.position}</Text>
                </View>
                <Ionicons name="chevron-forward" size={14} color={theme.colors.textTertiary} />
              </TouchableOpacity>
            )}
          />
        </View>
      )}

      {showResults && results.length === 0 && query.length >= 2 && !searching && (
        <View style={styles.noResults}>
          <Text style={styles.noResultsText}>No players found</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    zIndex: 100,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.glassInput,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    paddingHorizontal: 12,
    height: 42,
    gap: 8,
  },
  input: {
    flex: 1,
    color: theme.colors.textPrimary,
    fontSize: 14,
  },
  dropdown: {
    position: 'absolute',
    top: 46,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.backgroundDark,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    overflow: 'hidden',
    maxHeight: 300,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  resultsList: {
    maxHeight: 300,
  },
  resultItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
    gap: 10,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 11,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  resultInfo: {
    flex: 1,
  },
  resultName: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  resultMeta: {
    fontSize: 11,
    color: theme.colors.textTertiary,
  },
  noResults: {
    position: 'absolute',
    top: 46,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.backgroundDark,
    borderRadius: theme.borderRadius.s,
    borderWidth: 1,
    borderColor: theme.colors.glassBorder,
    padding: 16,
    alignItems: 'center',
  },
  noResultsText: {
    fontSize: 13,
    color: theme.colors.textTertiary,
  },
});
