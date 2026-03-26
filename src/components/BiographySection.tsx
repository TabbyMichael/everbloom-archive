import { motion } from "framer-motion";

const BiographySection = () => {
  return (
    <section className="py-24 bg-background" id="story">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <p className="text-sm tracking-[0.3em] uppercase text-primary font-sans mb-3">Her Story</p>
          <h2 className="text-4xl md:text-5xl font-serif font-light text-foreground">
            In Her Own Words
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-3xl mx-auto"
        >
          <div className="bg-card rounded-2xl p-8 md:p-12 shadow-sm border border-border">
            <blockquote className="font-serif text-xl md:text-2xl text-foreground/90 leading-relaxed italic mb-8 text-center">
              &ldquo;The best thing I ever planted was not in my garden — it was love in my children&rsquo;s hearts.&rdquo;
            </blockquote>

            <div className="w-16 h-px bg-primary/30 mx-auto mb-8" />

            <div className="space-y-6 font-sans text-muted-foreground leading-relaxed text-base">
              <p>
                Mary Wangui was a woman of quiet strength and boundless generosity. Born in the
                highlands of Central Kenya, she grew up learning the rhythms of the land — when to
                plant, when to harvest, and when to simply be still and listen.
              </p>
              <p>
                She married young and built a home that became the heart of her community. Her
                kitchen was never empty, and her counsel was sought by neighbors and strangers alike.
                She had a gift for making everyone feel seen, heard, and valued.
              </p>
              <p>
                In her later years, Mary found deep joy in her garden, her grandchildren, and the
                simple beauty of each new morning. She believed that every day was a gift, and she
                lived accordingly — with grace, with purpose, and with an unshakeable faith that
                love is the only thing that truly endures.
              </p>
            </div>

            <div className="mt-10 flex items-center justify-center gap-3">
              <div className="w-2 h-2 rounded-full bg-rose-light" />
              <div className="w-2 h-2 rounded-full bg-dusty-blue" />
              <div className="w-2 h-2 rounded-full bg-gold-soft" />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default BiographySection;
