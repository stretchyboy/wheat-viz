#!/bin/bash

# Complete setup script for Agricultural Trade Visualization

echo "============================================================"
echo "Agricultural Trade Visualization - Complete Setup"
echo "============================================================"
echo ""

# Step 1: Download data
echo "Step 1: Downloading all crops data from FAOSTAT..."
echo "This may take a few minutes..."
python3 download_wheat_data.py

if [ $? -ne 0 ]; then
    echo "❌ Download failed. Please check your internet connection."
    exit 1
fi

echo ""
echo "Step 2: Processing data into individual crop-country files..."
python3 process_data.py

if [ $? -ne 0 ]; then
    echo "❌ Processing failed."
    exit 1
fi

echo ""
echo "============================================================"
echo "✓ Setup Complete!"
echo "============================================================"
echo ""
echo "You can now:"
echo "1. Open output/index.html in your browser"
echo "2. Select crop and country to visualize"
echo ""
echo "Or use direct links like:"
echo "  - output/index.html?crop=wheat&country=world"
echo "  - output/index.html?crop=rice&country=china"
echo "  - output/index.html?crop=coffee&country=brazil"
echo ""
echo "To view in browser now, run:"
echo "  open output/index.html    (macOS)"
echo "  xdg-open output/index.html    (Linux)"
echo "  start output/index.html    (Windows)"
echo ""
