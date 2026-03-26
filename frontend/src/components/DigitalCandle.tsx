import { motion } from "framer-motion";
import { useState } from "react";
import { toast } from "sonner";
import { useTranslations } from "@/hooks/useTranslations";

const DigitalCandle = () => {
  const t = useTranslations();
  const [candleCount, setCandleCount] = useState(47);
  const [hasLit, setHasLit] = useState(false);

  const lightCandle = () => {
    if (hasLit) return;
    setCandleCount((c) => c + 1);
    setHasLit(true);
    toast.success(t.candle.toast);
  };

  return (
    <section className="py-20 bg-[hsl(var(--candle-bg))] text-[hsl(var(--candle-fg))]" id="candle">
      <div className="container mx-auto px-6 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="max-w-md mx-auto">
          <div className="candle-glow text-6xl mb-6">🕯️</div>
          <h2 className="text-3xl md:text-4xl font-serif font-light mb-4">{t.candle.title}</h2>
          <p className="opacity-70 font-sans text-sm mb-8">{candleCount} {t.candle.count}</p>
          <button
            onClick={lightCandle}
            disabled={hasLit}
            className={`px-8 py-3 rounded-full font-sans text-sm tracking-wide transition-all ${
              hasLit
                ? "bg-[hsl(var(--candle-fg))]/20 opacity-50 cursor-default"
                : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg hover:shadow-xl"
            }`}
          >
            {hasLit ? t.candle.lit : t.candle.button}
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default DigitalCandle;
