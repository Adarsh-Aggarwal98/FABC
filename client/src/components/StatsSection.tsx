import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

interface StatCardProps {
  value: number;
  suffix?: string;
  prefix?: string;
  label: string;
  description: string;
  dataKpi: string;
}

function StatCard({ value, suffix = "", prefix = "", label, description, dataKpi }: StatCardProps) {
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
      className="text-center p-6"
      data-kpi={dataKpi}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="mb-2">
        <span className="text-5xl md:text-6xl lg:text-7xl font-bold text-primary" data-testid={`stat-${dataKpi}`}>
          {prefix}{count}{suffix}
        </span>
      </div>
      <div className="text-base md:text-lg font-semibold mb-1">
        {label}
      </div>
      <div className="text-sm text-muted-foreground">
        {description}
      </div>
    </motion.div>
  );
}

export default function StatsSection() {
  return (
    <section className="py-16 md:py-20 lg:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-12 md:mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            SMSF Expertise You Can Count On
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            At AusSuperSource, we're on a mission to make SMSF management simple, fast, and stress-free. 
            Our professional team delivers comprehensive solutions that exceed expectations.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
          <StatCard
            value={100}
            suffix="%"
            label="Compliant SMSF Audits"
            description="We ensure every audit meets ASAE 3100 and GS 009 standards—guaranteed"
            dataKpi="asic-registered"
          />
          <StatCard
            value={18}
            suffix="+"
            label="Years Experience"
            description="Team powered by Chartered Accountants and CPAs with deep expertise"
            dataKpi="years-experience"
          />
          <StatCard
            value={5}
            label="Days Turnaround"
            description="Get your SMSF audit completed and delivered in 5 business days"
            dataKpi="smsf-administered"
          />
          <StatCard
            value={48}
            label="Hours Processing"
            description="90% of pre-audit tasks completed within 48 hours from submission"
            dataKpi="director-experience"
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
            Trusted by hundreds of Australian's for maximum compliance and peace of mind
          </p>
        </motion.div>
      </div>
    </section>
  );
}
