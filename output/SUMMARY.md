# Agricultural Trade Visualization - Summary

## What's Been Created

### 1. **Enhanced Download Script** (`download_wheat_data.py`)
- Downloads **all crops** data from FAOSTAT (not just wheat)
- **Caches** the download in `data/cache/all_crops_FAOSTAT.csv`
- Covers years 1961-2025
- Won't re-download if cache exists (asks user first)

### 2. **New Visualization System** (`output/` directory)

#### **Features:**
✅ **Full-screen video** with crop-based color filtering  
✅ **Handdrawn graph overlay** using Rough.js library  
✅ **Interactive selectors** for crop and country  
✅ **Direct URL links** - shareable URLs like:
   - `output/index.html?crop=wheat&country=united_kingdom`
   - `output/index.html?crop=rice&country=china`
   - `output/index.html?crop=coffee&country=brazil`

✅ **Real-time data display** showing year, price, quantity  
✅ **Responsive design** adapts to window size  
✅ **Fullscreen mode** for immersive viewing  

#### **Files Created:**
- `output/index.html` - Main visualization page
- `output/visualization.js` - JavaScript with Rough.js integration
- `output/README.md` - Detailed documentation

## How It Works

1. **User selects** crop and country from dropdown menus
2. **Video plays** full-screen with color filter based on import prices
3. **Graph draws** in real-time over the video showing price trends
4. **Handdrawn aesthetic** using Rough.js for organic, sketchy look
5. **URL updates** automatically for easy sharing

## To Use

### Option 1: Interactive Selection
1. Open `output/index.html` in browser
2. Choose crop and country
3. Click "Visualize"

### Option 2: Direct Link
- Create URL: `output/index.html?crop=CROPNAME&country=COUNTRYNAME`
- Share with others
- Opens directly to that visualization

## Next Steps

To complete the system, you'll need to:

1. **Run the download script:**
   ```bash
   python3 download_wheat_data.py
   ```

2. **Process the cached data** into individual country JSON files for each crop
   (Currently uses existing wheat data structure)

3. **Copy video file** to `output/../videos/` if needed

4. **Open** `output/index.html` in a browser to test

## Technical Details

- **Graph Style**: Rough.js provides handdrawn appearance with configurable roughness
- **Animation**: Synced to 54-second video loop
- **Data Points**: Each frame shows one year of data
- **Color Filter**: Hue rotation (0-270°) based on import price
- **Overlay**: Semi-transparent graph with highlighted current point

## Example URLs

Once data is processed, you can use URLs like:
- `?crop=wheat&country=world`
- `?crop=wheat&country=united_states_of_america`
- `?crop=maize&country=brazil`
- `?crop=rice&country=china`
- `?crop=coffee&country=ethiopia`
