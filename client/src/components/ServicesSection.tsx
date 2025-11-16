import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { FileCheck, Settings, FileText, DollarSign, ClipboardCheck, Users, FileSignature } from "lucide-react";
import ASICLogo from "@/images/ASIC.png";
import CPALogo from "@/images/CPA.jpg";
import BGLLogo from "@/images/Logo_BGL.png";

const services = [
  {
    icon: FileCheck,
    title: "SMSF Auditing",
    category: "Compliance",
    description: "Comprehensive and Independent SMSF Audit Solutions in strict accordance with ASAE 3100 and GS 009 standards and more.",
    features: [
      "Financial Statement Audit",
      "Compliance Audit & SISA/SISR evaluation",
      "Independent Auditor's Report (IAR)",
      "Audit Contravention Reporting",
    ]
  },
  {
    icon: Settings,
    title: "Outsourcing Solution",
    category: "Administration",
    description: "Seamless, End-to-End SMSF Outsourcing Solutions for accounting firms, financial advisors, and trustees and more.",
    features: [
      "SMSF Setup and Registration",
      "Ongoing Compliance Management",
      "Accounting and Bookkeeping",
      "Taxation and Regulatory Filings",
    ]
  },
  {
    icon: ClipboardCheck,
    title: "Pre-Audit Readiness",
    category: "Preparation",
    description: "Proactive SMSF financial & compliance review, Pre-Audit Preparation and Risk Minimization to ensure smooth, timely SMSF compliance and value derived and more.",
    features: [
      "SMSF Review and Gap Analysis",
      "Bank and Ledger Reconciliations",
      "Contribution and Benefit Verification",
      "Mock Audit and Risk Identification",
    ]
  },
  {
    icon: FileText,
    title: "Compliance Framework and management",
    category: "Documentation",
    description: "Strengthen your SMSF with a proven compliance framework—expertly managed to meet ATO and ASIC standards every step of the way and more.",
    features: [
      "Trust deed amendments and variations",
      "Member application processing",
      "Regulatory compliance review",
      "Documentation updates",
    ]
  },
  {
    icon: FileSignature,
    title: "Lump Sum Documentation",
    category: "Benefits",
    description: "Comprehensive preparation of ATO registrations and benefit payment documentation and more.",
    features: [
      "ATO registration support",
      "Benefit payment documents",
      "Compliance verification",
      "Trustee guidance",
    ]
  },
  {
    icon: DollarSign,
    title: "Pension Planning and Commencement",
    category: "Retirement",
    description: "Solving asset rich, cash poor SMSF issues -whether during accumulation or pension phase of your SMSF and more.",
    features: [
      "Pension documentation",
      "Payment calculations",
      "Reversionary pension setup",
      "Compliance checks",
    ]
  },
];

export default function ServicesSection() {
  return (
    <section id="services" className="py-20 md:py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Comprehensive SMSF Solutions Made Easy
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
           Expert guidance for everyone and for every stage - from SMSF planning to auditing to outsourcing. 

Access our professional SMSF advice & services without switching your accountant or auditor. 

We work alongside your existing trusted team of Accountant and/ or auditor to strengthen compliance, strategy, and value—all tailored to your fund’s goals.

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
            >
              <Card className="p-6 md:p-8 h-full hover-elevate transition-all duration-300 flex flex-col" data-testid={`service-${index}`}>
                <div className="flex items-start gap-4 mb-4">
                  <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                    <service.icon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="text-xs font-semibold text-primary mb-1 uppercase tracking-wide">
                      {service.category}
                    </div>
                    <h3 className="text-xl font-semibold" data-col="title">
                      {service.title}
                    </h3>
                  </div>
                </div>

                <p className="text-muted-foreground mb-4 leading-relaxed" data-col="description">
                  {service.description}
                </p>

                <ul className="mt-auto space-y-2">
                  {service.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start text-sm text-muted-foreground">
                      <span className="mr-2 mt-1 text-primary">•</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Credentials Section */}
        {/* <motion.div
          className="mt-20 pt-16 border-t"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center mb-12">
            <h3 className="text-2xl md:text-3xl font-bold mb-3">Our Credentials</h3>
            <p className="text-muted-foreground">Trusted partnerships and professional certifications</p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
            <motion.div
              className="grayscale hover:grayscale-0 transition-all duration-300"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <img src={ASICLogo} alt="ASIC Registered" className="h-16 md:h-20 object-contain" />
            </motion.div>
            <motion.div
              className="grayscale hover:grayscale-0 transition-all duration-300"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <img src={CPALogo} alt="CPA Australia" className="h-16 md:h-20 object-contain" />
            </motion.div>
            <motion.div
              className="grayscale hover:grayscale-0 transition-all duration-300"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <img src={BGLLogo} alt="BGL Partner" className="h-16 md:h-20 object-contain" />
            </motion.div>
          </div>
        </motion.div> */}
      </div>
    </section>
  );
}
