import { Link } from "wouter";
import { Facebook, Linkedin, Mail, Phone, MapPin, ArrowRight } from "lucide-react";

// X (formerly Twitter) icon component
const XIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);
import { motion } from "framer-motion";
import cpaLogo from "@/images/CPA.jpg";
import asicLogo from "@/images/ASIC.png";
import bglLogo from "@/images/Logo_BGL.png";
import { Button } from "@/components/ui/button";

export default function Footer() {
  return (
    <footer className="bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 text-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl" />
      </div>

      {/* CTA Banner */}
      <div className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-8">
          <motion.div
            className="flex flex-col md:flex-row items-center justify-between gap-6 p-6 rounded-2xl bg-gradient-to-r from-blue-600/20 to-cyan-600/20 backdrop-blur-sm border border-white/10"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div>
              <h3 className="text-2xl font-bold mb-2">Ready to streamline your SMSF practice?</h3>
              <p className="text-white/70">Partner with us and focus on what you do best: advising clients.</p>
            </div>
            <Link href="/contact">
              <Button size="lg" className="bg-white text-slate-900 hover:bg-white/90 shadow-lg group">
                Be our SMSF Compliance Partner
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-10 relative">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Brand section */}
          <div className="lg:col-span-2">
            <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              AusSuperSource
            </h3>
            <p className="text-white/70 max-w-md leading-relaxed mb-6">
              Your trusted SMSF audit and compliance partner for Australian accounting firms. Professional solutions,
              fast turnaround, and complete compliance. All delivered behind the scenes so you can
              focus on growing your practice.
            </p>

            {/* Credentials */}
            <div>
              <h4 className="font-semibold mb-4 text-white/90">Accreditations & Partners</h4>
              <div className="flex flex-wrap gap-4 items-center">
                {[
                  { logo: asicLogo, name: "ASIC Registered" },
                  { logo: cpaLogo, name: "CPA Australia" },
                  { logo: bglLogo, name: "BGL 360 Certified" },
                ].map((item) => (
                  <motion.div
                    key={item.name}
                    className="bg-white/10 backdrop-blur-sm p-3 rounded-xl border border-white/10 hover:bg-white/15 hover:border-white/20 transition-all duration-300"
                    whileHover={{ scale: 1.05 }}
                  >
                    <img
                      src={item.logo}
                      alt={item.name}
                      className="h-10 w-auto object-contain"
                    />
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-6 text-lg">For Accountants</h4>
            <ul className="space-y-3">
              {[
                { label: "SMSF Auditing", href: "/services" },
                { label: "Complete SMSF Solutions", href: "/services" },
                { label: "Partner Program", href: "/contact" },
                { label: "About Us", href: "/about" },
                { label: "Our Team", href: "/team" },
                { label: "Privacy Policy", href: "/privacy" },
              ].map((link) => (
                <li key={link.label}>
                  <Link href={link.href}>
                    <button className="text-white/60 hover:text-white hover:translate-x-1 transition-all duration-300 text-sm flex items-center gap-2 group">
                      <span className="w-1 h-1 rounded-full bg-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                      {link.label}
                    </button>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-6 text-lg">Get in Touch</h4>
            <ul className="space-y-4 text-sm text-white/60 mb-8">
              <li className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-white">Sydney Office</div>
                  <div>Level 7/186 Burwood Rd</div>
                  <div>Burwood, NSW 2134</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-white">Melbourne Office</div>
                  <div>Office 3077, Ground Floor</div>
                  <div>470 St Kilda Road</div>
                  <div>Melbourne, VIC 3004</div>
                </div>
              </li>
              <li>
                <a
                  href="tel:+61426784982"
                  className="flex items-center gap-3 hover:text-white transition-colors group"
                >
                  <Phone className="h-5 w-5 text-blue-400 group-hover:scale-110 transition-transform" />
                  +61 426 784 982
                </a>
              </li>
              <li>
                <a
                  href="tel:0280048156"
                  className="flex items-center gap-3 hover:text-white transition-colors group"
                >
                  <Phone className="h-5 w-5 text-blue-400 group-hover:scale-110 transition-transform" />
                  02 8004 8156
                </a>
              </li>
              <li>
                <a
                  href="mailto:info@aussupersource.com.au"
                  className="flex items-center gap-3 hover:text-white transition-colors group"
                >
                  <Mail className="h-5 w-5 text-blue-400 group-hover:scale-110 transition-transform" />
                  info@aussupersource.com.au
                </a>
              </li>
            </ul>

            {/* Social Links */}
            <div>
              <h4 className="font-semibold mb-4 text-sm text-white/90">Follow Us</h4>
              <div className="flex gap-3">
                {[
                  { icon: XIcon, href: "https://x.com", color: "hover:bg-black", label: "X" },
                  { icon: Facebook, href: "https://facebook.com", color: "hover:bg-[#4267B2]", label: "Facebook" },
                  { icon: Linkedin, href: "https://linkedin.com", color: "hover:bg-[#0077B5]", label: "LinkedIn" },
                ].map((social) => (
                  <motion.a
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center text-white/70 hover:text-white ${social.color} transition-all duration-300 border border-white/10 hover:border-transparent`}
                    aria-label={social.label}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <social.icon className="h-5 w-5" />
                  </motion.a>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/50">
          <p>
            © {new Date().getFullYear()} Australian Super Source Pty Ltd. All rights reserved.
          </p>
          <p>
            ASIC Registered SMSF Auditor • ABN: 50 122 940 596
          </p>
        </div>
      </div>
    </footer>
  );
}
