/**
 * LoadingState Component
 * 
 * Displays loading skeletons while data is being fetched.
 */

interface LoadingStateProps {
  message?: string;
  rows?: number;
}

export function LoadingState({
  message = "Loading...",
  rows = 3,
}: LoadingStateProps) {
  return (
    <div className="space-y-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="h-16 bg-gray-200 rounded-md"></div>
        </div>
      ))}
      <p className="text-center text-sm text-gray-500 mt-4">{message}</p>
    </div>
  );
}

