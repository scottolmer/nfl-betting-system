import React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import ChatHomeScreen from '../screens/ChatHomeScreen';
import ParlaysScreen from '../screens/ParlaysScreen';
import BuildScreen from '../screens/BuildScreen';
import ResultsScreen from '../screens/ResultsScreen';
import MoreScreen from '../screens/MoreScreen';
import { theme } from '../constants/theme';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarStyle: {
            backgroundColor: theme.colors.background,
            borderTopColor: theme.colors.glassBorder,
            borderTopWidth: 1,
            height: 60,
            paddingBottom: 8,
            paddingTop: 8,
          },
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.textSecondary,
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: '600',
          },
        }}
      >
        <Tab.Screen
          name="Chat"
          component={ChatHomeScreen}
          options={{
            tabBarLabel: 'Agent',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="chatbubble-ellipses-outline" size={24} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Pre-Built"
          component={ParlaysScreen}
          options={{
            tabBarLabel: 'Pre-Built',
            tabBarIcon: ({ color }) => (
              <Ionicons name="flash-outline" size={24} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="My Parlays"
          component={BuildScreen}
          options={{
            tabBarLabel: 'My Parlays',
            tabBarIcon: ({ color }) => (
              <Ionicons name="construct-outline" size={24} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Results"
          component={ResultsScreen}
          options={{
            tabBarLabel: 'Results',
            tabBarIcon: ({ color }) => (
              <Ionicons name="stats-chart-outline" size={24} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="More"
          component={MoreScreen}
          options={{
            tabBarLabel: 'More',
            tabBarIcon: ({ color }) => (
              <Ionicons name="menu-outline" size={24} color={color} />
            ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}


