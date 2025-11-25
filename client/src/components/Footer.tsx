import { Link } from "wouter";
import { Twitter, Facebook, Linkedin } from "lucide-react";
import cpaLogo from "@/images/CPA.jpg";
import asicLogo from "@/images/ASIC.png";
import bglLogo from "@/images/Logo_BGL.png";

export default function Footer() {
  return (
    <footer className="bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40 border-t">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          <div className="lg:col-span-2">
            <h3 className="text-2xl font-bold text-primary mb-3">
              AusSuperSource
            </h3>
            <p className="text-muted-foreground max-w-md leading-relaxed mb-6">
             Australia’s leading SMSF specialists—we partner with Accountants, Finance and Real Estate professionals, Lawyers, Mortgage Brokers, and Individual Trustees to deliver end-to-end SMSF planning, advice, and compliance solutions you can trust.
            </p>
            
            <div>
              <h4 className="font-semibold mb-3">Supportive Partners</h4>
              <div className="flex flex-wrap gap-6 items-center">
                <div className="bg-white p-3 rounded-md border border-gray-200">
                  <img
                    src={asicLogo}
                    alt="ASIC Registered"
                    className="h-14 w-auto object-contain"
                  />
                </div>
                <div className="bg-white p-3 rounded-md border border-gray-200">
                  <img
                    src={cpaLogo}
                    alt="CPA Australia"
                    className="h-14 w-auto object-contain"
                  />
                </div>
                <div className="bg-white p-3 rounded-md border border-gray-200">
                  <img
                    src={bglLogo}
                    alt="BGL 360 Certified"
                    className="h-14 w-auto object-contain"
                  />
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/about">
                  <button className="text-muted-foreground hover:text-primary transition-colors text-sm">
                    About Us
                  </button>
                </Link>
              </li>
              <li>
                <Link href="/services">
                  <button className="text-muted-foreground hover:text-primary transition-colors text-sm">
                    Services
                  </button>
                </Link>
              </li>
              <li>
                <Link href="/team">
                  <button className="text-muted-foreground hover:text-primary transition-colors text-sm">
                    Our Team
                  </button>
                </Link>
              </li>
              <li>
                <Link href="/privacy">
                  <button className="text-muted-foreground hover:text-primary transition-colors text-sm">
                    Privacy Statement
                  </button>
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Contact</h4>
            <ul className="space-y-2 text-sm text-muted-foreground mb-6">
              <li className="font-medium text-foreground">Sydney Office:</li>
              <li>Level 7/186 Burwood Rd</li>
              <li>Burwood, Sydney NSW 2134</li>
              <li className="mt-3">
                <a
                  href="tel:+61 426 784 982"
                  className="hover:text-primary transition-colors"
                >
                  +61 426 784 982
                </a>
              </li>
              <li>
                <a
                  href="tel:02 8004 8156"
                  className="hover:text-primary transition-colors"
                >
                  02 8004 8156
                </a>
              </li>
              <li>
                <a
                  href="mailto:info@aussupersource.com.au"
                  className="hover:text-primary transition-colors"
                >
                  info@aussupersource.com.au
                </a>
              </li>
            </ul>

            <div>
              <h4 className="font-semibold mb-3">Social Links</h4>
              <div className="flex gap-3">
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="h-10 w-10 rounded-full bg-[#1DA1F2] flex items-center justify-center text-white hover-elevate transition-all"
                  aria-label="Twitter"
                  data-testid="social-twitter"
                >
                  <Twitter className="h-5 w-5" />
                </a>
                <a
                  href="https://facebook.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="h-10 w-10 rounded-full bg-[#4267B2] flex items-center justify-center text-white hover-elevate transition-all"
                  aria-label="Facebook"
                  data-testid="social-facebook"
                >
                  <Facebook className="h-5 w-5" />
                </a>
                <a
                  href="https://linkedin.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="h-10 w-10 rounded-full bg-[#0077B5] flex items-center justify-center text-white hover-elevate transition-all"
                  aria-label="LinkedIn"
                  data-testid="social-linkedin"
                >
                  <Linkedin className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t pt-8 text-center text-sm text-muted-foreground">
          <p>
            © {new Date().getFullYear()} Australian Super Source Pty Ltd. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
