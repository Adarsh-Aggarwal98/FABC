import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, LogIn, User } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useAuth } from "@/contexts/AuthContext";
import logo from "@/images/AusSuperLogo.png";

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [location] = useLocation();
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const isHome = location === "/";

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <nav
      data-route="home"
      data-contract-version="1.0.0"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? "bg-white/95 backdrop-blur-md border-b" : isHome ? "bg-black/20 backdrop-blur-sm" : "bg-white/95 backdrop-blur-md border-b"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          <Link href="/">
            <img
              src={logo}
              alt="AusSuperSource Logo"
              className="h-12 md:h-16 w-auto transition-all duration-300 cursor-pointer hover:opacity-90"
            />
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link href="/">
              <button
                className={`text-sm font-medium hover-elevate px-3 py-2 rounded-md transition-colors ${
                  (isScrolled || !isHome) ? "" : "text-white"
                }`}
                data-nav-item="home"
                data-testid="link-home"
              >
                Home
              </button>
            </Link>
            <Link href="/about">
              <button
                className={`text-sm font-medium hover-elevate px-3 py-2 rounded-md transition-colors ${
                  (isScrolled || !isHome) ? "" : "text-white"
                }`}
                data-nav-item="about"
                data-testid="link-about"
              >
                About Us
              </button>
            </Link>
            <Link href="/services">
              <button
                className={`text-sm font-medium hover-elevate px-3 py-2 rounded-md transition-colors ${
                  (isScrolled || !isHome) ? "" : "text-white"
                }`}
                data-nav-item="services"
                data-testid="link-services"
              >
                Services
              </button>
            </Link>
            <Link href="/team">
              <button
                className={`text-sm font-medium hover-elevate px-3 py-2 rounded-md transition-colors ${
                  (isScrolled || !isHome) ? "" : "text-white"
                }`}
                data-nav-item="team"
                data-testid="link-team"
              >
                Our Team
              </button>
            </Link>
            <Link href="/blog">
              <button
                className={`text-sm font-medium hover-elevate px-3 py-2 rounded-md transition-colors ${
                  (isScrolled || !isHome) ? "" : "text-white"
                }`}
                data-nav-item="blog"
                data-testid="link-blog"
              >
                Blog
              </button>
            </Link>
            <Link href="/contact">
              <button
                className={`text-sm font-medium hover-elevate px-3 py-2 rounded-md transition-colors ${
                  (isScrolled || !isHome) ? "" : "text-white"
                }`}
                data-nav-item="contact"
                data-testid="link-contact"
              >
                Contact Us
              </button>
            </Link>

            {isAuthenticated ? (
              <Link href="/dashboard">
                <Button
                  variant={isScrolled || !isHome ? "default" : "secondary"}
                  size="sm"
                  className="ml-2"
                  data-testid="link-dashboard"
                >
                  <User className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
            ) : (
              <Link href="/login">
                <Button
                  variant={isScrolled || !isHome ? "default" : "secondary"}
                  size="sm"
                  className="ml-2"
                  data-testid="link-login"
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  Login
                </Button>
              </Link>
            )}
          </div>

          <div className="md:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className={(isScrolled || !isHome) ? "" : "text-white hover:text-white"}
              data-testid="button-mobile-menu"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden bg-background border-t">
          <div className="px-4 py-4 space-y-2">
            <Link href="/">
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="block w-full text-left px-3 py-2 rounded-md hover-elevate transition-colors"
                data-testid="link-home-mobile"
              >
                Home
              </button>
            </Link>
            <Link href="/about">
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="block w-full text-left px-3 py-2 rounded-md hover-elevate transition-colors"
                data-testid="link-about-mobile"
              >
                About Us
              </button>
            </Link>
            <Link href="/services">
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="block w-full text-left px-3 py-2 rounded-md hover-elevate transition-colors"
                data-testid="link-services-mobile"
              >
                Services
              </button>
            </Link>
            <Link href="/team">
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="block w-full text-left px-3 py-2 rounded-md hover-elevate transition-colors"
                data-testid="link-team-mobile"
              >
                Our Team
              </button>
            </Link>
            <Link href="/blog">
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="block w-full text-left px-3 py-2 rounded-md hover-elevate transition-colors"
                data-testid="link-blog-mobile"
              >
                Blog
              </button>
            </Link>
            <Link href="/contact">
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="block w-full text-left px-3 py-2 rounded-md hover-elevate transition-colors"
                data-testid="link-contact-mobile"
              >
                Contact Us
              </button>
            </Link>

            <div className="pt-2 border-t mt-2">
              {isAuthenticated ? (
                <Link href="/dashboard">
                  <Button
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="w-full"
                    data-testid="link-dashboard-mobile"
                  >
                    <User className="h-4 w-4 mr-2" />
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <Link href="/login">
                  <Button
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="w-full"
                    data-testid="link-login-mobile"
                  >
                    <LogIn className="h-4 w-4 mr-2" />
                    Login
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
