import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { WalletProvider } from "@/context/WalletContext";
import Navbar from "@/components/Navbar";
import AppSidebar from "@/components/AppSidebar";
import ScannerCursor from "@/components/ScannerCursor";
import Index from "./pages/Index";
import CheckNews from "./pages/CheckNews";
import ClaimFeed from "./pages/ClaimFeed";
import ClaimDetail from "./pages/ClaimDetail";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      refetchOnMount: false,
      refetchOnReconnect: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <WalletProvider>
          <ScannerCursor />
          <AppSidebar />
          <Navbar />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/check" element={<CheckNews />} />
            <Route path="/feed" element={<ClaimFeed />} />
            <Route path="/claim/:claimHash" element={<ClaimDetail />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </WalletProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
