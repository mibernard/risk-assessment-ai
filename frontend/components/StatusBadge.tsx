/**
 * StatusBadge Component
 * 
 * Displays status badge with color coding.
 */

import { getStatusColor, type Case } from "@/lib/api";

interface StatusBadgeProps {
  status: Case["status"];
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const { color, textColor } = getStatusColor(status);

  const label = status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color} ${textColor}`}
    >
      {label}
    </span>
  );
}

