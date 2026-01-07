import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Star } from "lucide-react";

const testimonials = [
  {
    name: "Emma Wadee",
    role: "Business Owner",
    rating: 5,
    comment: "This is the first time I've used AusSuperSource and I was very impressed with the service they provided. I found the team to be friendly and professional; always willing to go the extra mile to help me with my SMSF concerns.",
    avatar: "https://i.pravatar.cc/400?img=47"
  },
  {
    name: "David Chen",
    role: "Financial Advisor",
    rating: 5,
    comment: "I recently used AusSuperSource for SMSF auditing and compliance, and I was pleasantly surprised by how fast, easy, and convenient the whole process was. The team made it incredibly straightforward and professional.",
    avatar: "https://i.pravatar.cc/400?img=13"
  },
  {
    name: "Rachel Sparkes",
    role: "Accountant",
    rating: 5,
    comment: "Had a great experience with AusSuperSource. They are forward thinking and automate much of the process without feeling like security is being compromised. I enjoyed the transparency of their costs for services.",
    avatar: "https://i.pravatar.cc/400?img=45"
  },
  {
    name: "Michael Brown",
    role: "SMSF Trustee",
    rating: 5,
    comment: "It has been a great experience getting my SMSF audit and compliance done through AusSuperSource over the past few years. They are secure, attend to needs and provide correct and legitimate consultation.",
    avatar: "https://i.pravatar.cc/400?img=12"
  },
  {
    name: "Sarah Mitchell",
    role: "Business Owner",
    rating: 5,
    comment: "I had an excellent experience with AusSuperSource for my SMSF audit and compliance. The team provided professional, knowledgeable, and efficient service, making the process seamless and stress-free. Highly recommended.",
    avatar: "https://i.pravatar.cc/400?img=48"
  },
  {
    name: "James Wilson",
    role: "Financial Planner",
    rating: 5,
    comment: "Outstanding service from start to finish. AusSuperSource handled our firm's SMSF audit and compliance needs with precision and care. Their expertise in compliance is second to none.",
    avatar: "https://i.pravatar.cc/400?img=33"
  }
];

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-1 mb-3">
      {[...Array(5)].map((_, i) => (
        <Star
          key={i}
          className={`h-4 w-4 ${
            i < rating ? "fill-primary text-primary" : "text-muted-foreground/30"
          }`}
        />
      ))}
    </div>
  );
}

export default function Testimonials() {
  return (
    <section className="py-20 md:py-24 lg:py-32 bg-muted">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            What Our Clients Say
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            From first-time trustees to established advisors, our clients love how professional, 
            fast, and stress-free we make SMSF management
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="p-6 h-full flex flex-col hover-elevate transition-all duration-300">
                <StarRating rating={testimonial.rating} />
                
                <p className="text-muted-foreground mb-6 flex-grow leading-relaxed">
                  "{testimonial.comment}"
                </p>

                <div className="flex items-center gap-3">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="text-center mt-12"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="inline-flex items-center gap-2 text-lg font-medium">
            <Star className="h-5 w-5 fill-primary text-primary" />
            <span className="text-2xl font-bold">5.0</span>
            <span className="text-muted-foreground">rated by hundreds of satisfied clients</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
