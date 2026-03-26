import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import { Heart, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useTranslations } from "@/hooks/useTranslations";

interface Tribute {
  id: number;
  name: string;
  relationshipKey: "granddaughter" | "son" | "neighbor" | "grandson";
  message: string;
  date: string;
}

const sampleTributes: Tribute[] = [
  { id: 1, name: "Grace Muthoni", relationshipKey: "granddaughter", message: "Cucu, your laughter was the soundtrack of my childhood. Every Sunday at your house was a gift. I carry your warmth with me always.", date: "March 2026" },
  { id: 2, name: "James Kamau", relationshipKey: "son", message: "Mama, you taught me that strength is quiet and love is loud. Everything good in me came from you. Rest well.", date: "March 2026" },
  { id: 3, name: "Sarah Njeri", relationshipKey: "neighbor", message: "Mary was the kind of person who made you feel like family from the first cup of chai. Her garden gate was always open, and so was her heart.", date: "March 2026" },
  { id: 4, name: "Peter Wainaina", relationshipKey: "grandson", message: "Cucu taught me how to plant seeds — both in the soil and in life. I will keep tending the garden she started.", date: "March 2026" },
];

const TributeCard = ({ tribute, index, relationship }: { tribute: Tribute; index: number; relationship: string }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <motion.div ref={ref} initial={{ opacity: 0, y: 30 }} animate={isInView ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.6, delay: index * 0.1 }} className="bg-background/80 backdrop-blur-sm rounded-2xl p-6 shadow-sm border border-border hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-accent flex items-center justify-center text-accent-foreground font-serif text-lg">{tribute.name[0]}</div>
        <div>
          <p className="font-sans font-medium text-foreground text-sm">{tribute.name}</p>
          <p className="font-sans text-xs text-muted-foreground">{relationship}</p>
        </div>
      </div>
      <p className="font-serif text-foreground/90 leading-relaxed italic text-base mb-4">&ldquo;{tribute.message}&rdquo;</p>
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground font-sans">{tribute.date}</span>
        <Heart className="w-4 h-4 text-primary/40" />
      </div>
    </motion.div>
  );
};

const TributeWall = () => {
  const t = useTranslations();
  const [name, setName] = useState("");
  const [relationship, setRelationship] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !message.trim()) return;
    toast.success(t.tributes.successToast);
    setName("");
    setRelationship("");
    setMessage("");
  };

  return (
    <section className="py-24 living-background" id="tributes">
      <div className="container mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <p className="text-sm tracking-[0.3em] uppercase text-primary font-sans mb-3">{t.tributes.label}</p>
          <h2 className="text-4xl md:text-5xl font-serif font-light text-foreground">{t.tributes.title}</h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-16">
          {sampleTributes.map((tribute, i) => (
            <TributeCard key={tribute.id} tribute={tribute} index={i} relationship={t.tributes.relationships[tribute.relationshipKey]} />
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="max-w-lg mx-auto">
          <div className="bg-background/80 backdrop-blur-sm rounded-2xl p-8 shadow-sm border border-border">
            <h3 className="text-xl font-serif text-foreground mb-6 text-center">{t.tributes.shareTitle}</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input type="text" placeholder={t.tributes.namePlaceholder} value={name} onChange={(e) => setName(e.target.value)} maxLength={100} className="w-full px-4 py-3 rounded-lg bg-muted border border-border text-foreground font-sans text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30" />
              <input type="text" placeholder={t.tributes.relationshipPlaceholder} value={relationship} onChange={(e) => setRelationship(e.target.value)} maxLength={100} className="w-full px-4 py-3 rounded-lg bg-muted border border-border text-foreground font-sans text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30" />
              <textarea placeholder={t.tributes.messagePlaceholder} value={message} onChange={(e) => setMessage(e.target.value)} maxLength={1000} rows={4} className="w-full px-4 py-3 rounded-lg bg-muted border border-border text-foreground font-sans text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none" />
              <Button type="submit" className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-sans">
                <Send className="w-4 h-4 mr-2" />
                {t.tributes.submitButton}
              </Button>
            </form>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default TributeWall;
