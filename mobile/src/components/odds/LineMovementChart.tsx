/**
 * LineMovementChart — Legacy wrapper that delegates to LineMovementChartV2.
 */

import React from 'react';
import { LineMovementEntry } from '../../types';
import LineMovementChartV2 from '../charts/LineMovementChartV2';

interface LineMovementChartProps {
  movements: LineMovementEntry[];
  currentLine?: number;
}

export default function LineMovementChart({ movements, currentLine }: LineMovementChartProps) {
  return <LineMovementChartV2 movements={movements} currentLine={currentLine} />;
}
