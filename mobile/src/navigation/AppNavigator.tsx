/**
 * AppNavigator V2 — Pure black tab bar, cyan active icon, subtle dot indicator,
 * 4% white opacity top border.
 */

import React, { useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer, NavigationContainerRef } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../constants/theme';
import { useMode } from '../contexts/ModeContext';

// Mode navigators
import PropsNavigator from './PropsNavigator';
import ParlaysNavigator from './ParlaysNavigator';

// Shared screens
import HomeScreen from '../screens/HomeScreen';
import DiscoverScreen from '../screens/DiscoverScreen';
import BetSlipScreen from '../screens/props/BetSlipScreen';
import MoreScreen from '../screens/MoreScreen';

// Components
import ModeSwitcher from '../components/navigation/ModeSwitcher';

const Tab = createBottomTabNavigator();

function ModeHome() {
  const { mode } = useMode();

  switch (mode) {
    case 'parlays':
      return <ParlaysNavigator />;
    case 'props':
    default:
      return <PropsNavigator />;
  }
}

function TabDot({ focused }: { focused: boolean }) {
  if (!focused) return null;
  return (
    <View style={styles.activeDot} />
  );
}

export default function AppNavigator() {
  const navigationRef = useRef<NavigationContainerRef<any>>(null);

  const handleModeChange = (mode: string) => {
    // Navigate to the Home tab and target the specific root screen for that mode
    // This ensures we don't land on a stale 'PropDetail' screen if the user was deep in the stack
    navigationRef.current?.navigate('Home', {
      screen: mode === 'parlays' ? 'ParlaysHome' : 'PropsHome'
    });
  };

  return (
    <NavigationContainer ref={navigationRef}>
      <View style={styles.container}>
        {/* Mode switcher fixed at top */}
        <View style={styles.modeSwitcherBar}>
          <ModeSwitcher onModeChange={handleModeChange} />
        </View>

        {/* Bottom tab navigator */}
        <Tab.Navigator
          screenOptions={{
            headerShown: false,
            tabBarStyle: {
              backgroundColor: '#000000',
              borderTopColor: 'rgba(255, 255, 255, 0.04)',
              borderTopWidth: 1,
              height: 64,
              paddingBottom: 10,
              paddingTop: 8,
            },
            tabBarActiveTintColor: theme.colors.primary,
            tabBarInactiveTintColor: theme.colors.textTertiary,
            tabBarLabelStyle: {
              fontSize: 11,
              fontWeight: '600',
            },
          }}
        >
          <Tab.Screen
            name="Discover"
            component={DiscoverScreen}
            options={{
              tabBarIcon: ({ color, focused }) => (
                <View style={styles.tabIconContainer}>
                  <Ionicons name={focused ? 'compass' : 'compass-outline'} size={22} color={color} />
                  <TabDot focused={focused} />
                </View>
              ),
            }}
          />
          <Tab.Screen
            name="Home"
            component={ModeHome}
            options={{
              tabBarIcon: ({ color, focused }) => (
                <View style={styles.tabIconContainer}>
                  <Ionicons name={focused ? 'home' : 'home-outline'} size={22} color={color} />
                  <TabDot focused={focused} />
                </View>
              ),
            }}
          />
          <Tab.Screen
            name="My Bets"
            component={BetSlipScreen}
            options={{
              tabBarIcon: ({ color, focused }) => (
                <View style={styles.tabIconContainer}>
                  <Ionicons name={focused ? 'receipt' : 'receipt-outline'} size={22} color={color} />
                  <TabDot focused={focused} />
                </View>
              ),
            }}
          />
          <Tab.Screen
            name="More"
            component={MoreScreen}
            options={{
              tabBarIcon: ({ color, focused }) => (
                <View style={styles.tabIconContainer}>
                  <Ionicons name={focused ? 'person' : 'person-outline'} size={22} color={color} />
                  <TabDot focused={focused} />
                </View>
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
    backgroundColor: '#000000',
  },
  modeSwitcherBar: {
    paddingTop: 50,
    paddingBottom: 8,
    backgroundColor: '#000000',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.04)',
    alignItems: 'center',
  },
  tabIconContainer: {
    alignItems: 'center',
  },
  activeDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: theme.colors.primary,
    marginTop: 2,
  },
});
