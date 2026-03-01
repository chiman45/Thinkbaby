import { motion } from "framer-motion";
import { Bot, Link2 } from "lucide-react";
import { useEffect, useState } from "react";

interface TruthMatrixProps {
  aiRiskScore: number;
  onChainTrue: number;
  onChainFalse: number;
  explanation: string;
  confidence?: number;
  flags?: string[];
}

const CircularProgress = ({ value, label, size = 'large' }: { value: number; label: string; size?: 'large' | 'mini' }) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  
  // Size configurations
  const isLarge = size === 'large';
  const radius = isLarge ? 45 : 28;
  const strokeWidth = isLarge ? 6 : 4;
  const containerSize = isLarge ? 'w-40 h-40' : 'w-20 h-20';
  const fontSize = isLarge ? 'text-[42px]' : 'text-base';
  const labelSize = isLarge ? 'text-xs' : 'text-[10px]';
  
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedValue / 100) * circumference;

  const color = value >= 70 ? 'hsl(0 84% 60%)' : value >= 40 ? 'hsl(38 92% 50%)' : 'hsl(160 84% 39%)';
  const glowColor = value >= 70 ? 'rgba(239, 68, 68, 0.15)' : value >= 40 ? 'rgba(251, 146, 60, 0.15)' : 'rgba(0, 255, 179, 0.15)';

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), isLarge ? 300 : 400);
    return () => clearTimeout(timer);
  }, [value, isLarge]);

  // Format to 1 decimal place for large, 0 decimals for mini
  const displayValue = isLarge 
    ? (Math.round(animatedValue * 10) / 10).toFixed(1)
    : Math.round(animatedValue).toString();

  return (
    <div className="flex flex-col items-center gap-2">
      <div 
        className={`relative ${containerSize} transition-all duration-300 ease-out`}
        style={{
          filter: `drop-shadow(0 0 ${isLarge ? '40px' : '20px'} ${glowColor})`
        }}
      >
        <svg 
          className="w-full h-full -rotate-90" 
          viewBox="0 0 100 100"
          style={isLarge ? {
            animation: 'pulse-rotate 8s ease-in-out infinite'
          } : undefined}
        >
          <defs>
            <linearGradient id={`gradient-${label}-${size}`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={value >= 70 ? '#ef4444' : value >= 40 ? '#fb923c' : '#00ffb3'} />
              <stop offset="100%" stopColor={value >= 70 ? '#dc2626' : value >= 40 ? '#f97316' : '#3b82f6'} />
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r={radius} fill="none" className="stroke-secondary/30" strokeWidth={strokeWidth} />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke={`url(#gradient-${label}-${size})`}
            className="transition-all ease-out"
            style={{
              transitionDuration: '600ms',
              strokeLinecap: 'round',
              strokeDasharray: circumference,
              strokeDashoffset: strokeDashoffset
            }}
            strokeWidth={strokeWidth}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-mono ${fontSize} font-bold tracking-tight leading-none`}>{displayValue}%</span>
        </div>
      </div>
      <span className={`${labelSize} font-semibold text-muted-foreground/60 uppercase tracking-widest`}>{label}</span>
      {isLarge && (
        <style>{`
          @keyframes pulse-rotate {
            0%, 100% { transform: rotate(-90deg) scale(1); }
            50% { transform: rotate(-90deg) scale(1.02); }
          }
        `}</style>
      )}
    </div>
  );
};

// Helper to parse explanation text
const parseExplanation = (explanation: string) => {
  // Extract credibility and confidence from explanation
  const credibilityMatch = explanation.match(/Credibility Score:\s*(\d+)%/);
  const confidenceMatch = explanation.match(/Confidence:\s*(\d+)%/);
  const strongestFactorMatch = explanation.match(/Strongest factor:\s*([^|]+)/);
  const signalsMatch = explanation.match(/Signals:\s*(.+?)(?:\||$)/);
  
  const credibility = credibilityMatch ? parseInt(credibilityMatch[1]) : null;
  const confidence = confidenceMatch ? parseInt(confidenceMatch[1]) : null;
  const strongestFactor = strongestFactorMatch ? strongestFactorMatch[1].trim() : null;
  const signalsText = signalsMatch ? signalsMatch[1].trim() : null;
  
  // Parse signals into array
  const signals = signalsText 
    ? signalsText.split(',').map(s => s.trim()).filter(s => s.length > 0)
    : [];
  
  // Get the main verdict line (first part before |)
  const verdictLine = explanation.split('|')[0].trim();
  
  return {
    credibility,
    confidence,
    strongestFactor,
    signals,
    verdictLine
  };
};

const TruthMatrix = ({ aiRiskScore, onChainTrue, onChainFalse, explanation, confidence: propConfidence, flags }: TruthMatrixProps) => {
  const total = onChainTrue + onChainFalse;
  const truePercent = total > 0 ? Math.round((onChainTrue / total) * 100) : 50;
  
  // Parse explanation to extract structured data
  const parsed = parseExplanation(explanation);
  
  // Use prop confidence if available, otherwise use parsed
  const credibilityScore = parsed.credibility || (100 - aiRiskScore);
  const confidenceScore = propConfidence ? Math.round(propConfidence * 100) : (parsed.confidence || 50);
  const signals = flags || parsed.signals;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8 space-y-8"
    >
      <h3 className="text-sm font-bold uppercase tracking-wider text-foreground/80">The Truth Matrix</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* AI Side */}
        <motion.div 
          className="flex flex-col items-center gap-6 p-8 rounded-2xl border border-border transition-all duration-300 ease-out hover:transform hover:-translate-y-1.5 cursor-default"
          style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)'
          }}
          whileHover={{
            boxShadow: '0 0 50px rgba(99, 102, 241, 0.1)'
          }}
        >
          <div className="flex items-center gap-2 text-sm text-muted-foreground/80">
            <Bot className="w-4 h-4 text-primary" />
            <span className="font-semibold">AI Analysis</span>
          </div>
          
          {/* Main Risk Score */}
          <CircularProgress value={aiRiskScore} label="Risk Score" size="large" />
          
          {/* Mini Meters for Credibility & Confidence */}
          <div className="flex gap-6 mt-2">
            <CircularProgress value={credibilityScore} label="Credibility" size="mini" />
            <CircularProgress value={confidenceScore} label="Confidence" size="mini" />
          </div>
        </motion.div>

        {/* Blockchain Side */}
        <motion.div 
          className="flex flex-col items-center gap-4 p-8 rounded-2xl border border-border transition-all duration-300 ease-out hover:transform hover:-translate-y-1 cursor-default"
          style={{
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)'
          }}
          whileHover={{
            boxShadow: '0 0 50px rgba(6, 182, 212, 0.1)'
          }}
        >
          <div className="flex items-center gap-2 text-sm text-muted-foreground/80">
            <Link2 className="w-4 h-4 text-accent" />
            <span className="font-semibold">On-Chain Consensus</span>
          </div>
          <div className="w-full space-y-4 mt-4">
            <div className="flex justify-between text-xs font-bold">
              <span 
                className="transition-all duration-300"
                style={{
                  background: 'linear-gradient(135deg, #00ffb3, #10b981)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}
              >
                True {truePercent}%
              </span>
              <span 
                className="transition-all duration-300"
                style={{
                  background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}
              >
                False {100 - truePercent}%
              </span>
            </div>
            <div className="h-4 w-full rounded-full bg-secondary/30 overflow-hidden flex shadow-inner">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${truePercent}%` }}
                transition={{ duration: 0.4, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="h-full rounded-l-full"
                style={{ 
                  background: 'linear-gradient(90deg, #00ffb3, #10b981)',
                  boxShadow: '0 0 20px rgba(0, 255, 179, 0.3)'
                }}
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${100 - truePercent}%` }}
                transition={{ duration: 0.4, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="h-full rounded-r-full"
                style={{ 
                  background: 'linear-gradient(90deg, #ef4444, #dc2626)',
                  boxShadow: '0 0 20px rgba(239, 68, 68, 0.3)'
                }}
              />
            </div>
            <div className="flex justify-between text-sm font-bold text-muted-foreground">
              <span>{onChainTrue} votes</span>
              <span>{onChainFalse} votes</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Enhanced Explanation Section */}
      {explanation && (
        <motion.div 
          className="p-6 rounded-xl border border-border/50 transition-all duration-300 ease-out hover:border-border"
          style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.03) 0%, rgba(139, 92, 246, 0.03) 100%)'
          }}
        >
          <div className="space-y-4">
            {/* Verdict Line */}
            <p className="text-[15px] font-medium text-foreground/90 leading-relaxed">
              {parsed.verdictLine}
            </p>
            
            {/* Strongest Factor */}
            {parsed.strongestFactor && (
              <div className="pt-2 border-t border-border/30">
                <p className="text-sm text-muted-foreground/80 leading-relaxed">
                  <span className="font-semibold text-foreground/70">Strongest Factor:</span> {parsed.strongestFactor}
                </p>
              </div>
            )}
            
            {/* Signals */}
            {signals && signals.length > 0 && (
              <div className="pt-2 border-t border-border/30">
                <p className="text-sm font-semibold text-foreground/70 mb-2">Signals Detected:</p>
                <ul className="space-y-1.5">
                  {signals.map((signal, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground/80 flex items-start gap-2 leading-relaxed">
                      <span className="text-accent mt-0.5">•</span>
                      <span>{signal}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default TruthMatrix;
