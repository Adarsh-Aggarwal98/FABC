import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Mail, Linkedin } from "lucide-react";
import sharatImage from "@/images/sharat.jpeg";
import deepImage from "@/images/Deep.jpeg";
import adityaImage from "@/images/Aditya.png";
import yateenImage from "@/images/Yateen.jpeg";

const teamMembers = [
  {
    name: "Yateender Gupta",
    role: "Director, FCPA",
    bio: "Yateender Gupta, FCPA and Director, is a recognised SMSF expert with more than 25 years of experience advising clients across Australia in Self-Managed Superannuation Funds space. He specialises in advising on SMSF compliance, SMSF tax planning strategies and relevant business structures, supporting individuals and SMEs in diverse sectors including real estate, healthcare, NDIS, aged care, and manufacturing. Yateender’s reputation for clear guidance and tailored solutions makes him a trusted and thought leader in SMSF management and compliance.",
    email: "Yateen@aussupersource.com.au",
    image: yateenImage,
  },
  {
    name: "Sharat Sharma",
    role: "Partner, CPA, SMSF Auditor",
    bio: "With nearly 15+ years of experience in Audit & Risk Advisory space including Self-Managed Superannuation Fund (SMSF) compliance and advisory services, Sam is committed in expanding SMSF awareness and expertise. Sam is our Victoria partner based in Melbourne and specialises in providing tailored SMSF compliance support and strategic advice to accountants, financial planners, investment advisers, real estate professionals, mortgage brokers, and individual trustees. Sam’s goal is to simplify SMSF management, ensuring clients navigate regulatory requirements confidently while maximising their fund’s potential.",
    email: "sam@aussupersource.com.au",
    image: sharatImage,
  },
  {
 


    name: "Deependra Kumawat",
    role: "Partner, ICAI",
    bio: "Deep is our Adelaide (SA) Partner, specializing in SMSF Auditing and a wide range of SMSF compliance services. As a Chartered Accountant, he is dedicated to delivering high-quality compliance support while helping clients develop and maintain a clear strategic vision for their self-managed superannuation funds.",
    email: "deep@aussupersource.com.au",
    image: deepImage,
  },
  {
    name: "Aditya Wadhwa",
    role: "SMSF Consultant",
    bio: "Aditya is one of our senior SMSF Specialists who specializes in all SMSF related compliances including accounting, tax and audit matters.",
    email: "aditya@aussupersource.com.au",
    image: adityaImage,
  },
];

export default function TeamSection() {
  return (
    <section id="team" className="py-20 md:py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Our Experts
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
           
Our team of SMSF specialists blends technical expertise with a personal touch to every solution. We partner with accountants, advisers, mortgage brokers, lawyers, real estate professionals and individual trustees nationwide to simplify compliance, strengthen strategy, and help every SMSF reach its full potential.

          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto" data-list="team-members">
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              data-entity-type="team-member"
              data-entity-id={index.toString()}
            >
              <Card
                className="p-8 h-full hover-elevate transition-all duration-300"
                data-testid={`team-member-${index}`}
              >
                <div className="flex flex-col items-center text-center mb-6">
                  <div className="relative mb-4">
                    <img
                      src={member.image}
                      alt={member.name}
                      className="w-32 h-32 rounded-full object-cover border-4 border-primary/10"
                    />
                    <div className="absolute bottom-0 right-0 w-10 h-10 bg-primary rounded-full flex items-center justify-center border-4 border-background">
                      <Linkedin className="h-5 w-5 text-primary-foreground" />
                    </div>
                  </div>
                  <h3 className="text-2xl font-semibold mb-1" data-col="name">{member.name}</h3>
                  <p className="text-primary font-medium text-sm mb-2" data-col="role">{member.role}</p>
                </div>
                <p className="text-muted-foreground leading-relaxed mb-6 text-sm" data-col="bio">
                  {member.bio}
                </p>
                <a
                  href={`mailto:${member.email}`}
                  className="inline-flex items-center gap-2 text-primary hover:underline text-sm font-medium"
                  data-col="email"
                >
                  <Mail className="h-4 w-4" />
                  {member.email}
                </a>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
