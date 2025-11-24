import { Button } from "@/components/ui/button";
import { ArrowRight, Award } from "lucide-react";
import { Link } from "wouter";
import { useState, useEffect } from "react";
import heroImage from "@images/Professional_SMSF_office_collaboration_e65dfd08.png";
import cpaLogo from "@/images/CPA.jpg";
import asicLogo from "@/images/ASIC.png";
import bglLogo from "@/images/Logo_BGL.png";

export default function Hero() {
  const titles = ["Stress Free SMSF", "SMSF Health Check"];
  const [currentTitleIndex, setCurrentTitleIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTitleIndex((prevIndex) => (prevIndex + 1) % titles.length);
    }, 3000); // Change every 3 seconds

    return () => clearInterval(interval);
  }, []);
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-black/70 via-black/60 to-black/40" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-32 md:py-40">
        <div className="max-w-4xl">
          <div className="flex items-center gap-2 mb-6">
            <Award className="h-6 w-6 text-white" />
            <span className="text-sm font-medium text-white/90">
              18+ Years of SMSF Excellence
            </span>
          </div>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white leading-tight mb-6">
            <span
              key={currentTitleIndex}
              className="inline-block text-primary animate-fadeIn"
            >
              {titles[currentTitleIndex]}
            </span>
          </h1>

          <p className="text-lg md:text-xl text-white/90 mb-8 max-w-2xl leading-relaxed">
            Expert advice and administration of SMSF. One Stop SMSF solution provider for everyone throughout Australia.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 mb-12">
            <Link href="/contact">
              <Button
                size="lg"
                className="text-base"
                data-action="hero.contact"
                data-testid="button-contact-us"
              >
                Book a Free call
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/services">
              <Button
                size="lg"
                variant="outline"
                className="text-base bg-white/10 backdrop-blur-md border-white/20 text-white hover:bg-white/20"
                data-action="hero.services"
                data-testid="button-our-services"
              >
                Our Services
              </Button>
            </Link>
          </div>

          <div className="flex flex-wrap gap-6 items-center">
            <div className="flex items-center gap-2">
              <div className="h-16 w-16 rounded-md bg-white/90 backdrop-blur-md flex items-center justify-center border border-white/30 p-2">
                <img src={asicLogo} alt="ASIC Registered" className="w-full h-full object-contain" />
              </div>
              <div className="text-white">
                <div className="text-xs font-semibold">ASIC Registered</div>
                <div className="text-xs text-white/80">SMSF Auditor</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-16 w-16 rounded-md bg-white/90 backdrop-blur-md flex items-center justify-center border border-white/30 p-2">
                <img src={cpaLogo} alt="CPA Australia" className="w-full h-full object-contain" />
              </div>
              <div className="text-white">
                <div className="text-xs font-semibold">CPA Australia</div>
                <div className="text-xs text-white/80">Accredited</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-16 w-16 rounded-md bg-white/90 backdrop-blur-md flex items-center justify-center border border-white/30 p-2">
                <img src={bglLogo} alt="BGL 360 Certified" className="w-full h-full object-contain" />
              </div>
              <div className="text-white">
                <div className="text-xs font-semibold">BGL 360</div>
                <div className="text-xs text-white/80">Certified</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* <div className="h-12 w-12 rounded-md bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/30">
                <Award className="h-6 w-6 text-white" />
              </div>
              <div className="text-white">
                <div className="text-xs font-semibold">300+ SMSFs</div>
                <div className="text-xs text-white/80">Under Administration</div>
              </div> */}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
