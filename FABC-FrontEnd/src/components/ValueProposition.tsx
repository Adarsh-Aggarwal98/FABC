import { motion } from "framer-motion";
import { UserCheck, Clock, Eye, DollarSign, Shield, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/card";

const benefits = [
  {
    icon: UserCheck,
    title: "Your Brand, Our Work",
    description: "Professional audits delivered under your firm's name. Clients never know we exist, so you maintain full relationship control.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Clock,
    title: "5-Day Turnaround",
    description: "Get completed audits back in 5 business days. Rush options available for urgent deadlines.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: Eye,
    title: "Zero Client Contact",
    description: "We communicate only with your team. Your client relationships stay protected, guaranteed.",
    gradient: "from-orange-500 to-red-500",
  },
  {
    icon: DollarSign,
    title: "Volume-Based Pricing",
    description: "The more you send, the more you save. Transparent pricing with no hidden fees or surprises.",
    gradient: "from-green-500 to-emerald-500",
  },
  {
    icon: Shield,
    title: "100% Compliant",
    description: "ASAE 3100, GS 009, SISA/SISR compliant. ASIC registered auditors you can trust.",
    gradient: "from-indigo-500 to-violet-500",
  },
  {
    icon: TrendingUp,
    title: "Scale Without Hiring",
    description: "Take on more SMSF clients without expanding your team. We handle the workload, you grow the revenue.",
    gradient: "from-teal-500 to-cyan-500",
  },
];

export default function ValueProposition() {
  return (
    <section className="py-20 md:py-24 lg:py-32 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, -30, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"
          animate={{
            x: [0, -30, 0],
            y: [0, 50, 0],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 relative">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <motion.span
            className="inline-block px-4 py-1.5 rounded-full bg-white/10 text-white/90 text-sm font-medium mb-4 backdrop-blur-sm border border-white/10"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            Why Accountants Choose Us
          </motion.span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
            Focus on Advisory.{" "}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              We Handle Audits.
            </span>
          </h2>
          <p className="text-lg md:text-xl text-white/70 max-w-3xl mx-auto">
            Stop losing billable hours to SMSF audits. Partner with specialists
            who deliver quality, speed, and complete discretion.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card
                className="p-6 md:p-8 h-full bg-white/5 backdrop-blur-xl border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-500 group"
                data-testid={`benefit-${index}`}
              >
                <motion.div
                  className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${benefit.gradient} flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300`}
                  whileHover={{ rotate: [0, -10, 10, 0] }}
                  transition={{ duration: 0.5 }}
                >
                  <benefit.icon className="h-7 w-7 text-white" />
                </motion.div>
                <h3 className="text-xl font-bold mb-3 text-white group-hover:text-blue-300 transition-colors">
                  {benefit.title}
                </h3>
                <p className="text-white/60 leading-relaxed group-hover:text-white/80 transition-colors">
                  {benefit.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Trust indicators */}
        <motion.div
          className="mt-16 flex flex-wrap items-center justify-center gap-8 text-white/60"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm">ASIC Registered</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm">CPA Accredited</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm">18+ Years Experience</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-sm">500+ Partner Firms</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
