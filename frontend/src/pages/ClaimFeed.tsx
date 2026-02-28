import { motion } from "framer-motion";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import NewsCard from "@/components/NewsCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, FeedClaim } from "@/services/api";
import { Loader2, AlertCircle } from "lucide-react";
import { formatDate } from "@/utils/helpers";

type ClaimStatus = "verified" | "disputed" | "pending";

function getClaimStatus(trueVotes: number, falseVotes: number): ClaimStatus {
  const total = trueVotes + falseVotes;
  if (total === 0) return "pending";
  const truePercent = (trueVotes / total) * 100;
  if (truePercent >= 70) return "verified";
  if (truePercent <= 30) return "disputed";
  return "pending";
}

const ClaimFeed = () => {
  const [filter, setFilter] = useState<"all" | ClaimStatus>("all");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['feed'],
    queryFn: api.getFeed,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const claims = data?.claims || [];
  
  const filtered = filter === "all" 
    ? claims 
    : claims.filter((c) => {
        const totalVotes = c.userTrueVotes + c.userFalseVotes;
        const status = getClaimStatus(c.userTrueVotes, c.userFalseVotes);
        return status === filter;
      });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen pt-24 pb-16 px-4 md:pl-24 md:pr-8"
    >
      <div className="max-w-[1200px] mx-auto space-y-8">
        <div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-3">Claim Feed</h1>
          <p className="text-base text-muted-foreground leading-relaxed max-w-lg">
            Browse the decentralized ledger of verified and disputed claims.
          </p>
        </div>

        <Tabs defaultValue="all" onValueChange={(v) => setFilter(v as typeof filter)}>
          <TabsList className="bg-card border border-border rounded-xl p-1">
            <TabsTrigger value="all" className="rounded-lg text-sm data-[state=active]:bg-primary/15 data-[state=active]:text-primary font-medium">
              All
            </TabsTrigger>
            <TabsTrigger value="verified" className="rounded-lg text-sm data-[state=active]:bg-success/15 data-[state=active]:text-success font-medium">
              Verified
            </TabsTrigger>
            <TabsTrigger value="disputed" className="rounded-lg text-sm data-[state=active]:bg-warning/15 data-[state=active]:text-warning font-medium">
              Disputed
            </TabsTrigger>
            <TabsTrigger value="pending" className="rounded-lg text-sm data-[state=active]:bg-muted data-[state=active]:text-foreground font-medium">
              Pending
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="gradient-divider" />

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="glass-card p-8 flex items-center gap-4 text-destructive">
            <AlertCircle className="w-5 h-5" />
            <div>
              <p className="font-semibold">Failed to load claims</p>
              <p className="text-sm text-muted-foreground">{error.message}</p>
              <button 
                onClick={() => refetch()} 
                className="text-sm underline mt-2"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {!isLoading && !error && (
          <div className="space-y-6">
            {filtered.map((claim, i) => {
              const totalVotes = claim.userTrueVotes + claim.userFalseVotes;
              const status = getClaimStatus(claim.userTrueVotes, claim.userFalseVotes);
              
              return (
                <motion.div
                  key={claim.claimHash}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                >
                  <Link to={`/claim/${claim.claimHash}`}>
                    <NewsCard
                      claimHash={claim.claimHash}
                      contentCID={claim.contentCID}
                      status={status}
                      totalVotes={totalVotes}
                      trueVotes={claim.userTrueVotes}
                      falseVotes={claim.userFalseVotes}
                      timestamp={formatDate(claim.timestamp)}
                    />
                  </Link>
                </motion.div>
              );
            })}
            {filtered.length === 0 && !isLoading && (
              <div className="text-center py-16 text-muted-foreground">
                No claims found for this filter.
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ClaimFeed;
