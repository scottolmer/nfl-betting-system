/**
 * PropsNavigator — Stack navigator for Props mode screens.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import PropsHomeScreen from '../screens/props/PropsHomeScreen';
import PropDetailScreen from '../screens/props/PropDetailScreen';
import EdgeFinderScreen from '../screens/props/EdgeFinderScreen';
import ParlayReviewScreen from '../screens/props/ParlayReviewScreen';

const Stack = createNativeStackNavigator();

export default function PropsNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="PropsHome" component={PropsHomeScreen} />
      <Stack.Screen name="PropDetail" component={PropDetailScreen} />
      <Stack.Screen name="EdgeFinder" component={EdgeFinderScreen} />
      <Stack.Screen name="ParlayReview" component={ParlayReviewScreen} />
    </Stack.Navigator>
  );
}
