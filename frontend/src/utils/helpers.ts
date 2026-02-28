export const truncateAddress = (address: string): string => {
  if (!address) return "";
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

export const formatDate = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

export const getReputationTier = (score: number): "bronze" | "silver" | "gold" => {
  if (score >= 800) return "gold";
  if (score >= 500) return "silver";
  return "bronze";
};
