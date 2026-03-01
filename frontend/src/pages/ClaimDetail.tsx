import { motion, AnimatePresence } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/services/api";
import { useWallet } from "@/context/WalletContext";
import { Button } from "@/components/ui/button";
import { Loader2, ArrowLeft, Brain, AlertCircle, FileCheck, Link2 } from "lucide-react";
import TruthMatrix from "@/components/TruthMatrix";
import VoteButtons from "@/components/VoteButtons";
import { Contract } from "ethers";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/utils/constants";
import { toast } from "sonner";

const ClaimDetail = () => {
  const { claimHash } = useParams<{ claimHash: string }>();
  const navigate = useNavigate();
  const { walletAddress, signer, roleInfo, isConnected } = useWallet();
  const [analyzed, setAnalyzed] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);

  const { data: claimData, isLoading, error, refetch } = useQuery({
    queryKey: ['claim-detail', claimHash],
    queryFn: () => api.getClaimDetail(claimHash!, walletAddress || undefined),
    enabled: !!claimHash,
  });

  const analyzeMutation = useMutation({
    mutationFn: () => api.analyzeClaim(claimHash!, walletAddress || undefined),
    onSuccess: (data) => {
      setAnalysisData(data);
      setAnalyzed(true);
      toast.success("Analysis complete!");
    },
    onError: (error: Error) => {
      toast.error(`Analysis failed: ${error.message}`);
    },
  });

  const handleVote = async (voteType: 'true' | 'false') => {
    if (!isConnected || !walletAddress || !signer) {
      toast.error("Please connect your wallet");
      return;
    }

    try {
      const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);
      
      console.log("\n" + "=".repeat(60));
      console.log("🗳️  VOTING PROCESS STARTED");
      console.log("=".repeat(60));
      console.log(`📋 Claim Hash: ${claimHash}`);
      console.log(`👤 Voter Address: ${walletAddress}`);
      console.log(`✅ Vote Type: ${voteType}`);
      
      // Step 1: Fetch role FRESH from chain (don't trust cache)
      console.log("\n🔍 Step 1: Fetching role from blockchain...");
      const roleFromChain = await contract.getRole(walletAddress);
      const role = Number(roleFromChain);
      
      console.log(`🔥 REAL ROLE FROM CHAIN: ${role}`);
      console.log(`   0 = None, 1 = User, 2 = Validator`);
      
      if (role === 0) {
        console.log("❌ Role is 0 (None) - not registered");
        toast.error("Please register as User or Validator before voting.");
        return;
      }
      
      console.log(`✅ Role check passed - Role ${role} can vote`);
      
      // Step 2: Check if submitter (cannot vote on own claim)
      console.log("\n🔍 Step 2: Checking if voter is submitter...");
      const submitter = await contract.getClaimSubmitter(claimHash);
      console.log(`   Submitter (raw):      ${submitter}`);
      console.log(`   Voter (raw):          ${walletAddress}`);
      console.log(`   Submitter (lower):    ${submitter.toLowerCase()}`);
      console.log(`   Voter (lower):        ${walletAddress.toLowerCase()}`);
      
      // Defensive check with normalized addresses
      if (submitter.toLowerCase() === walletAddress.toLowerCase()) {
        console.log("🚫 SUBMITTER CANNOT VOTE - Blocking transaction");
        toast.error("You cannot vote on your own claim.");
        return;
      }
      
      console.log("✅ Voter is NOT submitter - can proceed");
      
      // Step 3: Verify claim exists on-chain
      console.log("\n🔍 Step 3: Verifying claim exists on-chain...");
      const claimExists = await contract.claimExists(claimHash);
      console.log(`   Claim exists: ${claimExists}`);
      
      if (!claimExists) {
        console.log("❌ Claim does not exist on-chain");
        toast.error("Claim not found on blockchain.");
        return;
      }
      
      console.log("✅ Claim exists - can proceed");
      
      // Step 4: Check if already voted
      console.log("\n🔍 Step 4: Checking if already voted...");
      const hasVoted = await contract.hasAddressVoted(claimHash, walletAddress);
      console.log(`   Has voted: ${hasVoted}`);
      
      if (hasVoted) {
        console.log("❌ Already voted on this claim");
        toast.error("You have already voted on this claim.");
        return;
      }
      
      console.log("✅ Has not voted yet - can proceed");

      // Step 5: Select correct vote function based on FRESH on-chain role
      console.log("\n📝 Step 5: Submitting vote transaction...");
      console.log(`   Role: ${role}`);
      console.log(`   Vote: ${voteType}`);
      
      toast.info("Submitting vote transaction...");
      
      let tx;
      let functionName;
      
      if (role === 1) {
        // User voting
        functionName = voteType === 'true' ? 'voteTrue()' : 'voteFalse()';
        console.log(`   Using User function: ${functionName}`);
        tx = voteType === 'true' 
          ? await contract.voteTrue(claimHash)
          : await contract.voteFalse(claimHash);
      } else if (role === 2) {
        // Validator voting
        functionName = voteType === 'true' ? 'voteTrueValid()' : 'voteFalseValid()';
        console.log(`   Using Validator function: ${functionName}`);
        tx = voteType === 'true' 
          ? await contract.voteTrueValid(claimHash)
          : await contract.voteFalseValid(claimHash);
      } else {
        console.log(`❌ Invalid role: ${role}`);
        toast.error("Invalid role for voting.");
        return;
      }

      console.log(`✅ Transaction sent: ${tx.hash}`);
      console.log(`   Function called: ${functionName}`);
      
      toast.info("Waiting for confirmation...");
      const receipt = await tx.wait();

      console.log("✅ Vote confirmed!");
      console.log(`   Block: ${receipt.blockNumber}`);
      console.log(`   Gas used: ${receipt.gasUsed.toString()}`);
      console.log("=".repeat(60) + "\n");
      
      toast.success("Vote recorded on-chain!");
      
      // Refetch claim data to update vote counts
      setTimeout(() => refetch(), 2000);
    } catch (error: any) {
      console.error("\n" + "=".repeat(60));
      console.error("❌ VOTE ERROR");
      console.error("=".repeat(60));
      console.error("Error:", error);
      console.error("Error message:", error.message);
      console.error("Error code:", error.code);
      if (error.data) {
        console.error("Error data:", error.data);
      }
      console.error("=".repeat(60) + "\n");
      
      toast.error(error.message || "Vote failed");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen pt-24 pb-16 px-4 md:pl-24 md:pr-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !claimData) {
    return (
      <div className="min-h-screen pt-24 pb-16 px-4 md:pl-24 md:pr-8">
        <div className="max-w-[1200px] mx-auto">
          <Button variant="ghost" onClick={() => navigate('/feed')} className="mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Feed
          </Button>
          <div className="glass-card p-8">
            <div className="flex items-center gap-4 text-destructive mb-4">
              <AlertCircle className="w-5 h-5" />
              <div>
                <p className="font-semibold">Failed to load claim</p>
                <p className="text-sm text-muted-foreground">{error?.message || "Claim not found"}</p>
              </div>
            </div>
            <div className="mt-6 p-4 bg-muted/50 rounded-lg border border-border">
              <p className="text-sm text-muted-foreground">
                This claim may not be indexed by the backend yet. Possible reasons:
              </p>
              <ul className="mt-2 text-sm text-muted-foreground list-disc list-inside space-y-1">
                <li>Claim was just registered (wait for indexing)</li>
                <li>Content was not uploaded to IPFS</li>
                <li>Backend is out of sync with blockchain</li>
              </ul>
              <p className="mt-4 text-sm text-warning">
                ⚠️ Cannot vote on claims that are not indexed by backend.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const displayData = analyzed && analysisData ? analysisData : claimData;
  const totalVotes = displayData.userTrueVotes + displayData.userFalseVotes;
  
  // Check if current user is the submitter (normalized address comparison)
  const isSubmitter = 
    walletAddress && 
    displayData.claimSubmitter && 
    walletAddress.toLowerCase() === displayData.claimSubmitter.toLowerCase();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen pt-24 pb-16 px-4 md:pl-24 md:pr-8"
    >
      <div className="max-w-[1200px] mx-auto space-y-8">
        <Button variant="ghost" onClick={() => navigate('/feed')} className="mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Feed
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Claim Content */}
          <div className="space-y-6">
            <div className="glass-card p-8">
              <div className="flex items-center gap-2 mb-4">
                <FileCheck className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  Claim Content
                </h3>
              </div>
              <p className="text-base leading-relaxed mb-6">{displayData.newsContent}</p>
              
              <div className="space-y-2 text-xs text-muted-foreground">
                <p className="font-mono">Hash: {displayData.claimHash}</p>
                <p className="font-mono">CID: {displayData.contentCID}</p>
                <p>Submitter: {displayData.claimSubmitter.slice(0, 10)}...</p>
                <p>Block: {displayData.blockNumber}</p>
              </div>
            </div>

            {/* Vote Section */}
            <div className="glass-card p-8">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                Cast Your Vote
              </h3>
              
              {isSubmitter && (
                <div className="mb-4 p-3 bg-warning/10 border border-warning/30 rounded-lg">
                  <p className="text-sm text-warning">
                    🚫 You cannot vote on your own claim
                  </p>
                </div>
              )}
              
              <VoteButtons
                onVoteTrue={() => handleVote('true')}
                onVoteFalse={() => handleVote('false')}
                trueVotes={displayData.userTrueVotes}
                falseVotes={displayData.userFalseVotes}
                disabled={isSubmitter || displayData.hasVoted}
              />
              <div className="mt-4 text-xs text-muted-foreground">
                <p>Total votes: {totalVotes}</p>
                {displayData.hasVoted && <p className="text-accent">You have already voted</p>}
                {isSubmitter && <p className="text-warning">You are the submitter of this claim</p>}
              </div>
            </div>

            {/* Analyze Button */}
            {!analyzed && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-8"
              >
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                  AI Analysis
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Run AI analysis to get risk assessment and generate snapshot
                </p>
                <Button
                  onClick={() => analyzeMutation.mutate()}
                  disabled={analyzeMutation.isPending}
                  className="w-full gap-2 shimmer-button rounded-xl h-12"
                >
                  {analyzeMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4" />
                      Analyze Claim
                    </>
                  )}
                </Button>
              </motion.div>
            )}
          </div>

          {/* Right: Analysis Results */}
          <div className="space-y-6">
            <AnimatePresence>
              {analyzed && analysisData ? (
                <motion.div
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 30 }}
                  className="space-y-6"
                >
                  <TruthMatrix
                    aiRiskScore={analysisData.aiOutput.risk_score * 100}
                    onChainTrue={analysisData.userTrueVotes}
                    onChainFalse={analysisData.userFalseVotes}
                    explanation={analysisData.aiOutput.summary}
                  />

                  <div className="glass-card p-8">
                    <div className="flex items-center gap-2 mb-4">
                      <Link2 className="w-4 h-4 text-accent" />
                      <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                        Snapshot Data
                      </h3>
                    </div>
                    <div className="space-y-2 text-xs font-mono">
                      <p className="text-muted-foreground break-all">
                        Hash: <span className="text-foreground">{analysisData.snapshotHash}</span>
                      </p>
                      {analysisData.snapshotCID && (
                        <p className="text-muted-foreground break-all">
                          CID: <span className="text-foreground">{analysisData.snapshotCID}</span>
                        </p>
                      )}
                      <p className="text-muted-foreground">
                        AI Label: <span className="text-foreground">{analysisData.aiOutput.ai_label}</span>
                      </p>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass-card p-8 flex flex-col items-center justify-center min-h-[300px] text-center"
                >
                  <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
                    style={{ background: 'hsl(239 84% 67% / 0.1)' }}>
                    <Brain className="w-8 h-8 text-primary/40" />
                  </div>
                  <h3 className="text-lg font-semibold text-muted-foreground mb-2">No Analysis Yet</h3>
                  <p className="text-sm text-muted-foreground/70 max-w-xs">
                    Click "Analyze Claim" to run AI analysis and generate snapshot
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ClaimDetail;
