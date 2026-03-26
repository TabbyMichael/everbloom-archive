const Footer = () => {
  return (
    <footer className="py-12 bg-card border-t border-border">
      <div className="container mx-auto px-6 text-center">
        <p className="font-serif text-2xl text-foreground mb-2">Mary Wangui</p>
        <p className="font-sans text-sm text-muted-foreground mb-6">
          Forever in our hearts
        </p>
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="w-1.5 h-1.5 rounded-full bg-rose-light" />
          <div className="w-1.5 h-1.5 rounded-full bg-dusty-blue" />
          <div className="w-1.5 h-1.5 rounded-full bg-gold-soft" />
        </div>
        <p className="font-sans text-xs text-muted-foreground/60">
          Made with love by her family
        </p>
      </div>
    </footer>
  );
};

export default Footer;
