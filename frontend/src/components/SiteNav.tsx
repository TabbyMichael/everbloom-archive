import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Moon, Sun, Globe, Images } from "lucide-react";
import { useLocale, useTheme } from "@/contexts/AppProviders";
import { useTranslations } from "@/hooks/useTranslations";
import { Link, useLocation } from "react-router-dom";

const SiteNav = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { locale, setLocale } = useLocale();
  const { theme, toggleTheme } = useTheme();
  const t = useTranslations();
  const location = useLocation();

  const links = [
    { label: t.nav.story, href: "#story" },
    { label: t.nav.timeline, href: "#timeline" },
    { label: t.nav.tributes, href: "#tributes" },
    { label: t.nav.lightCandle, href: "#candle" },
  ];

  const handleGalleryClick = () => {
    if (location.pathname === "/") {
      // On homepage, scroll to gallery section
      const galleryElement = document.getElementById("gallery");
      if (galleryElement) {
        galleryElement.scrollIntoView({ behavior: "smooth" });
      }
    } else {
      // On other pages, navigate to gallery page
      window.location.href = "/gallery";
    }
  };

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-background/90 backdrop-blur-md shadow-sm border-b border-border"
          : "bg-transparent"
      }`}
    >
      <div className="container mx-auto px-6 flex items-center justify-between h-16">
        <Link to="/" className="font-serif text-lg text-foreground">
          In Loving Memory
        </Link>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-6">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="font-sans text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {link.label}
            </a>
          ))}
          
          {/* Gallery Button */}
          <button
            onClick={handleGalleryClick}
            className="font-sans text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
          >
            <Images className="w-4 h-4" />
            Gallery
          </button>

          <div className="flex items-center gap-2 ml-4 pl-4 border-l border-border">
            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            {/* Language toggle */}
            <button
              onClick={() => setLocale(locale === "en" ? "sw" : "en")}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-sans font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            >
              <Globe className="w-3.5 h-3.5" />
              {locale === "en" ? "SW" : "EN"}
            </button>
          </div>
        </div>

        {/* Mobile controls */}
        <div className="flex md:hidden items-center gap-2">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full text-muted-foreground hover:text-foreground transition-colors"
          >
            {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setLocale(locale === "en" ? "sw" : "en")}
            className="px-2 py-1 rounded-full text-xs font-sans font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            {locale === "en" ? "SW" : "EN"}
          </button>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="text-foreground"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-background/95 backdrop-blur-md border-b border-border"
          >
            <div className="container mx-auto px-6 py-4 flex flex-col gap-3">
              {links.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="font-sans text-sm text-muted-foreground hover:text-foreground py-2"
                >
                  {link.label}
                </a>
              ))}
              
              {/* Gallery Button */}
              <button
                onClick={() => {
                  handleGalleryClick();
                  setMobileOpen(false);
                }}
                className="font-sans text-sm text-muted-foreground hover:text-foreground py-2 flex items-center gap-2 text-left"
              >
                <Images className="w-4 h-4" />
                Gallery
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default SiteNav;
