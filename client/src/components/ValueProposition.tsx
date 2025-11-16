import { motion } from "framer-motion";
import { CheckCircle, Users, Zap, DollarSign, Shield, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/card";

const benefits = [
  {
    icon: CheckCircle,
    title: "100% Compliant",
    description: "Full adherence to SISA/SISR, ATO policies, and Australian Auditing Standards",
  },
  {
    icon: Users,
    title: "Expert SMSF Team",
    description: "Qualified auditors and accountants specializing in self-managed super funds",
  },
  {
    icon: Zap,
    title: "Fast Turnaround",
    description: "Quick processing with detailed reporting and actionable insights",
  },
  {
    icon: DollarSign,
    title: "Transparent & Value based Pricing",
    description: "No hidden fees—clear, upfront pricing built on value, not volume, for all SMSF services.",
  },
  {
    icon: Shield,
    title: "Comprehensive Support",
    description: "Full-service SMSF solutions from setup to ongoing compliance",
  },
  {
    icon: TrendingUp,
    title: "Risk Mitigation",
    description: "Proactive identification and resolution of ATO and ASIC compliance issues and contraventions—before they become problems.",
  },
];

export default function ValueProposition() {
  return (
    <section className="py-20 md:py-24 lg:py-32 bg-muted">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Less Complexity, More Confidence
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            At AusSuperSource, we don't think SMSF compliance should feel like solving
            a puzzle in the dark. That's why we've built services that are fast,
            professional, and remarkably straightforward.
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
                className="p-6 md:p-8 h-full hover-elevate transition-all duration-300"
                data-testid={`benefit-${index}`}
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <benefit.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{benefit.title}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {benefit.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
