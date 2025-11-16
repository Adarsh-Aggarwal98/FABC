import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import FloatingContactButton from "@/components/FloatingContactButton";
import { CheckCircle, Target, Users, Award } from "lucide-react";
import { Card } from "@/components/ui/card";
import { motion } from "framer-motion";

export default function About() {
  const values = [
    {
      icon: Target,
      title: "Our Mission",
      description: "Simplifying SMSF management with ATO and ASIC compliance made easy—so your fund truly works for you."
    },
    {
      icon: Users,
      title: "Client First",
      description: "We work behind the scenes, representing you to maintain your client relationships"
    },
    {
      icon: Award,
      title: "Excellence",
      description: "18+ years of strong experience delivering compliant, professional end to end SMSF solutions."
    }
  ];

  return (
    <div className="min-h-screen" data-route="about" data-contract-version="1.0.0" data-ready="about-page">
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
            About Us
          </motion.h1>
          <motion.p
            className="text-xl text-white/80"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            Your trusted SMSF partner for over 18 years
          </motion.p>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-20 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-4xl mx-auto px-4 md:px-6 lg:px-8">
          <div className="prose prose-lg max-w-none">
            <p className="text-lg leading-relaxed mb-6 text-foreground">
              Australian Super Source Pty Ltd, a specialized SMSF compliance and advisory firm, has been facilitating Accountants, Financial advisors, Mortgage Brocker, Real estate Professional and Mom and Dads (individual) on wholesale SMSF solution provider for more than 18 years, offering services throughout Australia.
            </p>

            <p className="text-lg leading-relaxed mb-6 text-foreground">
              We regularly keep an eye on changes to legislation to ensure you and clients, are informed & kept up to date with the current best practice for SMSF management.
            </p>

            <p className="text-lg leading-relaxed mb-8 text-foreground">
              We are facilitating accountants & financial advisors so that they can get their clients' smsf administration, compliance and audit and all the documentation regarding rollovers, pension commencement & pension commutation, pension continuation, minutes, members' statements, contributing splitting, contribution reserves, arranging actuarial certificates, arranging property valuations and other compliance issues.
            </p>

            <Card className="bg-primary/5 border-l-4 border-primary p-6">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
                <p className="text-lg font-medium text-foreground">
                  We respect your privacy with your clients. We do not directly contact your clients, we work as we are representing you.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40">
        <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Our Values</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="p-8 h-full hover-elevate transition-all duration-300 text-center">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <value.icon className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{value.title}</h3>
                  <p className="text-muted-foreground">{value.description}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
      <FloatingContactButton />
    </div>
  );
}
