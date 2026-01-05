import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import FloatingContactButton from "@/components/FloatingContactButton";
import TeamSection from "@/components/TeamSection";
import { motion } from "framer-motion";

export default function Team() {
  return (
    <div className="min-h-screen" data-route="team" data-contract-version="1.0.0" data-ready="team-page">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20 bg-gradient-to-br from-slate-700 via-slate-800 to-blue-900 text-white">
        <div className="max-w-4xl mx-auto px-4 md:px-6 lg:px-8 text-center">
          <motion.h1
            className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Meet Our Team
          </motion.h1>
          <motion.p
            className="text-xl text-white/80"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            Expert professionals dedicated to your SMSF success
          </motion.p>
        </div>
      </section>

      <div className="bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40">
        <TeamSection />
      </div>

      <Footer />
      <FloatingContactButton />
    </div>
  );
}
