import { Button } from "@/components/ui/button";
import { ArrowRight, Award, Users, Shield, Clock } from "lucide-react";
import { Link } from "wouter";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import heroImage from "@images/Professional_SMSF_office_collaboration_e65dfd08.png";
import cpaLogo from "@/images/CPA.jpg";
import asicLogo from "@/images/ASIC.png";
import bglLogo from "@/images/Logo_BGL.png";

export default function Hero() {
  const titles = ["Your SMSF Audit Partner", "Grow Your Practice", "Seamless SMSF Audits"];
  const [currentTitleIndex, setCurrentTitleIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTitleIndex((prevIndex) => (prevIndex + 1) % titles.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const floatingCards = [
    { icon: Users, text: "500+ Accountant Partners", delay: 0.2 },
    { icon: Shield, text: "100% Compliance Rate", delay: 0.4 },
    { icon: Clock, text: "5-Day Turnaround", delay: 0.6 },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0">
        <div
          className="absolute inset-0 bg-cover bg-center scale-105"
          style={{ backgroundImage: `url(${heroImage})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/90 via-blue-900/80 to-indigo-900/70" />
        <motion.div
          className="absolute inset-0 bg-gradient-to-tr from-primary/20 via-transparent to-purple-500/10"
          animate={{
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white/20 rounded-full"
            style={{
              left: `${15 + i * 15}%`,
              top: `${20 + (i % 3) * 25}%`,
            }}
            animate={{
              y: [-20, 20, -20],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 4 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-32 md:py-40">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="max-w-2xl">
            {/* Badge */}
            <motion.div
              className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Award className="h-5 w-5 text-yellow-400" />
              <span className="text-sm font-medium text-white">
                Trusted by 500+ Accounting Firms Across Australia
              </span>
            </motion.div>

            {/* Main heading */}
            <motion.h1
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <span className="block text-white/90 text-2xl md:text-3xl font-medium mb-2">
                For SMSF and Tax Accountants
              </span>
              <motion.span
                key={currentTitleIndex}
                className="inline-block bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                {titles[currentTitleIndex]}
              </motion.span>
            </motion.h1>

            <motion.p
              className="text-lg md:text-xl text-white/80 mb-8 max-w-xl leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              Focus on your clients while we handle their SMSF audits. Professional solutions,
              fast turnaround, and complete compliance, all delivered under your brand.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 mb-12"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Link href="/contact">
                <Button
                  size="lg"
                  className="text-base group bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg shadow-blue-500/25 transition-all duration-300"
                  data-action="hero.contact"
                  data-testid="button-contact-us"
                >
                  Partner With Us
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link href="/services">
                <Button
                  size="lg"
                  variant="outline"
                  className="text-base bg-white/5 backdrop-blur-md border-white/30 text-white hover:bg-white/15 hover:border-white/50 transition-all duration-300"
                  data-action="hero.services"
                  data-testid="button-our-services"
                >
                  View Accountant Services
                </Button>
              </Link>
            </motion.div>

            {/* Trust badges */}
            <div className="flex flex-wrap gap-4 items-center">
              {[
                { logo: asicLogo, name: "ASIC Registered", sub: "SMSF Auditor" },
                { logo: cpaLogo, name: "CPA Australia", sub: "Accredited" },
                { logo: bglLogo, name: "BGL 360", sub: "Certified" },
              ].map((badge, index) => (
                <motion.div
                  key={badge.name}
                  className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/15 transition-all duration-300 cursor-default"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="h-10 w-10 rounded-lg bg-white flex items-center justify-center p-1.5">
                    <img src={badge.logo} alt={badge.name} className="w-full h-full object-contain" />
                  </div>
                  <div className="text-white">
                    <div className="text-xs font-semibold">{badge.name}</div>
                    <div className="text-xs text-white/70">{badge.sub}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Right side - Floating stat cards */}
          <div className="hidden lg:block relative">
            <div className="relative h-[400px]">
              {floatingCards.map((card, index) => (
                <motion.div
                  key={card.text}
                  className="absolute bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl"
                  style={{
                    top: `${index * 120}px`,
                    right: `${index % 2 === 0 ? 0 : 60}px`,
                  }}
                  initial={{ opacity: 0, x: 50, y: 20 }}
                  animate={{ opacity: 1, x: 0, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 + card.delay }}
                  whileHover={{
                    scale: 1.05,
                    boxShadow: "0 25px 50px -12px rgba(59, 130, 246, 0.25)"
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                      <card.icon className="h-6 w-6 text-white" />
                    </div>
                    <span className="text-white font-semibold text-lg">{card.text}</span>
                  </div>
                </motion.div>
              ))}

              {/* Decorative gradient orb */}
              <motion.div
                className="absolute -bottom-20 -right-20 w-64 h-64 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full blur-3xl"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.5, 0.3],
                }}
                transition={{
                  duration: 6,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 rounded-full border-2 border-white/30 flex items-start justify-center p-2">
          <motion.div
            className="w-1.5 h-3 bg-white/60 rounded-full"
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>
      </motion.div>
    </section>
  );
}
