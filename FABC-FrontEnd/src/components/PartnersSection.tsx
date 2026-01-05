import { motion } from "framer-motion";
import CPALogo from "@/images/CPA.jpg";
import BGLLogo from "@/images/Logo_BGL.png";
import ASICLogo from "@/images/ASIC.png";

const partners = [
  {
    name: "CPA Australia",
    logo: CPALogo,
    description: "Certified Practicing Accountants"
  },
  {
    name: "BGL",
    logo: BGLLogo,
    description: "Simple Fund 360"
  },
  {
    name: "ASIC Registered",
    logo: ASICLogo,
    description: "Australian Securities & Investments Commission"
  },
  {
    name: "CA ANZ",
    logo: null, // Placeholder - can add logo later
    description: "Chartered Accountants Australia and New Zealand"
  },
];

export default function PartnersSection() {
  const duplicatedPartners = [...partners, ...partners];

  return (
    <section className="py-16 md:py-20 bg-white overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl md:text-3xl font-bold mb-2">
            Our Credentials
          </h2>
        </motion.div>

        <div className="relative">
          <div className="flex animate-scroll gap-4">
            {duplicatedPartners.map((partner, index) => (
              <div
                key={`partner-${index}`}
                className="flex-shrink-0 px-4 md:px-6"
                data-testid={`partner-${index}`}
              >
                <motion.div
                  className="group relative bg-white rounded-xl p-6 md:p-8 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100"
                  whileHover={{ scale: 1.05, y: -5 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="w-56 md:w-64 h-32 md:h-40 flex items-center justify-center">
                    {partner.logo ? (
                      <motion.img
                        src={partner.logo}
                        alt={partner.name}
                        className="max-w-full max-h-full object-contain transition-all duration-300"
                        style={{
                          padding: '1rem',
                          imageRendering: 'crisp-edges'
                        }}
                        initial={{ opacity: 0, scale: 0.8 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                      />
                    ) : (
                      <div className="text-center">
                        <div className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">
                          {partner.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {partner.description}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Hover tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                    <div className="bg-gray-900 text-white text-xs rounded-lg py-2 px-3 whitespace-nowrap shadow-lg">
                      {partner.description}
                      <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
                    </div>
                  </div>
                </motion.div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .animate-scroll {
          animation: scroll 30s linear infinite;
        }
        .animate-scroll:hover {
          animation-play-state: paused;
        }
      `}</style>
    </section>
  );
}
