export function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Quick Actions Skeleton */}
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-xl"></div>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        {[1, 2].map((i) => (
          <div key={i} className="h-64 bg-gray-100 rounded-xl"></div>
        ))}
      </div>

      {/* Stats Skeleton */}
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-20 bg-gray-100 rounded-xl"></div>
        ))}
      </div>
    </div>
  );
}
