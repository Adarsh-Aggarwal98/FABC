import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight, Calendar, Clock, User, Tag, Loader2 } from "lucide-react";
import { Link } from "wouter";
import { fetchBlogs, type Blog } from "@/lib/api";

// Fallback blogs in case API is unavailable
const fallbackBlogs: Blog[] = [
  {
    id: "1",
    title: "2024 SMSF Compliance Changes: What Accountants Need to Know",
    slug: "2024-smsf-compliance-changes",
    excerpt: "Stay ahead of the latest regulatory updates affecting SMSF audits. Key changes to contribution caps, pension requirements, and reporting obligations.",
    content: null,
    category: "Compliance",
    author: "Yateender Gupta",
    readTime: "5 min read",
    image: "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=600&h=400&fit=crop",
    featured: true,
    published: true,
    createdAt: "2024-12-15",
    updatedAt: null,
  },
  {
    id: "2",
    title: "Partner Auditing: How to Scale Your SMSF Practice",
    slug: "partner-auditing-scale-practice",
    excerpt: "Discover how partnering with an audit provider can help you take on more clients without increasing overhead costs.",
    content: null,
    category: "Practice Growth",
    author: "Sharat Sharma",
    readTime: "4 min read",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop",
    featured: false,
    published: true,
    createdAt: "2024-12-10",
    updatedAt: null,
  },
  {
    id: "3",
    title: "Common SMSF Audit Findings and How to Avoid Them",
    slug: "common-smsf-audit-findings",
    excerpt: "Learn about the most frequent compliance issues we encounter during audits and practical steps to prevent them in your client's funds.",
    content: null,
    category: "Audit Insights",
    author: "Deependra Kumawat",
    readTime: "6 min read",
    image: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=600&h=400&fit=crop",
    featured: false,
    published: true,
    createdAt: "2024-12-05",
    updatedAt: null,
  },
  {
    id: "4",
    title: "SMSF Property Investment: Documentation Requirements",
    slug: "smsf-property-investment-documentation",
    excerpt: "A comprehensive guide to the documentation requirements for SMSF property investments, including limited recourse borrowing arrangements.",
    content: null,
    category: "Documentation",
    author: "Aditya Wadhwa",
    readTime: "7 min read",
    image: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&h=400&fit=crop",
    featured: false,
    published: true,
    createdAt: "2024-11-28",
    updatedAt: null,
  },
];

function formatDate(dateString: string | null): string {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-AU", { month: "short", day: "numeric", year: "numeric" });
}

export default function BlogsSection() {
  const [blogs, setBlogs] = useState<Blog[]>(fallbackBlogs);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadBlogs = async () => {
      try {
        const data = await fetchBlogs();
        if (data.length > 0) {
          setBlogs(data);
        }
      } catch (error) {
        console.error("Failed to load blogs:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadBlogs();
  }, []);

  const featuredBlog = blogs.find(blog => blog.featured);
  const regularBlogs = blogs.filter(blog => !blog.featured).slice(0, 3);

  return (
    <section className="py-20 md:py-24 lg:py-32 bg-gradient-to-br from-slate-50 via-white to-blue-50/30 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-100/40 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-100/40 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 relative">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <motion.span
            className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            Insights & Resources
          </motion.span>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Latest from Our{" "}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              SMSF Blog
            </span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Expert insights, compliance updates, and practical tips to help accountants
            deliver exceptional SMSF services.
          </p>
        </motion.div>

        {/* Blog Grid */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Featured Blog */}
          {featuredBlog && (
            <motion.div
              className="lg:row-span-2"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <Card className="h-full overflow-hidden group cursor-pointer hover:shadow-2xl transition-all duration-500">
                <div className="relative h-64 lg:h-80 overflow-hidden">
                  <img
                    src={featuredBlog.image}
                    alt={featuredBlog.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                  <div className="absolute top-4 left-4">
                    <span className="px-3 py-1 bg-primary text-white text-xs font-semibold rounded-full">
                      Featured
                    </span>
                  </div>
                  <div className="absolute bottom-4 left-4 right-4">
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-white/20 backdrop-blur-sm text-white text-xs rounded-full mb-2">
                      <Tag className="h-3 w-3" />
                      {featuredBlog.category}
                    </span>
                  </div>
                </div>
                <div className="p-6 lg:p-8">
                  <h3 className="text-xl lg:text-2xl font-bold mb-3 group-hover:text-primary transition-colors line-clamp-2">
                    {featuredBlog.title}
                  </h3>
                  <p className="text-muted-foreground mb-4 line-clamp-3">
                    {featuredBlog.excerpt}
                  </p>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {featuredBlog.author}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(featuredBlog.createdAt)}
                      </span>
                    </div>
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {featuredBlog.readTime}
                    </span>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Regular Blogs */}
          <div className="space-y-6">
            {regularBlogs.map((blog, index) => (
              <motion.div
                key={blog.id}
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="overflow-hidden group cursor-pointer hover:shadow-lg transition-all duration-300">
                  <div className="flex flex-col sm:flex-row">
                    <div className="relative w-full sm:w-48 h-48 sm:h-auto flex-shrink-0 overflow-hidden">
                      <img
                        src={blog.image}
                        alt={blog.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/20 sm:bg-gradient-to-t" />
                    </div>
                    <div className="p-5 flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary text-xs font-medium rounded-full">
                          <Tag className="h-3 w-3" />
                          {blog.category}
                        </span>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {blog.readTime}
                        </span>
                      </div>
                      <h3 className="font-bold mb-2 group-hover:text-primary transition-colors line-clamp-2">
                        {blog.title}
                      </h3>
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                        {blog.excerpt}
                      </p>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {blog.author}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(blog.createdAt)}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* View All Button */}
        <motion.div
          className="text-center mt-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Button
            size="lg"
            variant="outline"
            className="group border-primary/30 hover:border-primary hover:bg-primary/5"
          >
            View All Articles
            <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
