// Shared formatting utilities
export const formatCount = (n) => {
  if (n == null) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
};

export const formatScore = (n) =>
  n != null ? `${(n * 100).toFixed(1)}%` : "—";

export const truncate = (str, len = 120) =>
  str && str.length > len ? str.slice(0, len) + "…" : str;
