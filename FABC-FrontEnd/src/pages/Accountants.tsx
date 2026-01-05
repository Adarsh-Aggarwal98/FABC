import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { CheckCircle } from "lucide-react";

const steps = [
  "You request a fee quote and provide contact details by completing the Accountants & Advisors contact form",
  "We advise you of our proposed fees and contact you to discuss other administrative matters.",
  "On receipt of your fee confirmation we will send log-in details to our secure online client portal.",
  "You download the engagement letter for the trustees to sign.",
  "All documents required for Accounts & Audit are uploaded to our online client portal.",
  "We commence each Accounts and Audit once documents are uploaded to the portal.",
  "Accounts and Audits are completed in accordance with an agreed timetable.",
];

export default function Accountants() {
  return (
    <div className="min-h-screen" data-route="accountants" data-contract-version="1.0.0" data-ready="accountants-page">
      <Navbar />
      
      <section className="pt-32 pb-20 md:pt-40 md:pb-24 lg:pb-32">
        <div className="max-w-4xl mx-auto px-4 md:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
              Accountants & Advisors
            </h1>
            <p className="text-lg text-muted-foreground">
              The following are the indicative steps in the Accounts & Audit process:
            </p>
          </div>

          <div className="space-y-6">
            {steps.map((step, index) => (
              <div
                key={index}
                className="flex gap-4 p-6 bg-card rounded-lg border hover-elevate transition-all"
                data-testid={`step-${index}`}
              >
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-semibold">{index + 1}</span>
                  </div>
                </div>
                <div className="flex-1">
                  <p className="text-base leading-relaxed">{step}</p>
                </div>
                <div className="flex-shrink-0">
                  <CheckCircle className="h-6 w-6 text-primary" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
