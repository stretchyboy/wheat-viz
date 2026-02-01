# Agricultural Trade Visualization - Output

This directory contains the improved visualization system with full-screen video and handdrawn graph overlays.

## Features

### 1. **Crop and Country Selection**
- Interactive selector to choose any crop and country combination
- Smooth transition between selector and visualization

### 2. **URL Parameters for Direct Links**
- Create shareable links with specific crop/country combinations
- Format: `index.html?crop=wheat&country=united_kingdom`
- Examples:
  - `index.html?crop=wheat&country=world`
  - `index.html?crop=rice&country=china`
  - `index.html?crop=coffee&country=brazil`

### 3. **Full-Screen Video**
- Video fills the entire screen
- Color filter (hue rotation) based on import price data
- Smooth looping animation

### 4. **Handdrawn Graph Overlay**
- Real-time graph drawn over the video using Rough.js
- Handdrawn aesthetic with customizable roughness
- Shows import price trends over time
- Current data point highlighted
- Responsive to window resizing

### 5. **Data Display**
- Current year, import price, and import quantity
- Updates in real-time with the video
- Semi-transparent overlay for easy reading

### 6. **Controls**
- Change Selection: Return to crop/country selector
- Fullscreen: Toggle fullscreen mode
- Video controls available

## Setup

1. **Download Data**
   ```bash
   python3 ../download_wheat_data.py
   ```
   This will download all crops data and cache it.

2. **Open Visualization**
   - Open `output/index.html` in a web browser
   - Select crop and country
   - Click "Visualize"

3. **Create Direct Links**
   - Use URL parameters for specific combinations
   - Share links with colleagues

## File Structure

```
output/
├── index.html           # Main visualization page
├── visualization.js     # Visualization logic with Rough.js
└── README.md           # This file
```

## Dependencies

- **Rough.js**: Loaded from CDN for handdrawn graphics
- Video file: Expects `../videos/Wheat Field - Crop Timelapse-SD.mp4`
- Data files: Expected in `../data/[country].json`

## Data Format

The visualization expects country JSON files with the following structure:

```json
[
  {
    "year": "1992",
    "import_price": 150.50,
    "import_quantity": 1000000,
    "export_price": 140.25,
    "export_quantity": 500000
  },
  ...
]
```

## Customization

### Graph Styling
Edit in `visualization.js`:
- `roughness`: Controls handdrawn effect intensity (0-3)
- `bowing`: Controls curve bendiness (0-3)
- `strokeWidth`: Line thickness
- Colors: Change stroke and fill colors

### Video Effects
- Hue rotation range: Currently 0-270 degrees
- Can add brightness, contrast, saturation filters

### Animation Speed
- Currently synced to 54-second video
- Adjust `frameInterval` calculation in `startVisualization()`

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Fullscreen API support recommended

## Future Enhancements

- [ ] Multiple video sources for different crops
- [ ] Dual-axis graphs (price + quantity)
- [ ] Export graph as image
- [ ] Compare multiple countries
- [ ] Historical playback controls (scrubbing)
