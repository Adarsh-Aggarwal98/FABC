import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Mail } from "lucide-react";

export default function Privacy() {
  return (
    <div className="min-h-screen" data-route="privacy" data-contract-version="1.0.0" data-ready="privacy-page">
      <Navbar />
      
      <section className="pt-32 pb-20 md:pt-40 md:pb-24 lg:pb-32">
        <div className="max-w-4xl mx-auto px-4 md:px-6 lg:px-8">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
              Privacy Statement
            </h1>
            <p className="text-lg text-muted-foreground">
              Your privacy is important to Australian Super Source Pty Ltd. This privacy statement provides information about the personal information that Australian Super Source Pty Ltd collects, and the ways in which Australian Super Source Pty Ltd uses that personal information.
            </p>
          </div>

          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold mb-4">Personal information collection</h2>
              <p className="text-muted-foreground mb-3">
                Australian Super Source Pty Ltd may collect and use the following kinds of personal information:
              </p>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                <li>information about your use of this website;</li>
                <li>information that you provide using for the purpose of registering with the website;</li>
                <li>information that you provide for the purpose of subscribing to the website services; and</li>
                <li>any other information that you send to Australian Super Source Pty Ltd.</li>
              </ul>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Using personal information</h2>
              <p className="text-muted-foreground mb-3">
                Australian Super Source Pty Ltd may use your personal information to:
              </p>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                <li>administer the website;</li>
                <li>enable your access to and use of the website services;</li>
                <li>publish information about you on the website;</li>
                <li>send to you products that you purchase;</li>
                <li>supply to you services that you purchase;</li>
                <li>send you statements and invoices;</li>
                <li>collect payments from you; and</li>
                <li>send you marketing communications.</li>
              </ul>
              <p className="text-muted-foreground mt-4">
                Where Australian Super Source Pty Ltd discloses your personal information to its agents or sub-contractors for these purposes, the agent or sub-contractor in question will be obligated to use that personal information in accordance with the terms of this privacy statement.
              </p>
              <p className="text-muted-foreground mt-4">
                In addition to the disclosures reasonably necessary for the purposes identified elsewhere above, Australian Super Source Pty Ltd may disclose your personal information to the extent that it is required to do so by law, in connection with any legal proceedings or prospective legal proceedings, and in order to establish, exercise or defend its legal rights.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Securing your data</h2>
              <p className="text-muted-foreground">
                Australian Super Source Pty Ltd will take reasonable technical and organisational precautions to prevent the loss, misuse or alteration of your personal information. Australian Super Source Pty Ltd will store all the personal information you provide on its secure servers.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Cross-border data transfers</h2>
              <p className="text-muted-foreground mb-3">
                Information that Australian Super Source Pty Ltd collects may be stored and processed in and transferred between any of the countries in which Australian Super Source Pty Ltd operates to enable the use of the information in accordance with this privacy policy.
              </p>
              <p className="text-muted-foreground mb-3">
                In addition, personal information that you submit for publication on the website will be published on the internet and may be available around the world.
              </p>
              <p className="text-muted-foreground">
                You agree to such cross-border transfers of personal information.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Updating this statement</h2>
              <p className="text-muted-foreground">
                Australian Super Source Pty Ltd may update this privacy policy by posting a new version on this website. You should check this page occasionally to ensure you are familiar with any changes.
              </p>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Other websites</h2>
              <p className="text-muted-foreground mb-3">
                This website contains links to other websites.
              </p>
              <p className="text-muted-foreground">
                Australian Super Source Pty Ltd is not responsible for the privacy policies or practices of any third party.
              </p>
            </div>

            <div className="bg-muted/30 p-6 rounded-lg border">
              <h2 className="text-2xl font-semibold mb-4">Contact Australian Super Source Pty Ltd</h2>
              <p className="text-muted-foreground mb-4">
                If you have any questions about this privacy policy or the treatment of your personal information by Australian Super Source Pty Ltd, please write to:
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Mail className="h-5 w-5 text-primary" />
                  <span className="font-medium">By email:</span>
                  <a
                    href="mailto:info@aussupersource.com.au"
                    className="text-primary hover:underline"
                  >
                    info@aussupersource.com.au
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
