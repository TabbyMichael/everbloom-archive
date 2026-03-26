import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, X, ZoomIn } from "lucide-react";
import ImageUpload from "@/components/ImageUpload";
import { galleryApi, Gallery } from "@/services/api";

interface GalleryImage {
  id: string;
  url: string;
  title?: string;
  description?: string;
  uploadedAt: Date;
}

const GallerySection = () => {
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGallery();
  }, []);

  const loadGallery = async () => {
    try {
      setLoading(true);
      const galleryItems = await galleryApi.getAll();
      
      const galleryImages: GalleryImage[] = galleryItems.map(item => ({
        id: item.id,
        url: item.media_url.startsWith('http') ? item.media_url : `/api${item.media_url}`,
        title: item.title,
        description: item.description,
        uploadedAt: new Date(item.created_at),
      }));
      
      setImages(galleryImages);
    } catch (error) {
      console.error('Failed to load gallery:', error);
      // Keep sample images as fallback
      setImages([
        {
          id: "1",
          url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
          title: "Mountain Sunrise",
          description: "A beautiful sunrise over the mountains",
          uploadedAt: new Date("2024-01-15"),
        },
        {
          id: "2", 
          url: "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800&h=600&fit=crop",
          title: "Ocean Waves",
          description: "Peaceful waves at sunset",
          uploadedAt: new Date("2024-01-20"),
        },
        {
          id: "3",
          url: "https://images.unsplash.com/photo-1519904981063-b0cf448d479e?w=800&h=600&fit=crop", 
          title: "Forest Path",
          description: "A serene path through the forest",
          uploadedAt: new Date("2024-01-25"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleImageAdd = async (newImage: Omit<GalleryImage, "id" | "uploadedAt">) => {
    try {
      // For now, just add to local state
      // In a real implementation, you'd upload via the API
      const image: GalleryImage = {
        ...newImage,
        id: Date.now().toString(),
        uploadedAt: new Date(),
      };
      setImages((prev) => [...prev, image]);
    } catch (error) {
      console.error('Failed to add image:', error);
    }
  };

  const handleMultipleImagesAdd = (newImages: Omit<GalleryImage, "id" | "uploadedAt">[]) => {
    const images: GalleryImage[] = newImages.map((img, index) => ({
      ...img,
      id: `${Date.now()}-${index}`,
      uploadedAt: new Date(),
    }));
    setImages((prev) => [...prev, ...images]);
  };

  const handleImageDelete = (id: string) => {
    setImages((prev) => prev.filter((img) => img.id !== id));
  };

  if (loading) {
    return (
      <section id="gallery" className="py-16 px-4 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <Upload className="w-8 h-8 text-gray-400 animate-pulse" />
            </div>
            <p className="text-gray-500 text-lg">Loading gallery...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="gallery" className="py-16 px-4 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Photo Gallery
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Share and cherish memories through photographs that capture special moments
          </p>
        </div>

        <div className="mb-8 flex justify-center">
          <ImageUpload onImageAdd={handleImageAdd} onMultipleImagesAdd={handleMultipleImagesAdd} />
        </div>

        {images.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500 text-lg">No photos yet</p>
            <p className="text-gray-400 mt-2">Be the first to add a photo to the gallery</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {images.map((image) => (
              <Card key={image.id} className="group overflow-hidden hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-0 relative">
                  <Dialog>
                    <DialogTrigger asChild>
                      <div className="relative aspect-square cursor-pointer">
                        <img
                          src={image.url}
                          alt={image.title || "Gallery image"}
                          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity duration-300 flex items-center justify-center">
                          <ZoomIn className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        </div>
                      </div>
                    </DialogTrigger>
                    <DialogContent className="max-w-4xl">
                      <div className="relative">
                        <img
                          src={image.url}
                          alt={image.title || "Gallery image"}
                          className="w-full h-auto max-h-[70vh] object-contain"
                        />
                        {image.title && (
                          <div className="mt-4 text-center">
                            <h3 className="text-xl font-semibold">{image.title}</h3>
                            {image.description && (
                              <p className="text-gray-600 mt-2">{image.description}</p>
                            )}
                            <p className="text-sm text-gray-400 mt-2">
                              Added on {image.uploadedAt.toLocaleDateString()}
                            </p>
                          </div>
                        )}
                      </div>
                    </DialogContent>
                  </Dialog>
                  
                  <Button
                    variant="destructive"
                    size="sm"
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleImageDelete(image.id);
                    }}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                  
                  {image.title && (
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                      <p className="text-white text-sm font-medium truncate">{image.title}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default GallerySection;
