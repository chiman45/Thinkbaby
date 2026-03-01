import { motion } from "framer-motion";
import { ThumbsUp, ThumbsDown, Loader2, Check, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useWallet } from "@/context/WalletContext";
import { toast } from "sonner";

interface VoteButtonsProps {
  onVoteTrue: () => void;
  onVoteFalse: () => void;
  trueVotes?: number;
  falseVotes?: number;
  disabled?: boolean;
}

const VoteButtons = ({ onVoteTrue, onVoteFalse, trueVotes = 0, falseVotes = 0, disabled = false }: VoteButtonsProps) => {
  const [voting, setVoting] = useState<"true" | "false" | null>(null);
  const [voted, setVoted] = useState<"true" | "false" | null>(null);
  const { roleInfo } = useWallet();

  const handleVote = async (type: "true" | "false") => {
    if (voted || disabled) return;
    setVoting(type);
    await new Promise((r) => setTimeout(r, 1500));
    type === "true" ? onVoteTrue() : onVoteFalse();
    setVoted(type);
    setVoting(null);
    
    // Role-specific toast
    if (roleInfo.role === 2) {
      toast.success("⭐ VIP Vote Submitted");
    } else {
      toast.success("Vote Submitted");
    }
  };

  const isValidator = roleInfo.role === 2;

  return (
    <div className="flex items-center gap-3">
      <motion.div whileHover={{ scale: voted ? 1 : 1.05 }} whileTap={{ scale: voted ? 1 : 0.92 }}>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleVote("true")}
          disabled={voting !== null || voted !== null || disabled}
          className={`gap-2 rounded-xl transition-all duration-300 ${
            voted === "true"
              ? "bg-success/20 text-success border-success/40"
              : "border-border hover:bg-success/10 hover:text-success hover:border-success/30"
          } ${isValidator ? "ring-1 ring-amber-500/30" : ""}`}
        >
          {isValidator && <Star className="w-3 h-3 fill-amber-400 text-amber-400" />}
          {voting === "true" ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : voted === "true" ? (
            <Check className="w-4 h-4" />
          ) : (
            <ThumbsUp className="w-4 h-4" />
          )}
          <span className="font-mono text-xs">{trueVotes + (voted === "true" ? 1 : 0)}</span>
        </Button>
      </motion.div>

      <motion.div whileHover={{ scale: voted ? 1 : 1.05 }} whileTap={{ scale: voted ? 1 : 0.92 }}>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleVote("false")}
          disabled={voting !== null || voted !== null || disabled}
          className={`gap-2 rounded-xl transition-all duration-300 ${
            voted === "false"
              ? "bg-destructive/20 text-destructive border-destructive/40"
              : "border-border hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30"
          } ${isValidator ? "ring-1 ring-amber-500/30" : ""}`}
        >
          {isValidator && <Star className="w-3 h-3 fill-amber-400 text-amber-400" />}
          {voting === "false" ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : voted === "false" ? (
            <Check className="w-4 h-4" />
          ) : (
            <ThumbsDown className="w-4 h-4" />
          )}
          <span className="font-mono text-xs">{falseVotes + (voted === "false" ? 1 : 0)}</span>
        </Button>
      </motion.div>
    </div>
  );
};

export default VoteButtons;
