import React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import HomeScreen from '../screens/HomeScreen';
import ParlaysScreen from '../screens/ParlaysScreen';
import BuildScreen from '../screens/BuildScreen';
import MyBetsScreen from '../screens/MyBetsScreen';
import MoreScreen from '../screens/MoreScreen';

const Tab = createBottomTabNavigator();

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarStyle: {
            backgroundColor: '#FFFFFF',
            borderTopColor: '#E5E7EB',
            borderTopWidth: 1,
            height: 60,
            paddingBottom: 8,
            paddingTop: 8,
          },
          tabBarActiveTintColor: '#3B82F6',
          tabBarInactiveTintColor: '#6B7280',
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: '600',
          },
        }}
      >
        <Tab.Screen
          name="Home"
          component={HomeScreen}
          options={{
            tabBarLabel: 'Home',
            tabBarIcon: ({ color }) => <TabIcon icon="🏠" color={color} />,
          }}
        />
        <Tab.Screen
          name="Parlays"
          component={ParlaysScreen}
          options={{
            tabBarLabel: 'Parlays',
            tabBarIcon: ({ color }) => <TabIcon icon="🎰" color={color} />,
          }}
        />
        <Tab.Screen
          name="Build"
          component={BuildScreen}
          options={{
            tabBarLabel: 'Build',
            tabBarIcon: ({ color }) => <TabIcon icon="⚡" color={color} />,
          }}
        />
        <Tab.Screen
          name="My Bets"
          component={MyBetsScreen}
          options={{
            tabBarLabel: 'My Bets',
            tabBarIcon: ({ color }) => <TabIcon icon="📊" color={color} />,
          }}
        />
        <Tab.Screen
          name="More"
          component={MoreScreen}
          options={{
            tabBarLabel: 'More',
            tabBarIcon: ({ color }) => <TabIcon icon="⚙️" color={color} />,
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

// Simple emoji-based tab icon component
function TabIcon({ icon, color }: { icon: string; color: string }) {
  return (
    <Text style={{ fontSize: 24, opacity: color === '#3B82F6' ? 1 : 0.6 }}>
      {icon}
    </Text>
  );
}
