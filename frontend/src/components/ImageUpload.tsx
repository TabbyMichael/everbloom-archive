import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Upload, Image as ImageIcon, Loader2 } from "lucide-react";
import { galleryApi } from "@/services/api";

interface ImageUploadProps {
  onImageAdd: (image: { url: string; title?: string; description?: string }) => void;
  onMultipleImagesAdd?: (images: { url: string; title?: string; description?: string }[]) => void;
}

const ImageUpload = ({ onImageAdd, onMultipleImagesAdd }: ImageUploadProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [preview, setPreview] = useState<string>("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [multiplePreviews, setMultiplePreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      if (files.length === 1) {
        // Single file selection
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreview(reader.result as string);
          setImageUrl(reader.result as string);
          setMultiplePreviews([]);
        };
        reader.readAsDataURL(files[0]);
      } else {
        // Multiple file selection
        const readers: Promise<string>[] = [];
        const previews: string[] = [];
        
        Array.from(files).forEach((file) => {
          const reader = new FileReader();
          readers.push(
            new Promise((resolve) => {
              reader.onloadend = () => {
                const result = reader.result as string;
                previews.push(result);
                resolve(result);
              };
              reader.readAsDataURL(file);
            })
          );
        });
        
        Promise.all(readers).then(() => {
          setMultiplePreviews(previews);
          setPreview("");
          setImageUrl("");
        });
      }
    }
  };

  const handleUpload = async () => {
    if (!fileInputRef.current?.files?.length) return;

    const files = Array.from(fileInputRef.current.files);
    
    try {
      setUploading(true);
      setUploadProgress(0);

      if (files.length === 1) {
        // Single file upload
        const formData = new FormData();
        formData.append('file', files[0]);
        formData.append('title', title);
        formData.append('description', description);
        formData.append('caption', description);
        formData.append('is_featured', 'false');
        formData.append('media_type', 'image');

        const uploadedImage = await galleryApi.create(formData);
        
        // Update local state
        onImageAdd({
          url: uploadedImage.media_url.startsWith('http') 
            ? uploadedImage.media_url 
            : `/api${uploadedImage.media_url}`,
          title: uploadedImage.title,
          description: uploadedImage.description
        });
        
        // Reset form
        resetForm();
        setIsOpen(false);
      } else {
        // Multiple file upload
        const uploadPromises = files.map(async (file, index) => {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('title', `${title || 'Image'} ${index + 1}`);
          formData.append('caption', description);
          formData.append('is_featured', 'false');
          formData.append('media_type', 'image');

          return await galleryApi.create(formData);
        });

        const uploadedImages = await Promise.all(uploadPromises);
        
        // Update local state
        const newImages = uploadedImages.map(img => ({
          url: img.media_url.startsWith('http') ? img.media_url : `/api${img.media_url}`,
          title: img.title,
          description: img.description
        }));
        
        if (onMultipleImagesAdd) {
          onMultipleImagesAdd(newImages);
        }
        
        // Reset form
        resetForm();
        setIsOpen(false);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload image. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const resetForm = () => {
    setPreview("");
    setTitle("");
    setDescription("");
    setImageUrl("");
    setMultiplePreviews([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleUrlSubmit = () => {
    if (imageUrl.trim()) {
      onImageAdd({
        url: imageUrl,
        title: title || "Uploaded Image",
        description: description
      });
      resetForm();
      setIsOpen(false);
    }
  };

  const handleUrlChange = (url: string) => {
    setImageUrl(url);
    setPreview(url);
    setMultiplePreviews([]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (multiplePreviews.length > 0) {
      // Add multiple images
      const images = multiplePreviews.map((url) => ({
        url,
        title: title.trim() || undefined,
        description: description.trim() || undefined,
      }));
      
      if (onMultipleImagesAdd) {
        onMultipleImagesAdd(images);
      } else {
        // Fallback: add images one by one
        images.forEach((image) => onImageAdd(image));
      }
      handleClose();
    } else if (imageUrl) {
      // Add single image
      onImageAdd({
        url: imageUrl,
        title: title.trim() || undefined,
        description: description.trim() || undefined,
      });
      handleClose();
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setPreview("");
    setTitle("");
    setDescription("");
    setImageUrl("");
    setMultiplePreviews([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="bg-blue-600 hover:bg-blue-700 text-white">
          <Upload className="w-4 h-4 mr-2" />
          Add Photo
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Photo to Gallery</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="image-upload">Choose Image</Label>
            <div className="grid grid-cols-1 gap-3">
              <div>
                <Label htmlFor="file-input" className="text-sm text-gray-600">
                  Upload from device
                </Label>
                <input
                  id="file-input"
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-500">Or</span>
                </div>
              </div>
              
              <div>
                <Label htmlFor="url-input" className="text-sm text-gray-600">
                  Image URL
                </Label>
                <Input
                  id="url-input"
                  type="url"
                  placeholder="https://example.com/image.jpg"
                  value={imageUrl}
                  onChange={(e) => handleUrlChange(e.target.value)}
                />
              </div>
            </div>
          </div>

          {preview && (
            <div className="space-y-2">
              <Label>Preview</Label>
              <div className="relative aspect-video w-full overflow-hidden rounded-lg border">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-full object-cover"
                  onError={() => {
                    setPreview("");
                    setImageUrl("");
                  }}
                />
              </div>
            </div>
          )}

          {multiplePreviews.length > 0 && (
            <div className="space-y-2">
              <Label>Preview ({multiplePreviews.length} images)</Label>
              <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto">
                {multiplePreviews.map((preview, index) => (
                  <div key={index} className="relative aspect-square overflow-hidden rounded-lg border">
                    <img
                      src={preview}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="title">Title (optional)</Label>
            <Input
              id="title"
              placeholder="Enter photo title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Textarea
              id="description"
              placeholder="Enter photo description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={!preview && multiplePreviews.length === 0}>
              {multiplePreviews.length > 0 
                ? `Add ${multiplePreviews.length} Photos to Gallery` 
                : 'Add to Gallery'
              }
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ImageUpload;
