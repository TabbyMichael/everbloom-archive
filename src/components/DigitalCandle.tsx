import { motion } from "framer-motion";
import { useState } from "react";
import { toast } from "sonner";

const DigitalCandle = () => {
  const [candleCount, setCandleCount] = useState(47);
  const [hasLit, setHasLit] = useState(false);

  const lightCandle = () => {
    if (hasLit) return;
    setCandleCount((c) => c + 1);
    setHasLit(true);
    toast.success("Your candle has been lit for Mary. Thank you. 🕯️");
  };

  return (
    <section className="py-20 bg-foreground text-primary-foreground" id="candle">
      <div className="container mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-md mx-auto"
        >
          <div className="candle-glow text-6xl mb-6">🕯️</div>
          <h2 className="text-3xl md:text-4xl font-serif font-light mb-4">
            Light a Candle
          </h2>
          <p className="text-primary-foreground/70 font-sans text-sm mb-8">
            {candleCount} candles have been lit in memory of Mary Wangui
          </p>

          <button
            onClick={lightCandle}
            disabled={hasLit}
            className={`px-8 py-3 rounded-full font-sans text-sm tracking-wide transition-all ${
              hasLit
                ? "bg-primary-foreground/20 text-primary-foreground/50 cursor-default"
                : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg hover:shadow-xl"
            }`}
          >
            {hasLit ? "Your candle is burning ✨" : "Light a Candle"}
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default DigitalCandle;
