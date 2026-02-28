import { motion } from "framer-motion";
import { Bot, Link2 } from "lucide-react";
import { useEffect, useState } from "react";

interface TruthMatrixProps {
  aiRiskScore: number;
  onChainTrue: number;
  onChainFalse: number;
  explanation: string;
}

const CircularProgress = ({ value, label }: { value: number; label: string }) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedValue / 100) * circumference;

  const color = value >= 70 ? 'hsl(0 84% 60%)' : value >= 40 ? 'hsl(38 92% 50%)' : 'hsl(160 84% 39%)';

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 300);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={radius} fill="none" className="stroke-secondary" strokeWidth="5" />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke={color}
            className="transition-all duration-1000 ease-out"
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ filter: `drop-shadow(0 0 6px ${color})` }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-mono text-2xl font-bold">{animatedValue}%</span>
        </div>
      </div>
      <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{label}</span>
    </div>
  );
};

const TruthMatrix = ({ aiRiskScore, onChainTrue, onChainFalse, explanation }: TruthMatrixProps) => {
  const total = onChainTrue + onChainFalse;
  const truePercent = total > 0 ? Math.round((onChainTrue / total) * 100) : 50;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8 space-y-8"
    >
      <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">The Truth Matrix</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* AI Side */}
        <div className="flex flex-col items-center gap-4 p-8 rounded-2xl bg-secondary/50 border border-border">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Bot className="w-4 h-4 text-primary" />
            <span className="font-semibold">AI Analysis</span>
          </div>
          <CircularProgress value={aiRiskScore} label="Risk Score" />
        </div>

        {/* Blockchain Side */}
        <div className="flex flex-col items-center gap-4 p-8 rounded-2xl bg-secondary/50 border border-border">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Link2 className="w-4 h-4 text-accent" />
            <span className="font-semibold">On-Chain Consensus</span>
          </div>
          <div className="w-full space-y-4 mt-4">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-success">True {truePercent}%</span>
              <span className="text-destructive">False {100 - truePercent}%</span>
            </div>
            <div className="h-3 w-full rounded-full bg-muted overflow-hidden flex">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${truePercent}%` }}
                transition={{ duration: 1, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="h-full rounded-l-full"
                style={{ background: 'hsl(160 84% 39%)' }}
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${100 - truePercent}%` }}
                transition={{ duration: 1, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="h-full bg-destructive rounded-r-full"
              />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{onChainTrue} votes</span>
              <span>{onChainFalse} votes</span>
            </div>
          </div>
        </div>
      </div>

      {explanation && (
        <div className="p-4 rounded-xl bg-secondary/50 border border-border">
          <p className="text-sm text-muted-foreground italic leading-relaxed">
            {explanation}
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default TruthMatrix;
