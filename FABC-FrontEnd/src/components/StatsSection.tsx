import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Building2, Users, FileCheck, Clock } from "lucide-react";

interface StatCardProps {
  value: number;
  suffix?: string;
  prefix?: string;
  label: string;
  description: string;
  dataKpi: string;
  icon: React.ElementType;
  gradient: string;
}

function StatCard({ value, suffix = "", prefix = "", label, description, dataKpi, icon: Icon, gradient }: StatCardProps) {
  const [count, setCount] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !hasAnimated) {
          setHasAnimated(true);
          const duration = 2000;
          const steps = 60;
          const increment = value / steps;
          let current = 0;

          const timer = setInterval(() => {
            current += increment;
            if (current >= value) {
              setCount(value);
              clearInterval(timer);
            } else {
              setCount(Math.floor(current));
            }
          }, duration / steps);

          return () => clearInterval(timer);
        }
      },
      { threshold: 0.3 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [value, hasAnimated]);

  return (
    <motion.div
      ref={ref}
      className="relative group"
      data-kpi={dataKpi}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center p-8 rounded-2xl bg-white border border-border/50 shadow-sm hover:shadow-xl hover:border-primary/20 transition-all duration-500 h-full">
        {/* Icon */}
        <motion.div
          className={`w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
          whileHover={{ rotate: [0, -5, 5, 0] }}
        >
          <Icon className="h-8 w-8 text-white" />
        </motion.div>

        {/* Value */}
        <div className="mb-3">
          <span
            className={`text-5xl md:text-6xl font-bold bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}
            data-testid={`stat-${dataKpi}`}
          >
            {prefix}{count}{suffix}
          </span>
        </div>

        {/* Label */}
        <div className="text-lg font-bold mb-2 text-foreground">
          {label}
        </div>

        {/* Description */}
        <div className="text-sm text-muted-foreground leading-relaxed">
          {description}
        </div>

        {/* Decorative line */}
        <motion.div
          className={`absolute bottom-0 left-1/2 -translate-x-1/2 h-1 bg-gradient-to-r ${gradient} rounded-full`}
          initial={{ width: 0 }}
          whileInView={{ width: "40%" }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
        />
      </div>
    </motion.div>
  );
}

export default function StatsSection() {
  return (
    <section className="py-16 md:py-20 lg:py-24 bg-gradient-to-b from-white via-slate-50/50 to-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-blue-100/30 via-transparent to-cyan-100/30 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 relative">
        <motion.div
          className="text-center mb-12 md:mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <motion.span
            className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            By The Numbers
          </motion.span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Trusted by{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              Accounting Firms
            </span>{" "}
            Australia-Wide
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Our track record speaks for itself. Here's why accountants choose us
            as their SMSF audit and compliance partner.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
          <StatCard
            value={500}
            suffix="+"
            label="Partner Firms"
            description="Accounting practices across Australia trust us with their SMSF audits and compliance"
            dataKpi="partner-firms"
            icon={Building2}
            gradient="from-blue-500 to-cyan-500"
          />
          <StatCard
            value={18}
            suffix="+"
            label="Years Experience"
            description="CPA and Chartered Accountant-led team with deep SMSF expertise"
            dataKpi="years-experience"
            icon={Users}
            gradient="from-purple-500 to-pink-500"
          />
          <StatCard
            value={100}
            suffix="%"
            label="Compliance Rate"
            description="Every audit meets ASAE 3100, GS 009, and ATO standards"
            dataKpi="compliance-rate"
            icon={FileCheck}
            gradient="from-green-500 to-emerald-500"
          />
          <StatCard
            value={5}
            label="Day Turnaround"
            description="Average time from file submission to completed audit report"
            dataKpi="turnaround-days"
            icon={Clock}
            gradient="from-orange-500 to-red-500"
          />
        </div>

        <motion.div
          className="text-center mt-12 md:mt-16"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <p className="text-lg font-medium text-foreground">
            Join the growing network of accountants who've streamlined their SMSF practice
          </p>
        </motion.div>
      </div>
    </section>
  );
}
