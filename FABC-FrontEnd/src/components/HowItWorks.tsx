import { motion } from "framer-motion";
import { Calendar, Phone, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";

const steps = [
  {
    number: "1",
    title: "Book Your Free Consultation",
    description: "Choose the SMSF service you need, pick your preferred time, and schedule a consultation. Completely free with no obligations.",
    icon: Calendar,
  },
  {
    number: "2",
    title: "Speak with an SMSF Expert",
    description: "Our qualified specialist will review your requirements, answer questions, and provide tailored guidance for your specific SMSF situation.",
    icon: Phone,
  },
  {
    number: "3",
    title: "Relax & Stay Compliant",
    description: "We handle everything including audits, compliance checks, and reporting. Most clients receive their completed IAR within 5 business days.",
    icon: CheckCircle,
  },
];

export default function HowItWorks() {
  return (
    <section className="py-20 md:py-24 lg:py-32 bg-[hsl(var(--dark-section))] text-[hsl(var(--dark-section-foreground))]">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-lg md:text-xl text-[hsl(var(--dark-section-foreground))]/70 max-w-2xl mx-auto">
            Simple steps. Maximum compliance. Zero stress.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 mb-12">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              className="relative"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary text-primary-foreground text-2xl font-bold mb-6">
                  {step.number}
                </div>
                
                <div className="mb-6">
                  <step.icon className="h-12 w-12 mx-auto text-primary" />
                </div>

                <h3 className="text-xl md:text-2xl font-semibold mb-4">
                  {step.title}
                </h3>
                
                <p className="text-[hsl(var(--dark-section-foreground))]/70">
                  {step.description}
                </p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-border -translate-x-1/2" style={{ width: 'calc(100% - 4rem)' }} />
              )}
            </motion.div>
          ))}
        </div>

        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Link href="/contact">
            <Button size="lg" className="text-base" data-testid="button-get-started">
              Get Started Today
            </Button>
          </Link>
        </motion.div>
      </div>
    </section>
  );
}
