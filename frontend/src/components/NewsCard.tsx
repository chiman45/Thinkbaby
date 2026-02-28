import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { ArrowUp, ArrowDown, Star } from "lucide-react";

interface NewsCardProps {
  claimHash: string;
  contentCID: string | null;
  status: "verified" | "disputed" | "pending";
  totalVotes: number;
  trueVotes: number;
  falseVotes: number;
  timestamp: string;
}

const NewsCard = ({
  claimHash,
  contentCID,
  status,
  totalVotes,
  trueVotes,
  falseVotes,
  timestamp,
}: NewsCardProps) => {
  const statusConfig = {
    verified: { label: "Verified", className: "bg-success/15 text-success border-success/30 badge-pulse-green" },
    disputed: { label: "Under Dispute", className: "bg-warning/15 text-warning border-warning/30 badge-pulse-amber" },
    pending: { label: "Pending", className: "bg-muted text-muted-foreground border-border" },
  };

  const config = statusConfig[status];
  const truePercent = totalVotes > 0 ? Math.round((trueVotes / totalVotes) * 100) : 50;

  // Split votes into user and validator (for demo, assume 70/30 split)
  const userTrueVotes = Math.floor(trueVotes * 0.7);
  const userFalseVotes = Math.floor(falseVotes * 0.7);
  const validatorTrueVotes = trueVotes - userTrueVotes;
  const validatorFalseVotes = falseVotes - userFalseVotes;

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card-hover p-0 overflow-hidden cursor-pointer"
    >
      <div className="flex">
        {/* Left: Vote Column (Reddit-style) */}
        <div className="flex flex-col items-center gap-2 bg-secondary/30 px-4 py-6 border-r border-border">
          <button className="text-muted-foreground hover:text-success transition-colors">
            <ArrowUp className="w-5 h-5" />
          </button>
          <span className="font-mono text-lg font-bold text-foreground">
            {trueVotes - falseVotes}
          </span>
          <button className="text-muted-foreground hover:text-destructive transition-colors">
            <ArrowDown className="w-5 h-5" />
          </button>
        </div>

        {/* Right: Content */}
        <div className="flex-1 p-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className={`rounded-full px-3 py-1 text-xs font-semibold ${config.className}`}>
                  {config.label}
                </Badge>
                <span className="text-xs text-muted-foreground">{timestamp}</span>
              </div>
              <p className="text-xs text-muted-foreground font-mono mb-1">
                Hash: {claimHash.slice(0, 16)}...
              </p>
              {contentCID && (
                <p className="text-xs text-muted-foreground">
                  CID: {contentCID.slice(0, 20)}...
                </p>
              )}
            </div>
          </div>

          {/* Vote Stats */}
          <div className="space-y-3">
            {/* User Votes */}
            <div className="flex items-center gap-4 text-sm">
              <span className="text-muted-foreground font-medium min-w-[100px]">User Votes:</span>
              <div className="flex items-center gap-4">
                <span className="text-success font-semibold flex items-center gap-1">
                  {userTrueVotes} 👍
                </span>
                <span className="text-muted-foreground">|</span>
                <span className="text-destructive font-semibold flex items-center gap-1">
                  {userFalseVotes} 👎
                </span>
              </div>
            </div>

            {/* Validator Votes */}
            <div className="flex items-center gap-4 text-sm">
              <span className="text-amber-400 font-medium min-w-[100px] flex items-center gap-1">
                <Star className="w-3 h-3 fill-current" />
                Validator Votes:
              </span>
              <div className="flex items-center gap-4">
                <span className="text-success font-semibold flex items-center gap-1">
                  {validatorTrueVotes} 👍
                </span>
                <span className="text-muted-foreground">|</span>
                <span className="text-destructive font-semibold flex items-center gap-1">
                  {validatorFalseVotes} 👎
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="flex items-center gap-3 pt-2">
              <div className="h-2 flex-1 rounded-full bg-secondary overflow-hidden flex">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${truePercent}%` }}
                  transition={{ duration: 1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  className="h-full"
                  style={{ background: 'hsl(160 84% 39%)' }}
                />
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${100 - truePercent}%` }}
                  transition={{ duration: 1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  className="h-full"
                  style={{ background: 'hsl(0 84% 60%)' }}
                />
              </div>
              <span className="text-xs font-semibold text-muted-foreground min-w-[50px]">
                {truePercent}% true
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default NewsCard;
