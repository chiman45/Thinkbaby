import { motion } from "framer-motion";
import { Search, Newspaper, Shield, Users, ShieldCheck, Brain, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { useWallet } from "@/context/WalletContext";
import ReputationCard from "@/components/ReputationCard";
import RoleRegistration from "@/components/RoleRegistration";
import { useState, useEffect, useMemo } from "react";

const RollingNumber = ({ target, suffix = "" }: {target: number;suffix?: string;}) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    const stepTime = duration / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [target]);

  return (
    <span className="font-mono text-3xl font-bold text-primary tabular-nums">
      {count.toLocaleString()}{suffix}
    </span>);

};

const FloatingParticles = () => {
  const particles = useMemo(() =>
  Array.from({ length: 30 }, (_, i) => ({
    id: i,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    size: Math.random() * 4 + 1,
    duration: Math.random() * 10 + 8,
    delay: Math.random() * 5,
    driftX: (Math.random() - 0.5) * 200,
    driftY: (Math.random() - 0.5) * 200 - 100,
    isPrimary: Math.random() > 0.5
  })), []
  );

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) =>
      <div
        key={p.id}
        className="floating-particle"
        style={{
          left: p.left,
          top: p.top,
          width: p.size,
          height: p.size,
          background: p.isPrimary ?
          `hsl(239 84% 67% / ${0.2 + Math.random() * 0.3})` :
          `hsl(187 92% 53% / ${0.15 + Math.random() * 0.25})`,
          '--duration': `${p.duration}s`,
          '--delay': `${p.delay}s`,
          '--drift-x': `${p.driftX}px`,
          '--drift-y': `${p.driftY}px`
        } as React.CSSProperties} />

      )}
    </div>);

};

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 }
};

const Index = () => {
  const { isConnected, connectWallet, connecting } = useWallet();

  const fullText = "DECENTRALIZED\n TRUTH\nPowered by AI + Blockchain";
  const [displayedText, setDisplayedText] = useState("");
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText(fullText.slice(0, i + 1));
      i++;
      if (i >= fullText.length) {
        clearInterval(interval);
        setTimeout(() => setShowCursor(false), 1500);
      }
    }, 45);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen pt-24 pb-16 px-4 md:pl-24 md:pr-8 relative">

      {/* Animated gradient background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] rounded-full opacity-[0.04]"
        style={{ background: 'radial-gradient(circle, hsl(239 84% 67%), transparent 70%)' }} />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full opacity-[0.03]"
        style={{ background: 'radial-gradient(circle, hsl(187 92% 53%), transparent 70%)' }} />
      </div>

      <FloatingParticles />

      <div className="max-w-[1200px] mx-auto relative z-10">
        {/* Hero */}
        <div className="max-w-3xl mx-auto text-center mb-16 pt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border text-xs font-medium mb-10"
            style={{
              background: 'hsl(239 84% 67% / 0.08)',
              borderColor: 'hsl(239 84% 67% / 0.2)',
              color: 'hsl(239 84% 80%)'
            }}>

            <Shield className="w-3.5 h-3.5" />
            Decentralized Verification Protocol
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mb-8 whitespace-pre-line text-center flex flex-col items-center">

            {displayedText.split("\n").map((line, idx) =>
            <span key={idx}>
                {idx <= 1 ?
              <span className="block text-5xl sm:text-6xl font-extrabold leading-[1.1] uppercase font-heading whitespace-nowrap md:text-8xl">
                    {line}
                  </span> :

              <span className="block text-xl md:text-2xl font-medium leading-[1.4] bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent tracking-wide">
                    {line}
                  </span>
              }
              </span>
            )}
            {showCursor &&
            <span className="inline-block w-[3px] h-[0.85em] bg-primary ml-1 animate-pulse align-baseline" />
            }
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-base md:text-lg text-muted-foreground max-w-xl mx-auto mb-12 leading-relaxed">

            Verify news with AI analysis and on-chain consensus. Your vote shapes the truth.
          </motion.p>

          {!isConnected &&
          <>
              <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">

                <motion.button
                whileHover={{ scale: 1.03, boxShadow: '0 0 40px -5px hsl(239 84% 67% / 0.5)' }}
                whileTap={{ scale: 0.97 }}
                onClick={connectWallet}
                disabled={connecting}
                className="shimmer-button px-8 py-3.5 rounded-xl text-primary-foreground font-semibold text-sm tracking-wide">

                  Connect Wallet
                </motion.button>

                <Link to="/feed">
                  <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="btn-outline-cyan flex items-center gap-2">

                    Explore Claims
                    <ArrowRight className="w-4 h-4" />
                  </motion.button>
                </Link>
              </motion.div>

              {/* Rolling Stats */}
              <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="grid grid-cols-3 gap-8 max-w-lg mx-auto">

                {[
              { icon: Users, label: "Users", value: 2000 },
              { icon: ShieldCheck, label: "Validators", value: 100 },
              { icon: Brain, label: "Models", value: 10, suffix: "+" }].
              map((stat, i) =>
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + i * 0.12 }}
                className="flex flex-col items-center gap-3 p-6 rounded-2xl glass-card">

                    <stat.icon className="w-5 h-5 text-accent/60" />
                    <RollingNumber target={stat.value} suffix={stat.suffix || ""} />
                    <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
                      {stat.label}
                    </span>
                  </motion.div>
              )}
              </motion.div>
            </>
          }
        </div>

        {/* Connected State */}
        {isConnected &&
        <div className="space-y-8">
            {/* Role Registration (if not registered) */}
            <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="max-w-2xl mx-auto">

              <RoleRegistration />
            </motion.div>

            <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="max-w-sm mx-auto">

              <ReputationCard />
            </motion.div>

            {/* Action Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <Link to="/check">
                <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                className="glass-card-hover p-8 cursor-pointer group h-full">

                  <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300"
                style={{ background: 'hsl(239 84% 67% / 0.1)' }}>
                    <Search className="w-7 h-7 text-primary group-hover:text-accent transition-colors duration-300" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground mb-3">Check News</h3>
                  <p className="text-base text-muted-foreground leading-relaxed">
                    Paste any news article and get AI-powered risk analysis with on-chain verification.
                  </p>
                </motion.div>
              </Link>

              <Link to="/feed">
                <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                whileHover={{ scale: 1.02, y: -4 }}
                whileTap={{ scale: 0.98 }}
                className="glass-card-hover p-8 cursor-pointer group h-full">

                  <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300"
                style={{ background: 'hsl(187 92% 53% / 0.1)' }}>
                    <Newspaper className="w-7 h-7 text-accent group-hover:text-primary transition-colors duration-300" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground mb-3">Explore Claims</h3>
                  <p className="text-base text-muted-foreground leading-relaxed">
                    Browse the decentralized ledger of verified claims and cast your votes.
                  </p>
                </motion.div>
              </Link>
            </div>

            {/* Stats */}
            <div className="gradient-divider my-8" />
            <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">

              {[
            { label: "Claims Verified", value: "12,847" },
            { label: "Active Validators", value: "3,291" },
            { label: "Consensus Rate", value: "94.2%" }].
            map((stat) =>
            <div key={stat.label} className="text-center p-6 rounded-2xl glass-card">
                  <p className="font-mono text-xl font-bold text-foreground">{stat.value}</p>
                  <p className="text-xs text-muted-foreground font-medium mt-2">{stat.label}</p>
                </div>
            )}
            </motion.div>
          </div>
        }
      </div>
    </motion.div>);

};

export default Index;