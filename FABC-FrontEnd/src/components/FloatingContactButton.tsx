import { useState } from "react";
import { MessageCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Link } from "wouter";
import { motion, AnimatePresence } from "framer-motion";

export default function FloatingContactButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Popup Card - Renders before button so it's behind */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed bottom-6 right-24 z-40 w-80"
            initial={{ scale: 0.8, opacity: 0, x: 20 }}
            animate={{ scale: 1, opacity: 1, x: 0 }}
            exit={{ scale: 0.8, opacity: 0, x: 20 }}
            transition={{ duration: 0.2 }}
          >
            <Card className="p-6 shadow-2xl">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-lg font-semibold">How can we help?</h3>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="ml-2"
                  data-testid="button-close-contact-card"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Get in touch with our SMSF experts
              </p>

              <div className="space-y-3">
                <Link href="/contact">
                  <Button
                    variant="default"
                    className="w-full"
                    onClick={() => setIsOpen(false)}
                    data-testid="button-contact-page"
                  >
                    Send us a message
                  </Button>
                </Link>

                <a href="tel:0289701102">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setIsOpen(false)}
                    data-testid="button-call-us"
                  >
                    Call us now
                  </Button>
                </a>

                <a href="mailto:info@aussupersource.com.au">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setIsOpen(false)}
                    data-testid="button-email-us"
                  >
                    Email us
                  </Button>
                </a>
              </div>

              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-muted-foreground text-center">
                  Mon-Fri: 9:00 AM - 5:00 PM AEST
                </p>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Button - Higher z-index so it's always clickable */}
      <motion.div
        className="fixed bottom-6 right-6 z-50"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 1, duration: 0.3 }}
      >
        <Button
          size="lg"
          className="rounded-full shadow-lg hover:shadow-xl transition-all duration-300 px-6"
          onClick={() => setIsOpen(!isOpen)}
          data-testid="button-floating-contact"
        >
          {isOpen ? (
            <>
              <X className="h-5 w-5 mr-2" />
              Close
            </>
          ) : (
            <>
              <MessageCircle className="h-5 w-5 mr-2" />
              Contact Us
            </>
          )}
        </Button>
      </motion.div>
    </>
  );
}
