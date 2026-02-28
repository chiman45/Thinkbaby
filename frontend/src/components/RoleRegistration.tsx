import { motion } from "framer-motion";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, UserPlus, Shield } from "lucide-react";
import { useWallet } from "@/context/WalletContext";
import { Contract } from "ethers";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/utils/constants";
import { toast } from "sonner";

const RoleRegistration = () => {
  const { walletAddress, signer, roleInfo, isConnected, refreshRole } = useWallet();
  const [registering, setRegistering] = useState<"user" | "validator" | null>(null);

  const handleRegisterRole = async (roleType: "user" | "validator") => {
    if (!isConnected || !walletAddress || !signer) {
      toast.error("Please connect your wallet");
      return;
    }

    // STRICT: Only allow registration if role is 0
    if (roleInfo.role !== 0) {
      console.log("⚠️  Registration blocked - already registered");
      console.log("   Current role:", roleInfo.role);
      console.log("   Current label:", roleInfo.label);
      toast.error("Already registered");
      return;
    }

    setRegistering(roleType);
    console.log(`🔄 Registering as ${roleType}...`);
    console.log("   Wallet:", walletAddress);
    console.log("   Contract:", CONTRACT_ADDRESS);
    
    try {
      const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

      toast.info(`Registering as ${roleType}...`);
      
      // Call contract function - NO ARGUMENTS (uses msg.sender)
      const tx = roleType === "user" 
        ? await contract.registerAsUser()
        : await contract.registerAsValidator();

      console.log("📝 Transaction sent:", tx.hash);
      toast.info("Waiting for confirmation...");
      
      const receipt = await tx.wait();
      console.log("✅ Transaction confirmed:", receipt.hash);
      console.log("   Block number:", receipt.blockNumber);

      toast.success(`Successfully registered as ${roleType}!`);
      
      // Refresh role from contract immediately
      console.log("🔄 Refreshing role from contract...");
      await refreshRole();
      
      console.log("✅ Registration complete");
    } catch (error: any) {
      console.error("❌ Registration error:", error);
      console.error("   Error code:", error.code);
      console.error("   Error message:", error.message);
      
      // Handle AlreadyRegistered error
      if (error.message?.includes("AlreadyRegistered") || 
          error.code === "CALL_EXCEPTION" ||
          error.message?.includes("execution reverted")) {
        
        console.log("⚠️  AlreadyRegistered detected - refreshing role from contract");
        toast.error("Already registered");
        
        // Refresh role from contract to sync state
        try {
          await refreshRole();
          console.log("✅ Role refreshed after AlreadyRegistered error");
        } catch (refreshError) {
          console.error("Failed to refresh role:", refreshError);
        }
      } else if (error.code === 4001 || error.code === "ACTION_REJECTED") {
        toast.error("Transaction rejected by user");
      } else {
        toast.error("Registration failed. Please try again.");
      }
    } finally {
      setRegistering(null);
    }
  };

  // STRICT: Only show if connected AND role is exactly 0
  if (!isConnected || roleInfo.role !== 0) {
    console.log("🚫 Registration card hidden");
    console.log("   Connected:", isConnected);
    console.log("   Role:", roleInfo.role);
    return null;
  }

  console.log("✅ Registration card visible - Role:", roleInfo.role);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-8"
    >
      <h3 className="text-lg font-semibold mb-4">Register Your Role</h3>
      <p className="text-sm text-muted-foreground mb-6">
        You need to register a role before you can participate in the protocol.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button
            onClick={() => handleRegisterRole("user")}
            disabled={registering !== null}
            className="w-full gap-2 bg-gradient-to-r from-slate-400/20 to-slate-500/20 hover:from-slate-400/30 hover:to-slate-500/30 border border-slate-400/40 text-slate-300 rounded-xl h-16"
          >
            {registering === "user" ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Registering...</span>
              </>
            ) : (
              <>
                <UserPlus className="w-5 h-5" />
                <span className="font-semibold">Register as User</span>
              </>
            )}
          </Button>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button
            onClick={() => handleRegisterRole("validator")}
            disabled={registering !== null}
            className="w-full gap-2 bg-gradient-to-r from-amber-500/20 to-yellow-500/20 hover:from-amber-500/30 hover:to-yellow-500/30 border border-amber-500/40 text-amber-400 rounded-xl h-16"
          >
            {registering === "validator" ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Registering...</span>
              </>
            ) : (
              <>
                <Shield className="w-5 h-5" />
                <span className="font-semibold">Register as Validator</span>
              </>
            )}
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default RoleRegistration;
