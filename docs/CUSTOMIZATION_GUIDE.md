# Everbloom Archive - Customization Guide

## 🎨 Personalize Your Memorial Site

This guide will help you customize the Everbloom Archive to create a beautiful, personalized memorial for your loved one.

---

## 📝 Content Customization

### 1. **Update Personal Information**

#### Hero Section
Edit `frontend/src/components/HeroSection.tsx`:
```typescript
const name = "Your Loved One's Name";  // Change the name
const dates = "1950 - 2024";           // Change birth/death years
const tagline = "A life well lived";   // Add a personal tagline
```

#### Biography Section
Edit `frontend/src/components/BiographySection.tsx`:
- Replace the sample biography with personal memories
- Add specific life details and achievements
- Include family information and personal stories

### 2. **Add Real Life Events**

Access the admin panel at `http://localhost:8000/admin` or use the API:

```bash
# Add a life event via API
curl -X POST http://localhost:8000/life-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_year": 1975,
    "title": "Graduation",
    "description": "Graduated with honors from University",
    "location_name": "University Town",
    "coordinates": [40.7128, -74.0060],
    "is_featured": true
  }'
```

### 3. **Upload Personal Photos**

1. Go to the Gallery section on the website
2. Click "Upload Images"
3. Select meaningful family photos
4. Add descriptions and titles
5. Mark special photos as "featured"

---

## 🎨 Theme Customization

### 1. **Color Scheme**

Edit `frontend/src/index.css` or create a custom theme:

```css
:root {
  --primary-color: #2563eb;      /* Change primary blue */
  --secondary-color: #dc2626;    /* Change accent color */
  --background-color: #f8fafc;   /* Change background */
  --text-color: #1f2937;         /* Change text color */
}
```

### 2. **Typography**

Update fonts in `frontend/src/index.css`:

```css
body {
  font-family: 'Georgia', serif; /* Elegant serif font */
}

h1, h2, h3 {
  font-family: 'Playfair Display', serif; /* Classic headings */
}
```

### 3. **Hero Background**

Edit `frontend/src/components/HeroSection.tsx`:

```typescript
// Change background gradient
<div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100">
  
  // Or use a background image
  <div className="min-h-screen bg-cover bg-center bg-fixed" 
       style={{backgroundImage: "url('/path/to/image.jpg')"}}>
```

---

## 🖼️ Visual Customization

### 1. **Logo and Branding**

Replace the heart icon in the navigation:
```typescript
// In frontend/src/components/SiteNav.tsx
<Heart className="w-6 h-6" />  // Replace with custom logo
```

### 2. **Custom Icons**

Add custom SVG icons or use different Lucide icons:
```typescript
import { Flower, Heart, Star } from "lucide-react";
<Flower className="w-6 h-6" />  // Use flower instead of heart
```

### 3. **Background Images**

Add personal background images:
1. Place images in `frontend/public/images/`
2. Reference them in components:
```css
background-image: url('/images/family-photo.jpg');
```

---

## 📱 Layout Adjustments

### 1. **Section Order**

Edit `frontend/src/pages/Index.tsx` to reorder sections:
```typescript
<HeroSection />
<GallerySection />     // Move gallery up
<BiographySection />
<Timeline />
<TributesWall />
<DigitalCandle />
```

### 2. **Section Visibility**

Hide sections you don't need:
```typescript
// Comment out sections to hide them
// <DigitalCandle />
```

### 3. **Custom Sections**

Add new sections:
```typescript
// Create custom component
import CustomSection from "@/components/CustomSection";

// Add to main page
<CustomSection />
```

---

## 🔧 Advanced Customization

### 1. **Custom Domain**

1. Update `nginx/nginx.conf`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

2. Update `.env.prod`:
```bash
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

### 2. **Email Notifications**

Add email service for new tributes:
```python
# In backend/complete_app.py
import smtplib
from email.mime.text import MIMEText

def send_notification_email(tribute):
    # Send email when new tribute is posted
    pass
```

### 3. **Custom CSS Themes**

Create theme variants:
```css
/* themes/warm.css */
:root {
  --primary-color: #dc2626;
  --background-color: #fef2f2;
}

