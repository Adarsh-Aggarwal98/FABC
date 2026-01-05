import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ContactSection from "@/components/ContactSection";

export default function Contact() {
  return (
    <div className="min-h-screen" data-route="contact" data-contract-version="1.0.0" data-ready="contact-page">
      <Navbar />
      
      <div className="pt-20">
        <ContactSection />
      </div>

      <Footer />
    </div>
  );
}
