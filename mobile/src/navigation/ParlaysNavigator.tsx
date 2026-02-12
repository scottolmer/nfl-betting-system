/**
 * ParlaysNavigator — Stack navigator for Parlays mode (AI-generated parlays).
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AIParlaysScreen from '../screens/props/AIParlaysScreen';
import ParlayDetailScreen from '../screens/props/ParlayDetailScreen';
import PropDetailScreen from '../screens/props/PropDetailScreen';

const Stack = createNativeStackNavigator();

export default function ParlaysNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ParlaysHome" component={AIParlaysScreen} />
      <Stack.Screen name="ParlayDetail" component={ParlayDetailScreen} />
      <Stack.Screen name="PropDetail" component={PropDetailScreen} />
    </Stack.Navigator>
  );
}
