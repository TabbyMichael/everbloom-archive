import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import childhoodImg from "@/assets/timeline-childhood.jpg";
import familyImg from "@/assets/timeline-family.jpg";
import gardenImg from "@/assets/timeline-garden.jpg";

interface Milestone {
  year: string;
  title: string;
  description: string;
  image: string;
  mood: "bright" | "warm" | "serene";
}

const milestones: Milestone[] = [
  {
    year: "Early Years",
    title: "A Childhood in the Highlands",
    description:
      "Born into the rolling green hills, Mary grew up surrounded by the beauty of nature. Her love for the land and its people began here — a foundation that would shape everything she became.",
    image: childhoodImg,
    mood: "bright",
  },
  {
    year: "Family Years",
    title: "The Heart of the Home",
    description:
      "Mary built a family rooted in love, laughter, and togetherness. Her table was never empty, her door never closed. Every gathering was a celebration, and she was always at the center — the warmth everyone gravitated toward.",
    image: familyImg,
    mood: "warm",
  },
  {
    year: "Later Years",
    title: "A Garden of Grace",
    description:
      "In her quieter years, Mary found peace in her garden and in the gentle rhythm of each day. She tended her flowers with the same care she gave to everyone around her — patiently, lovingly, beautifully.",
    image: gardenImg,
    mood: "serene",
  },
];

const TimelineItem = ({ milestone, index }: { milestone: Milestone; index: number }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const isEven = index % 2 === 0;

  return (
    <div ref={ref} className="relative flex items-center mb-24 last:mb-0">
      {/* Center dot */}
      <div className="absolute left-1/2 -translate-x-1/2 z-10">
        <motion.div
          initial={{ scale: 0 }}
          animate={isInView ? { scale: 1 } : {}}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-4 h-4 rounded-full bg-primary border-4 border-background shadow-md"
        />
      </div>

      {/* Content */}
      <div className={`w-full flex ${isEven ? "flex-row" : "flex-row-reverse"}`}>
        <motion.div
          initial={{ opacity: 0, x: isEven ? -60 : 60 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-5/12"
        >
          <div className="rounded-2xl overflow-hidden shadow-lg">
            <img
              src={milestone.image}
              alt={milestone.title}
              loading="lazy"
              width={1280}
              height={720}
              className="w-full h-48 md:h-64 object-cover"
            />
          </div>
        </motion.div>

        <div className="w-2/12" />

        <motion.div
          initial={{ opacity: 0, x: isEven ? 60 : -60 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="w-5/12 flex flex-col justify-center"
        >
          <span className="text-sm tracking-[0.2em] uppercase text-primary font-sans font-medium mb-2">
            {milestone.year}
          </span>
          <h3 className="text-2xl md:text-3xl font-serif font-medium text-foreground mb-3">
            {milestone.title}
          </h3>
          <p className="text-muted-foreground font-sans leading-relaxed text-sm md:text-base">
            {milestone.description}
          </p>
        </motion.div>
      </div>
    </div>
  );
};

// Mobile version
const TimelineItemMobile = ({ milestone, index }: { milestone: Milestone; index: number }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, delay: index * 0.1 }}
      className="relative pl-8 mb-16 last:mb-0"
    >
      {/* Left dot */}
      <div className="absolute left-0 top-2 w-3 h-3 rounded-full bg-primary border-3 border-background shadow" />

      <span className="text-xs tracking-[0.2em] uppercase text-primary font-sans font-medium mb-2 block">
        {milestone.year}
      </span>
      <h3 className="text-xl font-serif font-medium text-foreground mb-2">{milestone.title}</h3>
      <div className="rounded-xl overflow-hidden shadow-md mb-3">
        <img
          src={milestone.image}
          alt={milestone.title}
          loading="lazy"
          width={1280}
          height={720}
          className="w-full h-48 object-cover"
        />
      </div>
      <p className="text-muted-foreground font-sans leading-relaxed text-sm">{milestone.description}</p>
    </motion.div>
  );
};

const LifeTimeline = () => {
  return (
    <section className="py-24 bg-card" id="timeline">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <p className="text-sm tracking-[0.3em] uppercase text-primary font-sans mb-3">Her Journey</p>
          <h2 className="text-4xl md:text-5xl font-serif font-light text-foreground">
            A Life in Chapters
          </h2>
        </motion.div>

        {/* Desktop timeline */}
        <div className="relative hidden md:block max-w-5xl mx-auto">
          {/* Center line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px timeline-line" />
          {milestones.map((m, i) => (
            <TimelineItem key={i} milestone={m} index={i} />
          ))}
        </div>

        {/* Mobile timeline */}
        <div className="relative md:hidden">
          <div className="absolute left-[5px] top-0 bottom-0 w-px timeline-line" />
          {milestones.map((m, i) => (
            <TimelineItemMobile key={i} milestone={m} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default LifeTimeline;
