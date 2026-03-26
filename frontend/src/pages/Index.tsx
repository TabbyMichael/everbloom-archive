import SiteNav from "@/components/SiteNav";
import HeroSection from "@/components/HeroSection";
import BiographySection from "@/components/BiographySection";
import Timeline from "@/components/Timeline";
import TributesWall from "@/components/TributesWall";
import GallerySection from "@/components/GallerySection";
import DigitalCandle from "@/components/DigitalCandle";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <SiteNav />
      <HeroSection />
      <BiographySection />
      <Timeline />
      <TributesWall />
      <GallerySection />
      <DigitalCandle />
      <Footer />
    </div>
  );
};

export default Index;
