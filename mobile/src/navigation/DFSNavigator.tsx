/**
 * DFSNavigator — Stack navigator for DFS mode screens.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import DFSHomeScreen from '../screens/dfs/DFSHomeScreen';
import SlipBuilderScreen from '../screens/dfs/SlipBuilderScreen';
import DFSPlayerDetailScreen from '../screens/dfs/DFSPlayerDetailScreen';
import SuggestedSlipsScreen from '../screens/dfs/SuggestedSlipsScreen';

const Stack = createNativeStackNavigator();

export default function DFSNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="DFSHome" component={DFSHomeScreen} />
      <Stack.Screen name="SlipBuilder" component={SlipBuilderScreen} />
      <Stack.Screen name="DFSPlayerDetail" component={DFSPlayerDetailScreen} />
      <Stack.Screen name="SuggestedSlips" component={SuggestedSlipsScreen} />
    </Stack.Navigator>
  );
}
