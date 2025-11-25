import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Mail, Phone, MapPin } from "lucide-react";
import { submitContactForm } from "@/lib/api";

const contactFormSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  phone: z.string().optional(),
  state: z.string().min(1, "Please select a state"),
  subject: z.string().min(2, "Subject is required"),
  message: z.string().min(10, "Message must be at least 10 characters"),
});

type ContactFormValues = z.infer<typeof contactFormSchema>;

const australianStates = [
  { value: "NSW", label: "NSW" },
  { value: "VIC", label: "VIC" },
  { value: "QLD", label: "QLD" },
  { value: "SA", label: "SA" },
  { value: "WA", label: "WA" },
  { value: "TAS", label: "TAS" },
  { value: "ACT", label: "ACT" },
  { value: "NT", label: "NT" },
];

export default function ContactSection() {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      state: "",
      subject: "",
      message: "",
    },
  });

  const onSubmit = async (data: ContactFormValues) => {
    setIsSubmitting(true);

    try {
      const response = await submitContactForm(data);

      if (response.status === 'success') {
        toast({
          title: "Message sent!",
          description: response.message || "We'll get back to you within 24 hours.",
          variant: "default",
        });
        form.reset();
      } else {
        toast({
          title: "Failed to send message",
          description: response.message || "Please try again later.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Contact form error:", error);
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section id="contact" className="py-20 md:py-24 lg:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Contact Us
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Let's discuss how we can help with your SMSF needs
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-semibold mb-6">Our Locations</h3>

            {/* Sydney - Head Office */}
            <div className="mb-8 p-6 bg-muted/30 rounded-lg hover-elevate transition-all duration-300">
              <div className="flex items-start gap-3 mb-3">
                <MapPin className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-lg mb-1">Sydney (NSW)</h4>
                  <p className="text-muted-foreground text-sm">
                    180, Level 7/186, Burwood Rd, Burwood NSW 2134
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 mb-2">
                <Phone className="h-4 w-4 text-primary flex-shrink-0 mt-1" />
                <div className="space-y-1">
                  <a href="tel:+61 426 784 982" className="text-sm text-muted-foreground hover:text-primary transition-colors block">
                    +61 426 784 982
                  </a>
                  <a href="tel:0280048156" className="text-sm text-muted-foreground hover:text-primary transition-colors block">
                    02 8004 8156
                  </a>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="h-4 w-4 text-primary flex-shrink-0 mt-1" />
                <a href="mailto:info@aussupersource.com.au" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  info@aussupersource.com.au
                </a>
              </div>
            </div>

            {/* Victoria - Melbourne */}
            <div className="mb-8 p-6 bg-muted/30 rounded-lg hover-elevate transition-all duration-300">
              <div className="flex items-start gap-3 mb-3">
                <MapPin className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-lg mb-1">Melbourne (Victoria)</h4>
                  <p className="text-muted-foreground text-sm">
                    Office 3077, Ground Floor, 470, St Kilda Road, Melbourne (VIC) 3004
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 mb-2">
                <Phone className="h-4 w-4 text-primary flex-shrink-0 mt-1" />
                <a href="tel:+61426784982" className="text-sm text-muted-foreground hover:text-primary transition-colors block">
                  +61 426 784 982
                </a>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="h-4 w-4 text-primary flex-shrink-0 mt-1" />
                <a href="mailto:info@aussupersource.com.au" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  info@aussupersource.com.au
                </a>
              </div>
            </div>

            {/* Adelaide - SA */}
            <div className="mb-8 p-6 bg-muted/30 rounded-lg hover-elevate transition-all duration-300">
              <div className="flex items-start gap-3 mb-3">
                <MapPin className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-lg mb-1">Adelaide (SA)</h4>
                  <p className="text-muted-foreground text-sm">
                    Adelaide, SA
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="h-4 w-4 text-primary flex-shrink-0 mt-1" />
                <a href="mailto:info@aussupersource.com.au" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  info@aussupersource.com.au
                </a>
              </div>
            </div>

            <div className="p-6 bg-primary/5 rounded-lg border-l-4 border-primary">
              <h4 className="font-semibold mb-2">Business Hours</h4>
              <p className="text-muted-foreground text-sm">
                Monday - Friday: 9:00 AM - 5:00 PM AEST
              </p>
              <p className="text-muted-foreground text-sm">
                Saturday - Sunday: Closed
              </p>
            </div>
          </div>

          <div>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name *</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Your name"
                          {...field}
                          data-field="contact.name"
                          data-testid="input-name"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email Address *</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="your.email@example.com"
                          {...field}
                          data-field="contact.email"
                          data-testid="input-email"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contact No.</FormLabel>
                      <FormControl>
                        <Input
                          type="tel"
                          placeholder="04XX XXX XXX"
                          {...field}
                          data-field="contact.phone"
                          data-testid="input-phone"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="state"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Your Location *</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger data-field="contact.state" data-testid="select-state">
                            <SelectValue placeholder="Select state" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {australianStates.map((state) => (
                            <SelectItem key={state.value} value={state.value}>
                              {state.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="subject"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Subject *</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Subject"
                          {...field}
                          data-field="contact.subject"
                          data-testid="input-subject"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Message *</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Your message / Suggestion"
                          className="min-h-[120px]"
                          {...field}
                          data-field="contact.message"
                          data-testid="input-message"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting}
                  data-action="contact.submit"
                  data-testid="button-submit"
                >
                  {isSubmitting ? "Sending..." : "Send Message"}
                </Button>
              </form>
            </Form>
          </div>
        </div>
      </div>
    </section>
  );
}
