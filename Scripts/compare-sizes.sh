#!/bin/bash

# Docker Image Size Comparison Script
echo "🐳 Docker Image Size Comparison"
echo "================================"

# Function to get image size
get_image_size() {
    local image_name=$1
    local size=$(docker images --format "{{.Size}}" $image_name 2>/dev/null)
    if [ -z "$size" ]; then
        echo "0B"
    else
        echo $size
    fi
}

# Build both images
echo "📦 Building Docker images..."

echo "Building original image..."
docker build -t everbloom-backend:original -f backend/Dockerfile.prod ./backend 2>/dev/null

echo "Building optimized image..."
docker build -t everbloom-backend:optimized -f backend/Dockerfile.optimized ./backend 2>/dev/null

# Get sizes
echo ""
echo "📊 Image Size Comparison"
echo "======================"

original_size=$(get_image_size "everbloom-backend:original")
optimized_size=$(get_image_size "everbloom-backend:optimized")

echo "Original Backend Image: $original_size"
echo "Optimized Backend Image: $optimized_size"

# Convert sizes to MB for calculation
original_mb=$(echo $original_size | sed 's/MB//g' | sed 's/GB//g' | awk '{print $1}')
optimized_mb=$(echo $optimized_size | sed 's/MB//g' | sed 's/GB//g' | awk '{print $1}')

# Handle GB to MB conversion
if [[ $original_size == *"GB"* ]]; then
    original_mb=$(echo "$original_mb * 1024" | bc)
fi
if [[ $optimized_size == *"GB"* ]]; then
    optimized_mb=$(echo "$optimized_mb * 1024" | bc)
fi

# Calculate reduction
if [ "$original_mb" -gt 0 ]; then
    reduction=$(echo "scale=1; (($original_mb - $optimized_mb) / $original_mb) * 100" | bc)
    echo ""
    echo "🎉 Size Reduction: ${reduction}%"
    echo "💾 Space Saved: $(echo "$original_mb - $optimized_mb" | bc)MB"
fi

echo ""
echo "🔍 Detailed Analysis"
echo "=================="

# Show layer sizes
echo "Original image layers:"
docker history everbloom-backend:original --format "table {{.CreatedBy}}\t{{.Size}}" | head -10

echo ""
echo "Optimized image layers:"
docker history everbloom-backend:optimized --format "table {{.CreatedBy}}\t{{.Size}}" | head -10

# Show container resource usage
echo ""
echo "📈 Resource Usage Test"
echo "======================"

echo "Starting original container..."
docker run -d --name original-test everbloom-backend:original 2>/dev/null
sleep 5
original_memory=$(docker stats --no-stream --format "{{.MemUsage}}" original-test 2>/dev/null)
docker stop original-test 2>/dev/null
docker rm original-test 2>/dev/null

echo "Starting optimized container..."
docker run -d --name optimized-test everbloom-backend:optimized 2>/dev/null
sleep 5
optimized_memory=$(docker stats --no-stream --format "{{.MemUsage}}" optimized-test 2>/dev/null)
docker stop optimized-test 2>/dev/null
docker rm optimized-test 2>/dev/null

echo "Original Container Memory: $original_memory"
echo "Optimized Container Memory: $optimized_memory"

# Cleanup
echo ""
echo "🧹 Cleanup"
echo "========"
docker rmi everbloom-backend:original 2>/dev/null
docker rmi everbloom-backend:optimized 2>/dev/null

echo ""
echo "✅ Comparison complete!"
echo ""
echo "💡 Recommendations:"
echo "- Use optimized version for production"
echo "- Keep original for development debugging"
echo "- Monitor resource usage in production"
echo "- Consider further optimizations for large scale"
