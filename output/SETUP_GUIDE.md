# Agricultural Trade Visualization System

A full-screen, interactive visualization system for exploring agricultural trade data with handdrawn graph overlays.

## 🌟 Features

- **📊 All Crops Support**: Download and visualize data for all agricultural products
- **🎨 Handdrawn Graph Overlay**: Beautiful, sketch-style graphs using Rough.js
- **🎬 Full-Screen Video**: Immersive video background with dynamic color filtering
- **🔗 Direct URLs**: Share specific crop/country combinations with URL parameters
- **💾 Smart Caching**: Downloaded data is cached to avoid repeated downloads
- **🌍 Global Coverage**: All countries and regions from FAOSTAT database
- **📈 Real-Time Animation**: Graph draws in sync with video playback
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Option 1: Automated Setup

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Download all crops trade data from FAOSTAT (1961-2025)
2. Process data into individual crop-country files
3. Set up the visualization system

### Option 2: Manual Setup

1. **Download Data**
   ```bash
   python3 download_wheat_data.py
   ```
   - Downloads all crops data (not just wheat, despite the script name)
   - Caches in `data/cache/all_crops_FAOSTAT.csv`
   - Won't re-download if cache exists

2. **Process Data**
   ```bash
   python3 process_data.py
   ```
   - Converts cached CSV into individual JSON files
   - Creates `data/crops/[crop]_[country].json` for each combination
   - Generates `data/crops_list.txt` with available crops

3. **Open Visualization**
   ```bash
   open output/index.html
   # or
   xdg-open output/index.html  # Linux
   # or just open it in your browser
   ```

## 📖 Usage

### Interactive Mode

1. Open `output/index.html` in a web browser
2. Select a crop from the dropdown (e.g., "Wheat", "Rice", "Coffee")
3. Select a country from the dropdown (e.g., "World", "United Kingdom", "China")
4. Click "Visualize"
5. Watch the full-screen video with animated graph overlay
6. Use controls:
   - **Change Selection**: Return to selector
   - **Fullscreen**: Toggle fullscreen mode
   - Video controls for pause/play

### Direct Links

Create shareable URLs with specific combinations:

```
output/index.html?crop=wheat&country=world
output/index.html?crop=rice&country=china
output/index.html?crop=coffee&country=brazil
output/index.html?crop=maize&country=united_states_of_america
```

Format: `?crop=[CROP_NAME]&country=[COUNTRY_NAME]`

## 📁 Project Structure

```
wheat-viz/
├── download_wheat_data.py    # Download script (all crops, with caching)
├── process_data.py           # Data processor (CSV → JSON)
├── setup.sh                  # Automated setup script
├── output/                   # Visualization system
│   ├── index.html           # Main page with selectors
│   ├── visualization.js     # Visualization logic + Rough.js
│   ├── README.md            # Detailed documentation
│   └── SUMMARY.md           # Quick summary
├── data/
│   ├── cache/               # Cached download
│   │   └── all_crops_FAOSTAT.csv
│   ├── crops/               # Processed data
│   │   ├── wheat_world.json
│   │   ├── rice_china.json
│   │   └── ...
│   ├── crops_list.txt       # Available crops
│   ├── [country].json       # Legacy wheat data
│   └── wheat-FAOSTAT.csv    # Raw data
├── videos/
│   └── Wheat Field - Crop Timelapse-SD.mp4
└── countries.txt
```

## 🎨 Visualization Details

### Video Effects
- **Hue Rotation**: Video color shifts based on import price
- **Range**: 0-270 degrees (higher price = more rotation)
- **Smooth**: Transitions between frames

### Graph Overlay
- **Style**: Handdrawn using Rough.js library
- **Roughness**: Configurable sketch effect (currently 1.2)
- **Real-Time**: Draws one data point per video frame
- **Highlighting**: Current year shown as larger circle
- **Position**: Bottom of screen, semi-transparent background

### Data Display
- **Year**: Current year being shown
- **Import Price**: USD per tonne
- **Import Quantity**: Total tonnes imported
- **Updates**: Every frame (synced to video duration / data points)

## 🔧 Customization

### Change Graph Style

Edit `output/visualization.js`, in the `drawGraph()` function:

```javascript
roughCanvas.linearPath(points, {
    stroke: '#4CAF50',      // Line color
    strokeWidth: 3,         // Line thickness
    roughness: 1.2,         // Sketchiness (0-3)
    bowing: 0.5            // Curve bendiness (0-3)
});
```

### Change Animation Speed

Edit `output/visualization.js`, in `startVisualization()`:

```javascript
const frameInterval = Math.round((54 * 1000) / tradeData.length);
// Change 54 to desired seconds
```

### Change Video

Replace `videos/Wheat Field - Crop Timelapse-SD.mp4` with your video, or update the path in `output/index.html`:

```html
<source src="../videos/YOUR_VIDEO.mp4#t=6" type="video/mp4" />
```

## 📊 Data Source

Data from [FAOSTAT](https://www.fao.org/faostat/) (Food and Agriculture Organization of the United Nations):
- **Dataset**: Trade - Crops and Livestock Products
- **Years**: 1961-2025
- **Elements**: Import/Export Quantity and Value
- **Coverage**: All countries and regions
- **All Crops**: Complete agricultural product range

## 🌐 Browser Compatibility

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera
- ⚠️ Requires JavaScript enabled
- ⚠️ Fullscreen API for fullscreen mode

## 🐛 Troubleshooting

### "Data not available for this combination"
- Run `python3 process_data.py` to regenerate data files
- Check that `data/crops/` directory exists and contains files
- Try a different crop/country combination

### Video not playing
- Check that video file exists at `videos/Wheat Field - Crop Timelapse-SD.mp4`
- Try a different browser (Chrome recommended)
- Check browser console for errors

### Download fails
- Check internet connection
- FAOSTAT API might be temporarily unavailable
- Try the bulk download fallback option when prompted

### Graph not showing
- Check browser console for JavaScript errors
- Verify Rough.js is loading from CDN
- Try refreshing the page

## 📝 License

This visualization system is open source. Data is from FAOSTAT and subject to their terms of use.

## 🤝 Contributing

Feel free to:
- Add more video sources for different crops
- Improve graph styling and animations
- Add additional data visualizations
- Enhance mobile responsiveness
- Add data export features

## 📧 Support

For issues or questions about:
- **Data**: Visit [FAOSTAT](https://www.fao.org/faostat/)
- **Visualization**: Check `output/README.md` for detailed docs
- **Technical**: Review browser console for error messages
