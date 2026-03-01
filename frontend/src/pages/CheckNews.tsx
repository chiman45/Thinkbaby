import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2, Search, Upload, AlertTriangle, CheckCircle } from "lucide-react";
import { useWallet } from "@/context/WalletContext";
import { hashClaim } from "@/utils/hash";
import { api } from "@/services/api";
import { Contract } from "ethers";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/utils/constants";
import { toast } from "sonner";

const CheckNews = () => {
  const [newsText, setNewsText] = useState("");
  const [checking, setChecking] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [claimHash, setClaimHash] = useState<string | null>(null);
  const [exists, setExists] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const { walletAddress, provider, signer, isConnected, roleInfo } = useWallet();
  const navigate = useNavigate();

  const handleCheck = async () => {
    if (!newsText.trim()) {
      toast.error("Please enter some text");
      return;
    }

    setChecking(true);
    try {
      // Compute claim hash
      const hash = hashClaim(newsText);
      setClaimHash(hash);

      // Check if exists on-chain
      if (!provider) {
        toast.error("Please connect your wallet");
        return;
      }

      const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
      const claimExists = await contract.claimExists(hash);
      
      setExists(claimExists);
      
      if (claimExists) {
        toast.success("Claim found on-chain!");
        // Navigate to detail page after a moment
        setTimeout(() => navigate(`/claim/${hash}`), 1500);
      } else {
        toast.info("Claim not registered yet");
      }
    } catch (error: any) {
      console.error("Check error:", error);
      toast.error(error.message || "Failed to check claim");
    } finally {
      setChecking(false);
    }
  };

  const handleRegister = async () => {
    if (!isConnected || !walletAddress || !signer || !provider) {
      toast.error("Please connect your wallet");
      return;
    }

    if (!claimHash) {
      toast.error("Please check the claim first");
      return;
    }

    setRegistering(true);
    try {
      // Step 1: Check role BEFORE attempting registration
      const readContract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
      
      console.log("🔍 Checking role before registration...");
      const roleRaw = await readContract.getRole(walletAddress);
      const role = Number(roleRaw);
      
      console.log("   Role:", role);
      
      // Role validation
      if (role === 0) {
        toast.error("Please register as a User before submitting claims.");
        setRegistering(false);
        return;
      }
      
      if (role === 2) {
        toast.error("Validators cannot register claims.");
        setRegistering(false);
        return;
      }
      
      // Only Users (role === 1) can proceed
      if (role !== 1) {
        toast.error("Invalid role for claim registration.");
        setRegistering(false);
        return;
      }
      
      console.log("✅ Role check passed - User can register claims");
      
      // Step 2: Check if claim already exists
      console.log("🔍 Checking if claim already exists...");
      const alreadyExists = await readContract.claimExists(claimHash);
      
      if (alreadyExists) {
        toast.error("Claim already exists on-chain.");
        setRegistering(false);
        return;
      }
      
      console.log("✅ Claim does not exist - proceeding with registration");

      // Step 3: Backend-orchestrated registration
      toast.info("Registering claim via backend...");
      console.log("============================================================");
      console.log("📤 FRONTEND: Sending registration request to backend");
      console.log("============================================================");
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/claims/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          newsContent: newsText,
          submitterAddress: walletAddress
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();
      
      console.log("✅ FRONTEND: Registration complete");
      console.log("📥 Using claimHash from backend:", data.claimHash);
      console.log("   Block:", data.blockNumber);
      console.log("   CID:", data.contentCID);
      console.log("   Already existed:", data.alreadyExists);
      console.log("============================================================");
      
      toast.success("Claim registered successfully!");
      
      // Navigate to claim detail page using hash from backend
      console.log("🔀 Redirecting to:", `/claim/${data.claimHash}`);
      setTimeout(() => navigate(`/claim/${data.claimHash}`), 1500);
    } catch (error: any) {
      console.error("❌ Registration error:", error);
      toast.error(error.message || "Registration failed");
    } finally {
      setRegistering(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen pt-24 pb-16 px-4 md:pl-24 md:pr-8"
    >
      <div className="max-w-[1200px] mx-auto space-y-8">
        <div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-3">Check News</h1>
          <p className="text-base text-muted-foreground leading-relaxed max-w-lg">
            Paste a news article or claim to verify if it exists on-chain or register it.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Input */}
          <div className="space-y-6">
            <div className={`glass-card p-8 transition-all duration-500 ${checking ? "scan-animation" : ""} ${isFocused ? "glow-input" : ""}`}>
              <Textarea
                placeholder="Paste news text or a claim here to verify..."
                value={newsText}
                onChange={(e) => setNewsText(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                className="min-h-[200px] bg-secondary/50 border-border text-base resize-none focus:border-primary/50 rounded-xl transition-all duration-300"
              />
              <div className="mt-4">
                <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
                  <Button
                    onClick={handleCheck}
                    disabled={checking || !newsText.trim()}
                    className="w-full gap-2 shimmer-button rounded-xl h-12 text-sm font-semibold tracking-wide"
                  >
                    {checking ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Checking blockchain...</span>
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4" />
                        Check Claim
                      </>
                    )}
                  </Button>
                </motion.div>
              </div>
            </div>

            {/* Registration Action */}
            <AnimatePresence>
              {claimHash && !exists && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="glass-card p-8"
                >
                  <div className="text-center space-y-4">
                    <p className="text-base text-muted-foreground leading-relaxed">
                      This claim hasn't been registered on-chain yet.
                    </p>
                    
                    {/* Role-based messaging */}
                    {isConnected && roleInfo.role === 0 && (
                      <p className="text-sm text-warning">
                        ⚠️ Register as User first to submit claims
                      </p>
                    )}
                    {isConnected && roleInfo.role === 2 && (
                      <p className="text-sm text-warning">
                        ⚠️ Validators cannot submit claims
                      </p>
                    )}
                    
                    <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
                      <Button
                        onClick={handleRegister}
                        disabled={registering || !isConnected || roleInfo.role !== 1}
                        className="shimmer-button gap-2 rounded-xl h-12"
                      >
                        {registering ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Registering...</span>
                          </>
                        ) : (
                          <>
                            <Upload className="w-4 h-4" />
                            Register Claim on Sepolia
                          </>
                        )}
                      </Button>
                    </motion.div>
                    {!isConnected && (
                      <p className="text-xs text-muted-foreground">
                        Connect your wallet to register
                      </p>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right: Status */}
          <div className="space-y-6">
            <AnimatePresence>
              {claimHash ? (
                <motion.div
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 30 }}
                  transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                  className="space-y-6"
                >
                  <div className="glass-card p-8">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                      Claim Hash
                    </h3>
                    <p className="text-xs font-mono break-all mb-6">{claimHash}</p>
                    
                    {exists ? (
                      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold text-success bg-success/10 border border-success/30">
                        <CheckCircle className="w-3 h-3" />
                        Registered On-Chain
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold text-warning bg-warning/10 border border-warning/30">
                        <AlertTriangle className="w-3 h-3" />
                        Not Registered
                      </div>
                    )}
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
                    <Search className="w-8 h-8 text-primary/40" />
                  </div>
                  <h3 className="text-lg font-semibold text-muted-foreground mb-2">No Check Yet</h3>
                  <p className="text-sm text-muted-foreground/70 max-w-xs">
                    Paste a claim on the left and click Check to verify its status
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

export default CheckNews;
