import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Bell, ExternalLink, AlertTriangle, Info, AlertCircle, Loader2 } from "lucide-react";
import { fetchAtoAlerts, type AtoAlert } from "@/lib/api";

// Fallback data in case API is unavailable
const fallbackAlerts: AtoAlert[] = [
  {
    id: "1",
    title: "SMSF annual return deadline extended to 28 February 2025 for eligible funds",
    type: "update",
    link: "https://www.ato.gov.au/super/self-managed-super-funds/",
    active: true,
    priority: 1,
    createdAt: null,
    expiresAt: null,
  },
  {
    id: "2",
    title: "New contribution caps for 2024-25: Concessional $30,000, Non-concessional $120,000",
    type: "alert",
    link: "https://www.ato.gov.au/super/self-managed-super-funds/contributions-and-rollovers/",
    active: true,
    priority: 2,
    createdAt: null,
    expiresAt: null,
  },
  {
    id: "3",
    title: "Reminder: Ensure all SMSF investments are at arm's length before EOFY",
    type: "reminder",
    link: "https://www.ato.gov.au/super/self-managed-super-funds/investing/",
    active: true,
    priority: 3,
    createdAt: null,
    expiresAt: null,
  },
];

export default function FloatingATOBanner() {
  const [isVisible, setIsVisible] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [alerts, setAlerts] = useState<AtoAlert[]>(fallbackAlerts);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const data = await fetchAtoAlerts();
        if (data.length > 0) {
          setAlerts(data);
        }
      } catch (error) {
        console.error("Failed to load ATO alerts:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadAlerts();
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "alert":
        return <AlertTriangle className="h-3.5 w-3.5" />;
      case "reminder":
        return <AlertCircle className="h-3.5 w-3.5" />;
      default:
        return <Info className="h-3.5 w-3.5" />;
    }
  };

  const getTypeStyles = (type: string) => {
    switch (type) {
      case "alert":
        return "bg-red-500 text-white";
      case "reminder":
        return "bg-yellow-500 text-black";
      default:
        return "bg-blue-500 text-white";
    }
  };

  if (!isVisible || alerts.length === 0) return null;

  // Duplicate the alerts for seamless infinite scroll
  const duplicatedAlerts = [...alerts, ...alerts];

  return (
    <AnimatePresence>
      <motion.div
        className="fixed top-16 md:top-20 left-0 right-0 z-40 bg-white border-b border-gray-200 shadow-lg"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -50 }}
        transition={{ duration: 0.3 }}
      >
        {/* Animated shine effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/5 to-transparent"
          animate={{ x: ["-100%", "100%"] }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        />

        <div className="relative overflow-hidden">
          {/* Left fade gradient */}
          <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none" />

          {/* Right fade gradient */}
          <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none" />

          {/* ATO Label - Larger and more prominent */}
          <div className="absolute left-0 top-0 bottom-0 z-20 flex items-center pl-4 pr-8 bg-gradient-to-r from-white via-white to-transparent">
            <div className="flex items-center gap-3">
              <motion.div
                className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Bell className="h-5 w-5 text-white" />
              </motion.div>
              <div className="hidden sm:block">
                <span className="text-sm font-bold text-blue-600 block leading-tight">
                  ATO NEWS
                </span>
                <span className="text-xs text-gray-500">
                  Latest Updates
                </span>
              </div>
            </div>
          </div>

          {/* Close button - Larger */}
          <button
            onClick={() => setIsVisible(false)}
            className="absolute right-3 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-400 hover:text-gray-600 transition-all"
            aria-label="Close banner"
          >
            <X className="h-5 w-5" />
          </button>

          {/* Scrolling content - Larger padding and text */}
          <div
            className="py-4 pl-32 sm:pl-44 pr-16"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
          >
            <motion.div
              className="flex gap-12"
              animate={{
                x: isPaused ? 0 : "-50%",
              }}
              transition={{
                x: {
                  duration: 25,
                  repeat: Infinity,
                  ease: "linear",
                  repeatType: "loop",
                },
              }}
              style={{ width: "fit-content" }}
            >
              {duplicatedAlerts.map((alert, index) => (
                <a
                  key={`${alert.id}-${index}`}
                  href={alert.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 group whitespace-nowrap"
                >
                  <span className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-bold shadow-md ${getTypeStyles(alert.type)}`}>
                    {getTypeIcon(alert.type)}
                    <span>{alert.type.charAt(0).toUpperCase() + alert.type.slice(1)}</span>
                  </span>
                  <span className="text-base font-medium text-gray-800 group-hover:text-blue-600 transition-colors">
                    {alert.title}
                  </span>
                  <ExternalLink className="h-4 w-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                  <span className="text-gray-200 mx-6 text-2xl">|</span>
                </a>
              ))}
            </motion.div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
