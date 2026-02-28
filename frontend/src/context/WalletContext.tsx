import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { BrowserProvider, JsonRpcSigner, Contract } from "ethers";
import { toast } from "sonner";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/utils/constants";

const SEPOLIA_CHAIN_ID = "0xaa36a7"; // 11155111 in hex

// Role enum from contract: 0 = None, 1 = User, 2 = Validator
export type ContractRole = 0 | 1 | 2;

export interface RoleInfo {
  role: ContractRole;
  label: string;
  reputation: number;
}

interface WalletState {
  walletAddress: string | null;
  provider: BrowserProvider | null;
  signer: JsonRpcSigner | null;
  roleInfo: RoleInfo;
  isConnected: boolean;
  connecting: boolean;
  connectWallet: () => Promise<void>;
  disconnect: () => void;
  switchAccount: () => Promise<void>;
  refreshRole: () => Promise<void>;
}

const WalletContext = createContext<WalletState | undefined>(undefined);

function getRoleLabel(role: ContractRole): string {
  switch (role) {
    case 2:
      return "Validator";
    case 1:
      return "User";
    default:
      return "Unregistered";
  }
}

function getRoleInfo(role: ContractRole): RoleInfo {
  return {
    role,
    label: getRoleLabel(role),
    reputation: 0 // Default to 0, will be calculated separately
  };
}