/* themes/ocean.css */
:root {
  --primary-color: #0891b2;
  --background-color: #f0f9ff;
}
```

---

## 📸 Media Management

### 1. **Photo Organization**

Organize gallery photos by categories:
- Childhood photos
- Family events
- Achievements
- Special moments

### 2. **Video Support**

Add video uploads to the gallery:
```typescript
// In gallery upload component
accept="image/*,video/*"
```

### 3. **Image Optimization**

Compress images before uploading:
- Use tools like TinyPNG
- Target file size under 2MB
- Use consistent dimensions

---

## 🎵 Audio Enhancements

### 1. **Background Music**

Add audio player for favorite songs:
```typescript
// Create AudioPlayer component
<audio controls>
  <source src="/music/favorite-song.mp3" type="audio/mpeg">
</audio>
```

### 2. **Voice Messages**

Allow audio tributes:
```typescript
// Add audio recording capability
const mediaRecorder = new MediaRecorder(stream);
```

---

## 📊 Analytics and Monitoring

### 1. **Visitor Tracking**

Add Google Analytics:
```html
<!-- In frontend/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

### 2. **Tribute Statistics**

Track engagement metrics:
- Number of candles lit
- Tribute submissions
- Photo uploads
- Visitor locations

---

## 🔒 Privacy Settings

### 1. **Public vs Private**

Control visibility:
```python
# Add privacy settings to tributes
is_public = db.Column(db.Boolean, default=True)
```

### 2. **Content Moderation**

Set up approval workflow:
```python
# Require admin approval for public content
approved = db.Column(db.Boolean, default=False)
```

---

## 🌍 Multilingual Support

### 1. **Language Options**

Add language selector:
```typescript
// Create language context
const [language, setLanguage] = useState('en');
```

### 2. **Translated Content**

Create language files:
```json
// locales/en.json
{
  "tributes_wall": "Tributes Wall",
  "leave_tribute": "Leave a Tribute"
}

// locales/es.json
{
  "tributes_wall": "Muro de Homenajes",
  "leave_tribute": "Dejar Homenaje"
}
```

---

## 📱 Mobile Optimization

### 1. **Touch Gestures**

Add swipe gestures for gallery:
```typescript
// Add touch support
const touchStartX = useRef(0);
const handleTouchStart = (e) => {
  touchStartX.current = e.touches[0].clientX;
};
```

### 2. **Mobile Navigation**

Optimize menu for mobile:
```css
@media (max-width: 768px) {
  .nav-menu {
    flex-direction: column;
  }
}
```

---

## 🎯 Seasonal Updates

### 1. **Holiday Themes**

Add seasonal decorations:
```typescript
// Check current season/month
const month = new Date().getMonth();
const isDecember = month === 11; // December
```

### 2. **Anniversary Reminders**

Set up memorial date reminders:
```typescript
// Calculate days since passing
const daysSince = Math.floor((Date.now() - memorialDate) / (1000 * 60 * 60 * 24));
```

---

## ✅ Quick Start Checklist

### Basic Customization
- [ ] Update name and dates in HeroSection
- [ ] Add personal biography
- [ ] Upload family photos
- [ ] Add real life events to timeline
- [ ] Test all functionality

### Advanced Customization
- [ ] Customize color scheme
- [ ] Add custom domain
- [ ] Set up email notifications
- [ ] Add background music
- [ ] Configure privacy settings

### Final Steps
- [ ] Test on mobile devices
- [ ] Check all links and forms
- [ ] Verify real-time features
- [ ] Deploy to production
- [ ] Share with family and friends

---

## 💌 Need Help?

If you need assistance with customization:

1. **Check the Documentation**: Review all technical docs
2. **Test Changes**: Always test in development first
3. **Backup Data**: Save your customizations
4. **Ask for Help**: Reach out for technical support

**Remember**: This is your memorial. Make it personal, meaningful, and beautiful. 🌸

---

## 🎨 Inspiration Ideas

### Memorial Themes
- **Garden Theme**: Green colors, flower imagery, nature sounds
- **Ocean Theme**: Blue colors, wave sounds, beach photos
- **Vintage Theme**: Sepia tones, classic typography, historical photos
- **Modern Theme**: Clean lines, minimal design, contemporary fonts

### Personal Touches
- Favorite quotes or poems
- Significant dates and anniversaries
- Personal achievements and milestones
- Family traditions and memories
- Hobbies and passions

The Everbloom Archive is designed to be a living memorial that grows and evolves with your family's memories. Make it uniquely yours. 💙
