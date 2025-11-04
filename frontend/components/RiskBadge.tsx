/**
 * RiskBadge Component
 * 
 * Displays a color-coded risk score badge with label.
 */

import { getRiskLevel } from "@/lib/api";

interface RiskBadgeProps {
  score: number;
  showLabel?: boolean;
}

export function RiskBadge({ score, showLabel = true }: RiskBadgeProps) {
  const { label, color, textColor } = getRiskLevel(score);

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color} ${textColor}`}
    >
      {score.toFixed(2)}
      {showLabel && <span className="ml-1">{label}</span>}
    </span>
  );
}

