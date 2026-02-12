/**
 * FantasyNavigator — Stack navigator for Fantasy mode screens.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import FantasyHomeScreen from '../screens/fantasy/FantasyHomeScreen';
import SleeperConnectScreen from '../screens/fantasy/SleeperConnectScreen';
import RosterScreen from '../screens/fantasy/RosterScreen';
import StartSitScreen from '../screens/fantasy/StartSitScreen';
import WaiverWireScreen from '../screens/fantasy/WaiverWireScreen';
import MatchupHeatmapScreen from '../screens/fantasy/MatchupHeatmapScreen';
import TradeAnalyzerScreen from '../screens/fantasy/TradeAnalyzerScreen';

const Stack = createNativeStackNavigator();

export default function FantasyNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="FantasyHome" component={FantasyHomeScreen} />
      <Stack.Screen name="SleeperConnect" component={SleeperConnectScreen} />
      <Stack.Screen name="Roster" component={RosterScreen} />
      <Stack.Screen name="StartSit" component={StartSitScreen} />
      <Stack.Screen name="WaiverWire" component={WaiverWireScreen} />
      <Stack.Screen name="MatchupHeatmap" component={MatchupHeatmapScreen} />
      <Stack.Screen name="TradeAnalyzer" component={TradeAnalyzerScreen} />
    </Stack.Navigator>
  );
}
