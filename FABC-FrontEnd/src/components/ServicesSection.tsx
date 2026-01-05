import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { FileCheck, Settings, FileText, DollarSign, ClipboardCheck, Briefcase, ArrowRight } from "lucide-react";
import { useState } from "react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";

const services = [
  {
    icon: FileCheck,
    title: "Professional SMSF Auditing",
    category: "Core Service",
    description: "Independent SMSF audits delivered under your brand. We handle the compliance while you keep the client relationship.",
    features: [
      "Branded audit reports with your firm's identity",
      "ASAE 3100 & GS 009 compliant audits",
      "Direct communication with your team only",
      "Comprehensive IAR documentation",
    ],
    highlight: true
  },
  {
    icon: Settings,
    title: "Complete SMSF Solutions",
    category: "Practice Growth",
    description: "End to end SMSF administration services. Expand your service offering without expanding your team.",
    features: [
      "Complete SMSF setup and registration",
      "Ongoing compliance and accounting",
      "Annual tax return preparation",
      "Regulatory filings and lodgements",
    ],
    highlight: false
  },
  {
    icon: ClipboardCheck,
    title: "Pre-Audit Preparation",
    category: "Efficiency",
    description: "Get audit-ready files delivered to your desk. We review, reconcile, and prepare so you can focus on advisory.",
    features: [
      "Bank and ledger reconciliations",
      "Gap analysis and issue identification",
      "Investment schedule verification",
      "Contribution and pension checks",
    ],
    highlight: false
  },
  {
    icon: Briefcase,
    title: "Practice Support",
    category: "Partnership",
    description: "Dedicated support for your accounting practice. We're an extension of your team, not a competitor.",
    features: [
      "Dedicated account manager",
      "Priority turnaround options",
      "Technical SMSF guidance",
      "Volume-based pricing",
    ],
    highlight: false
  },
  {
    icon: FileText,
    title: "Compliance Documentation",
    category: "Documentation",
    description: "Complete documentation services for complex SMSF matters. Professionally prepared, compliance-ready.",
    features: [
      "Trust deed reviews and amendments",
      "Minutes and resolutions",
      "Member statements",
      "ATO and ASIC correspondence",
    ],
    highlight: false
  },
  {
    icon: DollarSign,
    title: "Pension & Benefits",
    category: "Specialist",
    description: "Complex pension and benefit documentation handled by specialists. From commencement to death benefits.",
    features: [
      "Pension commencement documents",
      "Lump sum documentation",
      "Death benefit processing",
      "Reversionary pension setup",
    ],
    highlight: false
  },
];

export default function ServicesSection() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="services" className="py-20 md:py-24 lg:py-32 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-blue-100/50 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-cyan-100/50 to-transparent rounded-full blur-3xl" />
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
            className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            Built for Accountants
          </motion.span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            SMSF Services That{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              Grow Your Practice
            </span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Partner with us to offer comprehensive SMSF services without the overhead.
            We work behind the scenes. Your clients stay yours.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8" data-list="services">
          {services.map((service, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              data-entity-type="service"
              data-entity-id={`service-${index}`}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <Card
                className={`p-6 md:p-8 h-full transition-all duration-500 flex flex-col relative overflow-hidden group cursor-pointer
                  ${service.highlight ? 'border-2 border-primary/30 bg-gradient-to-br from-primary/5 to-transparent' : ''}
                  ${hoveredIndex === index ? 'shadow-xl shadow-primary/10 -translate-y-1' : 'hover:shadow-lg'}
                `}
                data-testid={`service-${index}`}
              >
                {/* Hover gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {service.highlight && (
                  <div className="absolute top-4 right-4">
                    <span className="px-2 py-1 text-xs font-semibold bg-primary text-white rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="relative">
                  <div className="flex items-start gap-4 mb-4">
                    <motion.div
                      className={`flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300
                        ${hoveredIndex === index
                          ? 'bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/25'
                          : 'bg-primary/10'}
                      `}
                      whileHover={{ rotate: [0, -5, 5, 0] }}
                      transition={{ duration: 0.5 }}
                    >
                      <service.icon className={`h-7 w-7 transition-colors duration-300 ${hoveredIndex === index ? 'text-white' : 'text-primary'}`} />
                    </motion.div>
                    <div className="flex-1">
                      <div className="text-xs font-semibold text-primary mb-1 uppercase tracking-wide">
                        {service.category}
                      </div>
                      <h3 className="text-xl font-bold" data-col="title">
                        {service.title}
                      </h3>
                    </div>
                  </div>

                  <p className="text-muted-foreground mb-6 leading-relaxed" data-col="description">
                    {service.description}
                  </p>

                  <ul className="space-y-3 mb-6">
                    {service.features.map((feature, idx) => (
                      <motion.li
                        key={idx}
                        className="flex items-start text-sm"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 * idx }}
                      >
                        <span className="mr-3 mt-0.5 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                          <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </span>
                        <span className="text-foreground/80">{feature}</span>
                      </motion.li>
                    ))}
                  </ul>

                  <div className="mt-auto pt-4 border-t border-border/50">
                    <Link href="/contact">
                      <span className="inline-flex items-center text-sm font-medium text-primary group-hover:text-blue-700 transition-colors">
                        Learn more
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </span>
                    </Link>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="inline-flex flex-col sm:flex-row gap-4 items-center justify-center p-8 rounded-2xl bg-gradient-to-r from-slate-50 via-blue-50/50 to-cyan-50/50 border border-border/50">
            <div className="text-center sm:text-left">
              <h3 className="text-xl font-bold mb-1">Ready to scale your SMSF practice?</h3>
              <p className="text-muted-foreground">Get a custom quote based on your volume</p>
            </div>
            <Link href="/contact">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg shadow-blue-500/25">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
