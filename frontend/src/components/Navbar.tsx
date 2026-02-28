import { Link } from "react-router-dom";
import { Wallet, LogOut, Loader2, Star, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useWallet } from "@/context/WalletContext";
import { truncateAddress } from "@/utils/helpers";
import { motion } from "framer-motion";

const Navbar = () => {
  const { walletAddress, roleInfo, isConnected, connecting, connectWallet, disconnect, switchAccount } = useWallet();

  const getRoleStyle = () => {
    switch (roleInfo.role) {
      case 2: // Validator
        return "bg-gradient-to-r from-amber-500/20 to-yellow-500/20 text-amber-400 border-amber-500/40";
      case 1: // User
        return "bg-gradient-to-r from-slate-400/20 to-slate-500/20 text-slate-300 border-slate-400/40";
      default: // None
        return "bg-muted/50 text-muted-foreground border-border";
    }
  };

  const getRoleIcon = () => {
    if (roleInfo.role === 2) {
      return <Star className="w-3 h-3 fill-current" />;
    }
    return null;
  };

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-0 left-0 md:left-16 right-0 h-16 z-40 flex items-center justify-between px-8 backdrop-blur-2xl border-b border-border/50"
      style={{ background: 'hsl(222 47% 7% / 0.8)' }}
    >
      <Link to="/" className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center md:hidden"
          style={{ background: 'linear-gradient(135deg, hsl(239 84% 67%), hsl(187 92% 53%))' }}>
          <span className="text-white font-mono text-xs font-bold">TP</span>
        </div>
        <h1 className="text-lg font-bold tracking-tight">Truth Protocol</h1>
      </Link>

      {isConnected ? (
        <div className="flex items-center gap-3">
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getRoleStyle()}`}
          >
            {getRoleIcon()}
            <span className="text-xs font-semibold">{roleInfo.label}</span>
          </motion.div>
          <motion.span
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="font-mono text-sm text-muted-foreground hidden sm:inline px-3 py-1.5 rounded-lg bg-secondary/50 border border-border"
          >
            {truncateAddress(walletAddress!)}
          </motion.span>
          <Button
            variant="outline"
            size="sm"
            onClick={switchAccount}
            className="border-border bg-secondary/50 hover:bg-primary/15 hover:text-primary hover:border-primary/30 rounded-lg"
            title="Switch Account"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={disconnect}
            className="border-border bg-secondary/50 hover:bg-destructive/15 hover:text-destructive hover:border-destructive/30 rounded-lg"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      ) : (
        <Button onClick={connectWallet} disabled={connecting} className="gap-2 shimmer-button rounded-xl font-semibold text-sm">
          {connecting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Wallet className="w-4 h-4" />
          )}
          Connect Wallet
        </Button>
      )}
    </motion.nav>
  );
};

export default Navbar;
