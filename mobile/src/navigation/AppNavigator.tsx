/**
 * AppNavigator — Mode switcher (DFS | Props | Fantasy) at top,
 * bottom tabs (Discover / Home / My Bets / Profile) below.
 * Discover shows unified cross-pillar feed.
 * Home shows the current mode's navigator.
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import { useMode } from '../contexts/ModeContext';

// Mode navigators
import PropsNavigator from './PropsNavigator';
import DFSNavigator from './DFSNavigator';
import FantasyNavigator from './FantasyNavigator';

// Shared screens
import HomeScreen from '../screens/HomeScreen';
import BetSlipScreen from '../screens/props/BetSlipScreen';
import MoreScreen from '../screens/MoreScreen';

// Components
import ModeSwitcher from '../components/navigation/ModeSwitcher';

const Tab = createBottomTabNavigator();

function ModeHome() {
  const { mode } = useMode();

  switch (mode) {
    case 'dfs':
      return <DFSNavigator />;
    case 'fantasy':
      return <FantasyNavigator />;
    case 'props':
    default:
      return <PropsNavigator />;
  }
}

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <View style={styles.container}>
        {/* Mode switcher fixed at top */}
        <View style={styles.modeSwitcherBar}>
          <ModeSwitcher />
        </View>

        {/* Bottom tab navigator */}
        <Tab.Navigator
          screenOptions={{
            headerShown: false,
            tabBarStyle: {
              backgroundColor: theme.colors.backgroundDark,
              borderTopColor: theme.colors.glassBorder,
              borderTopWidth: 1,
              height: 60,
              paddingBottom: 8,
              paddingTop: 8,
            },
            tabBarActiveTintColor: theme.colors.primary,
            tabBarInactiveTintColor: theme.colors.textSecondary,
            tabBarLabelStyle: {
              fontSize: 11,
              fontWeight: '600',
            },
          }}
        >
          <Tab.Screen
            name="Discover"
            component={HomeScreen}
            options={{
              tabBarIcon: ({ color }) => (
                <Ionicons name="compass-outline" size={22} color={color} />
              ),
            }}
          />
          <Tab.Screen
            name="Home"
            component={ModeHome}
            options={{
              tabBarIcon: ({ color }) => (
                <Ionicons name="home-outline" size={22} color={color} />
              ),
            }}
          />
          <Tab.Screen
            name="My Bets"
            component={BetSlipScreen}
            options={{
              tabBarIcon: ({ color }) => (
                <Ionicons name="receipt-outline" size={22} color={color} />
              ),
            }}
          />
          <Tab.Screen
            name="More"
            component={MoreScreen}
            options={{
              tabBarIcon: ({ color }) => (
                <Ionicons name="person-outline" size={22} color={color} />
              ),
              tabBarLabel: 'Profile',
            }}
          />
        </Tab.Navigator>
      </View>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  modeSwitcherBar: {
    paddingTop: 50,
    paddingBottom: 8,
    backgroundColor: theme.colors.backgroundDark,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.glassBorder,
    alignItems: 'center',
  },
});
