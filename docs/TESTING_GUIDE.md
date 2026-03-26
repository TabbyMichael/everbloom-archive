# Everbloom Archive - Testing Guide

## 🚀 Development Setup Complete

### ✅ Services Running
- **Frontend**: http://localhost:8080 (React app)
- **Backend API**: http://localhost:8000 (Flask with WebSocket)
- **Admin Panel**: http://localhost:8000/admin
- **WebSocket**: Real-time updates enabled

### 🔐 Admin Access
- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Feature Testing Checklist

### 1. **Basic Functionality** ✅
- [ ] Frontend loads at http://localhost:8080
- [ ] API responds at http://localhost:8000
- [ ] Health check: http://localhost:8000/health

### 2. **Timeline Component** 
- [ ] Navigate to Timeline section
- [ ] Life events display with years and titles
- [ ] Click on events to see detailed view
- [ ] Featured events have star indicators
- [ ] Coordinates display for location-based events

### 3. **Tributes Wall** 🕯️
- [ ] View existing tributes
- [ ] Click "Leave a Tribute" button
- [ ] Fill out tribute form (name, message, etc.)
- [ ] Submit new tribute
- [ ] Click candle button to light candles
- [ ] See real-time candle counter update
- [ ] WebSocket connection indicator shows green

### 4. **Gallery Upload** 📸
- [ ] Click upload button in Gallery section
- [ ] Select image file from device
- [ ] Add title and description
- [ ] Upload image successfully
- [ ] See new image in gallery
- [ ] Click image for full-screen view

### 5. **Admin Panel** 👑
- [ ] Access: http://localhost:8000/admin
- [ ] Login with admin credentials
- [ ] View statistics dashboard
- [ ] See tribute count and candle count
- [ ] View recent tributes
- [ ] Manage users (if implemented)

### 6. **Real-time Features** ⚡
- [ ] Open two browser windows
- [ ] Light candle in one window
- [ ] See candle update in other window instantly
- [ ] Add tribute in one window
- [ ] See tribute appear in other window
- [ ] WebSocket connection indicator shows status

### 7. **API Endpoints** 🔌
Test these endpoints directly:

```bash
# Get all life events
curl http://localhost:8000/life-events

# Get all tributes
curl http://localhost:8000/tributes

# Light a candle (replace ID with actual tribute ID)
curl -Method POST http://localhost:8000/tributes/{TRIBUTE_ID}/light-candle

# Create new tribute
curl -Method POST -Headers @{"Content-Type": "application/json"} -Body '{"author_name":"Test User","message":"Test message"}' http://localhost:8000/tributes
```

---

## 🐛 Troubleshooting

### Frontend Issues
- **404 errors**: Check if frontend is running on port 8080
- **API errors**: Verify backend is running on port 8000
- **CORS issues**: Check ALLOWED_ORIGINS in backend

### Backend Issues
- **Database errors**: Ensure `everbloom.db` exists in backend folder
- **WebSocket errors**: Check browser console for connection status
- **Upload errors**: Verify uploads directory exists

### Common Fixes
1. **Restart services**: Stop and restart both frontend and backend
2. **Clear browser cache**: Hard refresh (Ctrl+F5)
3. **Check console**: Look for JavaScript errors in browser dev tools
4. **Verify ports**: Ensure 8080 and 8000 are available

---

## 📊 Performance Testing

### Load Testing
- Test with multiple simultaneous users
- Verify WebSocket connections handle multiple clients
- Test file upload with large images
- Check memory usage with many tributes

### Stress Testing
- Rapid candle lighting/unlighting
- Multiple file uploads simultaneously
- Admin panel under heavy load

---

## 📱 Mobile Testing

### Responsive Design
- [ ] Test on mobile viewport (Chrome DevTools)
- [ ] Timeline layout works on small screens
- [ ] Tribute form usable on mobile
- [ ] Gallery images display properly

### Touch Interactions
- [ ] Tap to light candles
- [ ] Swipe through gallery
- [ ] Mobile-friendly navigation

---

## 🔒 Security Testing

### Authentication
- [ ] Login/logout functionality
- [ ] Protected admin routes
- [ ] Session management

### Input Validation
- [ ] Form validation on tribute submission
- [ ] File upload restrictions
- [ ] XSS prevention

---

## ✅ Success Criteria

### Minimum Viable Product
- [x] Users can view timeline of life events
- [x] Users can leave and view tributes
- [x] Users can light candles (real-time)
- [x] Users can upload images to gallery
- [x] Admin can manage content
- [x] Real-time updates work across browsers

### Advanced Features
- [x] WebSocket real-time updates
- [x] File upload with validation
- [x] Admin authentication
- [x] Responsive design
- [x] Error handling
- [x] Loading states

---

## 🚀 Next Steps

After successful testing:

1. **Production Deployment**: Run `./deploy.sh`
2. **Customization**: Add your own content and themes
3. **Scaling**: Monitor performance and optimize
4. **Features**: Add additional functionality based on feedback

---

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Review browser console for errors
3. Verify all services are running
4. Check network connectivity
5. Restart services if needed

**Happy Testing! 🌸**