export const WalletProvider = ({ children }: { children: ReactNode }) => {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [provider, setProvider] = useState<BrowserProvider | null>(null);
  const [signer, setSigner] = useState<JsonRpcSigner | null>(null);
  const [roleInfo, setRoleInfo] = useState<RoleInfo>({
    role: 0,
    label: "Unregistered",
    reputation: 0
  });
  const [connecting, setConnecting] = useState(false);

  // STRICT ROLE FETCH - NO FALLBACKS
  const fetchRole = async (address: string, contractInstance: Contract) => {
    console.log("============================================================");
    console.log("🔍 Fetching role from contract...");
    console.log("   Calling getRole for:", address);
    console.log("   Contract address:", CONTRACT_ADDRESS);
    
    try {
      const role = await contractInstance.getRole(address);
      const roleNumber = Number(role) as ContractRole;
      const info = getRoleInfo(roleNumber);
      
      setRoleInfo(info);
      
      console.log("✅ Role from chain:", roleNumber);
      console.log("   Label:", info.label);
      console.log("============================================================");
      
      return roleNumber;
    } catch (error: any) {
      console.error("============================================================");
      console.error("❌ CRITICAL: getRole() CALL_EXCEPTION");
      console.error("   Contract address:", CONTRACT_ADDRESS);
      console.error("   Wallet address:", address);
      console.error("   Error code:", error.code);
      console.error("   Error message:", error.message);
      console.error("============================================================");
      
      // CRITICAL ERROR - DO NOT DEFAULT TO ROLE 0
      toast.error("Contract error: getRole() failed. Wrong contract address or ABI mismatch.");
      throw new Error(`getRole() failed: ${error.message}`);
    }
  };

  const refreshRole = useCallback(async () => {
    if (!walletAddress || !provider) {
      console.warn("⚠️  Cannot refresh role: wallet not connected");
      return;
    }

    try {
      const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
      await fetchRole(walletAddress, contract);
    } catch (error) {
      console.error("Failed to refresh role:", error);
    }
  }, [walletAddress, provider]);

  const switchToSepolia = async () => {
    try {
      const ethereum = (window as any).ethereum;
      await ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: SEPOLIA_CHAIN_ID }],
      });
      return true;
    } catch (error: any) {
      // Chain not added, try to add it
      if (error.code === 4902) {
        try {
          await (window as any).ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
              {
                chainId: SEPOLIA_CHAIN_ID,
                chainName: "Sepolia Testnet",
                nativeCurrency: {
                  name: "Sepolia ETH",
                  symbol: "ETH",
                  decimals: 18,
                },
                rpcUrls: ["https://sepolia.infura.io/v3/"],
                blockExplorerUrls: ["https://sepolia.etherscan.io"],
              },
            ],
          });
          return true;
        } catch (addError) {
          console.error("Failed to add Sepolia network:", addError);
          return false;
        }
      }
      console.error("Failed to switch to Sepolia:", error);
      return false;
    }
  };

  const connectWallet = useCallback(async () => {
    setConnecting(true);
    try {
      const ethereum = (window as any).ethereum;
      
      if (!ethereum) {
        toast.error("MetaMask not installed. Please install MetaMask to continue.");
        throw new Error("MetaMask not installed");
      }

      console.log("🔌 Connecting to MetaMask...");

      // Request accounts
      const accounts = await ethereum.request({ 
        method: "eth_requestAccounts" 
      });

      if (accounts.length === 0) {
        throw new Error("No accounts found");
      }

      console.log("✅ Account connected:", accounts[0]);

      // Create provider and signer
      const browserProvider = new BrowserProvider(ethereum);
      const network = await browserProvider.getNetwork();
      
      console.log("🌐 Network detected:");
      console.log("   Chain ID:", network.chainId.toString());
      console.log("   Name:", network.name);
      
      // ENFORCE SEPOLIA NETWORK - MUST BE 11155111
      if (network.chainId !== BigInt(11155111)) {
        console.warn("⚠️  Wrong network detected, switching to Sepolia...");
        toast.info("Please switch to Sepolia testnet");
        const switched = await switchToSepolia();
        if (!switched) {
          throw new Error("Failed to switch to Sepolia network");
        }
        // Recreate provider after network switch
        const newProvider = new BrowserProvider(ethereum);
        const newNetwork = await newProvider.getNetwork();
        
        // Verify we're on Sepolia now
        if (newNetwork.chainId !== BigInt(11155111)) {
          throw new Error("Still not on Sepolia after switch attempt");
        }
        
        console.log("✅ Switched to Sepolia");
        const newSigner = await newProvider.getSigner();
        const signerAddress = await newSigner.getAddress();
        const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, newProvider);
        
        setProvider(newProvider);
        setSigner(newSigner);
        setWalletAddress(signerAddress);
        
        // Fetch role from contract - STRICT, NO FALLBACK
        await fetchRole(signerAddress, contract);
        
        toast.success("Connected to Sepolia!");
      } else {
        console.log("✅ Already on Sepolia");
        const walletSigner = await browserProvider.getSigner();
        const signerAddress = await walletSigner.getAddress();
        const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, browserProvider);
        
        setProvider(browserProvider);
        setSigner(walletSigner);
        setWalletAddress(signerAddress);
        
        // Fetch role from contract - STRICT, NO FALLBACK
        await fetchRole(signerAddress, contract);
        
        toast.success("Wallet connected!");
      }
    } catch (err: any) {
      console.error("❌ Connection failed:", err);
      toast.error(err.message || "Failed to connect wallet");
      throw err;
    } finally {
      setConnecting(false);
    }
  }, []);

  const switchAccount = useCallback(async () => {
    try {
      const ethereum = (window as any).ethereum;
      if (!ethereum) {
        toast.error("MetaMask not installed");
        return;
      }

      // Request permission to access accounts (triggers account selector)
      await ethereum.request({
        method: "wallet_requestPermissions",
        params: [{ eth_accounts: {} }],
      });

      // Get new account
      const accounts = await ethereum.request({ method: "eth_accounts" });
      if (accounts.length > 0 && provider) {
        const newSigner = await provider.getSigner();
        const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
        
        setSigner(newSigner);
        setWalletAddress(accounts[0]);
        
        // Fetch role for new account - STRICT, NO FALLBACK
        await fetchRole(accounts[0], contract);
        
        toast.success("Account switched!");
      }
    } catch (error: any) {
      console.error("Failed to switch account:", error);
      toast.error("Failed to switch account");
    }
  }, [provider]);

  const disconnect = useCallback(() => {
    setWalletAddress(null);
    setProvider(null);
    setSigner(null);
    setRoleInfo({
      role: 0,
      label: "Unregistered",
      reputation: 0
    });
    toast.info("Wallet disconnected");
  }, []);

  // Listen for account changes
  useEffect(() => {
    const ethereum = (window as any).ethereum;
    if (!ethereum) return;

    const handleAccountsChanged = async (accounts: string[]) => {
      if (accounts.length === 0) {
        // User disconnected
        disconnect();
      } else if (accounts[0] !== walletAddress) {
        // Account changed
        setWalletAddress(accounts[0]);
        
        // Recreate signer with new account
        if (provider) {
          const newSigner = await provider.getSigner();
          const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
          setSigner(newSigner);
          
          // Fetch role for new account - STRICT, NO FALLBACK
          await fetchRole(accounts[0], contract);
        }
        
        toast.info("Account changed");
      }
    };

    const handleChainChanged = (chainId: string) => {
      // Reload page on chain change (recommended by MetaMask)
      window.location.reload();
    };

    ethereum.on("accountsChanged", handleAccountsChanged);
    ethereum.on("chainChanged", handleChainChanged);

    return () => {
      ethereum.removeListener("accountsChanged", handleAccountsChanged);
      ethereum.removeListener("chainChanged", handleChainChanged);
    };
  }, [walletAddress, provider, disconnect]);

  // Check if already connected on mount
  useEffect(() => {
    const checkConnection = async () => {
      const ethereum = (window as any).ethereum;
      if (!ethereum) return;

      try {
        const accounts = await ethereum.request({ method: "eth_accounts" });
        if (accounts.length > 0) {
          const browserProvider = new BrowserProvider(ethereum);
          const network = await browserProvider.getNetwork();
          
          // Verify Sepolia
          if (network.chainId !== BigInt(11155111)) {
            console.warn("⚠️  Not on Sepolia, skipping auto-connect");
            return;
          }
          
          const walletSigner = await browserProvider.getSigner();
          const signerAddress = await walletSigner.getAddress();
          const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, browserProvider);
          
          setProvider(browserProvider);
          setSigner(walletSigner);
          setWalletAddress(signerAddress);
          
          // Fetch role from contract - STRICT, NO FALLBACK
          await fetchRole(signerAddress, contract);
        }
      } catch (error) {
        console.error("Failed to check connection:", error);
      }
    };

    checkConnection();
  }, []);

  return (
    <WalletContext.Provider
      value={{
        walletAddress,
        provider,
        signer,
        roleInfo,
        isConnected: !!walletAddress,
        connecting,
        connectWallet,
        disconnect,
        switchAccount,
        refreshRole,
      }}
    >
      {children}
    </WalletContext.Provider>
  );
};

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) throw new Error("useWallet must be used within WalletProvider");
  return context;
};
