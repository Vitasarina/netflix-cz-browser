export function SkeletonCard() {
  return (
    <div className="rounded-md overflow-hidden animate-pulse bg-[#2f2f2f]">
      <div className="aspect-[2/3] bg-[#3a3a3a]" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-[#3a3a3a] rounded w-3/4" />
        <div className="h-3 bg-[#3a3a3a] rounded w-1/2" />
        <div className="h-3 bg-[#3a3a3a] rounded w-full" />
        <div className="h-3 bg-[#3a3a3a] rounded w-4/5" />
      </div>
    </div>
  );
}
