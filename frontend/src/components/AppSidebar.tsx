import { Link, useLocation } from "react-router-dom";
import { Home, Search, Newspaper, User } from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  { icon: Home, label: "Home", path: "/" },
  { icon: Search, label: "Check", path: "/check" },
  { icon: Newspaper, label: "Feed", path: "/feed" },
  { icon: User, label: "Profile", path: "/" },
];

const AppSidebar = () => {
  const location = useLocation();

  return (
    <motion.aside
      initial={{ x: -60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="hidden md:flex fixed left-0 top-0 h-screen w-16 flex-col items-center py-8 gap-8 z-50 backdrop-blur-2xl border-r border-border/50"
      style={{ background: 'hsl(222 47% 5% / 0.9)' }}
    >
      <div className="w-8 h-8 rounded-lg flex items-center justify-center mb-4"
        style={{ background: 'linear-gradient(135deg, hsl(239 84% 67%), hsl(187 92% 53%))' }}>
        <span className="text-white font-mono text-xs font-bold">TP</span>
      </div>

      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        return (
          <Link key={item.label} to={item.path}>
            <motion.div
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
              className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
                isActive
                  ? "bg-primary/15 text-primary shadow-[0_0_15px_-3px_hsl(239_84%_67%_/_0.3)]"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary"
              }`}
            >
              <item.icon className="w-5 h-5" />
            </motion.div>
          </Link>
        );
      })}
    </motion.aside>
  );
};

export default AppSidebar;
