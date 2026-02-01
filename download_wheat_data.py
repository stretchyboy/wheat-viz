#!/usr/bin/env python3
"""
Download the latest wheat trade data from FAOSTAT API
Stores data directly as JSON files for each country/area
"""

import requests
import json
import csv
import time
from pathlib import Path

# FAOSTAT API endpoints
BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en"
BULK_URL = "https://fenixservices.fao.org/faostat/static/bulkdownloads"
DATA_DIR = Path("data")

def normalize_area_name(area_name):
    """Convert area name to filename-safe format"""
    return area_name.lower().replace(" ", "_").replace("-", "_").replace(",", "").replace(".", "")

def get_existing_json_data(area_code, area_name):
    """
    Load existing JSON data for an area if it exists
    Returns: dict with years as keys
    """
    filename = normalize_area_name(area_name) + ".json"
    json_file = DATA_DIR / filename
    
    if not json_file.exists():
        return {}
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert list to dict keyed by year
            return {str(item['year']): item for item in data}
    except Exception as e:
        print(f"  Note: Could not read {json_file}: {e}")
        return {}

def save_json_data(area_code, area_name, year_data):
    """
    Save data for an area as a JSON file
    
    Args:
        area_code: FAO area code
        area_name: Human-readable name
        year_data: Dict with years as keys and data dicts as values
    """
    filename = normalize_area_name(area_name) + ".json"
    json_file = DATA_DIR / filename
    
    # Convert dict back to sorted list
    data_list = [year_data[year] for year in sorted(year_data.keys(), key=int)]
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=4)
    
    return json_file

def download_bulk_data():
    """
    Download wheat data using FAOSTAT bulk download
    Processes data directly into JSON files by country/area
    Caches the downloaded zip file for reuse
    """
    output_file = Path("data/Trade_CropsLivestock_E_All_Data_(Normalized).zip")
    
    # Check if we already have the bulk download cached
    if output_file.exists():
        print("✓ Found cached bulk download file")
        print(f"  Using: {output_file}")
    else:
        print("Downloading FAOSTAT Trade data (bulk download)...")
        print("(This will download ~100MB and may take a few minutes)")
        
        bulk_file_url = f"{BULK_URL}/Trade_CropsLivestock_E_All_Data_(Normalized).zip"
        
        print(f"Downloading from: {bulk_file_url}")
        response = requests.get(bulk_file_url, stream=True)
        
        if response.status_code == 200:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Downloaded to: {output_file}")
        else:
            print(f"✗ Error downloading: {response.status_code}")
            return False
    
    print("\nExtracting and processing wheat data to JSON files...")
    
    # Extract and filter
    import zipfile
    temp_dir = Path("data/temp_trade")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(output_file, 'r') as zip_ref:
        # List all files in the archive
        file_list = zip_ref.namelist()
        print(f"  Archive contains {len(file_list)} files")
        
        # Find the main data CSV file
        data_file = None
        for filename in file_list:
            # Look for files with "All_Data" but NOT "ItemCodes" or "Metadata"
            if 'All_Data' in filename and filename.endswith('.csv'):
                if 'ItemCodes' not in filename and 'Metadata' not in filename:
                    data_file = filename
                    break
        
        if not data_file:
            # Fallback: find largest CSV that's not ItemCodes or Metadata
            csv_files = [f for f in file_list if f.endswith('.csv') 
                        and 'ItemCodes' not in f and 'Metadata' not in f]
            if csv_files:
                data_file = csv_files[0]
        
        if data_file:
            print(f"  Extracting: {data_file}")
            zip_ref.extract(data_file, temp_dir)
            process_bulk_to_json(temp_dir / data_file)
        else:
            print("  ✗ Could not find data CSV file in archive")
            print(f"  Available files: {file_list[:5]}...")
            return False
    
    return True

def process_bulk_to_json(input_csv):
    """
    Process the bulk CSV data directly into JSON files by country/area
    Only processes wheat data
    """
    print(f"Processing wheat data from {input_csv.name}...")
    print("  (This may take a minute - processing large CSV file)")
    
    # Track data by area
    area_data = {}  # area_code -> {area_name, year_data}
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        row_count = 0
        wheat_count = 0
        
        for row in reader:
            row_count += 1
            
            # Show progress every 100k rows
            if row_count % 100000 == 0:
                print(f"  ... processed {row_count:,} rows, found {wheat_count:,} wheat records")
            
            # Filter for wheat (Item Code = 15 or Item = "Wheat")
            item_code = row.get('Item Code', '')
            item = row.get('Item', '')
            
            if item_code != '15' and 'Wheat' not in item:
                continue
            
            wheat_count += 1
            
            area_code = row.get('Area Code', '')
            area_name = row.get('Area', '')
            year = row.get('Year', '')
            element = row.get('Element', '')
            value = row.get('Value', '0')
            
            if not (area_code and area_name and year):
                continue
            
            # Initialize area if needed
            if area_code not in area_data:
                area_data[area_code] = {
                    'area_name': area_name,
                    'year_data': {}
                }
            
            # Initialize year if needed
            if year not in area_data[area_code]['year_data']:
                area_data[area_code]['year_data'][year] = {'year': int(year)}
            
            year_rec = area_data[area_code]['year_data'][year]
            
            # Map element to field name
            try:
                val = int(float(value)) if value else 0
            except:
                val = 0
            
            if 'Import Quantity' in element:
                year_rec['import_quantity'] = val
            elif 'Import Value' in element:
                year_rec['import_value'] = val
            elif 'Export Quantity' in element:
                year_rec['export_quantity'] = val
            elif 'Export Value' in element:
                year_rec['export_value'] = val
    
    print(f"  ✓ Processed {row_count:,} total rows")
    print(f"  ✓ Found {wheat_count:,} wheat records across {len(area_data)} areas")
    
    # Calculate prices and save each area to its own JSON file
    print(f"  Saving JSON files...")
    saved_count = 0
    for area_code, data in area_data.items():
        area_name = data['area_name']
        year_data = data['year_data']
        
        # Calculate prices
        for year, year_rec in year_data.items():
            if 'import_quantity' in year_rec and year_rec['import_quantity'] > 0:
                import_val = year_rec.get('import_value', 0)
                year_rec['import_price'] = int(import_val / year_rec['import_quantity']) if import_val else 0
            
            if 'export_quantity' in year_rec and year_rec['export_quantity'] > 0:
                export_val = year_rec.get('export_value', 0)
                year_rec['export_price'] = int(export_val / year_rec['export_quantity']) if export_val else 0
        
        # Save to JSON file
        try:
            save_json_data(area_code, area_name, year_data)
            saved_count += 1
        except Exception as e:
            print(f"  ⚠ Could not save {area_name}: {e}")
    
    print(f"  ✓ Saved {saved_count} JSON files to data/ folder")
    
    # Clean up temp directory
    import shutil
    shutil.rmtree("data/temp_trade", ignore_errors=True)
    
    return saved_count

def download_area_data(area_code, area_name, years=None):
    """
    Download wheat data for a specific area/country and save as JSON
    
    Args:
        area_code: FAO area code (e.g., 229 for UK, 5000 for World)
        area_name: Human-readable name for logging
        years: List of years to fetch (default: 1961-current year+1)
    
    Returns:
        True if successful
        False if failed (no data or other error)
        521 if server is down (special case to stop retrying)
    """
    if years is None:
        current_year = 2026
        years = list(range(1961, current_year + 1))
    
    print(f"\nDownloading wheat data for {area_name} (code: {area_code})...")
    print(f"  Years: {min(years)}-{max(years)} ({len(years)} years)")
    
    # API parameters for wheat trade data
    api_url = f"{BASE_URL}/data/TCL"
    elements_str = '5610,5622,5910,5922'  # Import Qty, Import Value, Export Qty, Export Value
    years_str = ','.join(map(str, years))
    
    # Build query with area filter
    full_url = f"{api_url}?item=15&element={elements_str}&year={years_str}&area={area_code}"
    
    try:
        response = requests.get(full_url, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                print(f"  ✓ Received {len(data['data'])} records")
                
                # Load existing data for this area
                existing_data = get_existing_json_data(area_code, area_name)
                
                # Process and merge new data
                for record in data['data']:
                    year = str(record.get('Year') or record.get('year', ''))
                    element = record.get('Element') or record.get('element', '')
                    value = record.get('Value') or record.get('value', 0)
                    
                    if not year:
                        continue
                    
                    # Initialize year entry if needed
                    if year not in existing_data:
                        existing_data[year] = {'year': int(year)}
                    
                    # Map element to field name
                    if 'Import Quantity' in element:
                        existing_data[year]['import_quantity'] = int(float(value)) if value else 0
                    elif 'Import Value' in element:
                        existing_data[year]['import_value'] = int(float(value)) if value else 0
                    elif 'Export Quantity' in element:
                        existing_data[year]['export_quantity'] = int(float(value)) if value else 0
                    elif 'Export Value' in element:
                        existing_data[year]['export_value'] = int(float(value)) if value else 0
                
                # Calculate prices where possible
                for year, year_data in existing_data.items():
                    if 'import_quantity' in year_data and year_data['import_quantity'] > 0:
                        import_val = year_data.get('import_value', 0)
                        year_data['import_price'] = int(import_val / year_data['import_quantity']) if import_val else 0
                    
                    if 'export_quantity' in year_data and year_data['export_quantity'] > 0:
                        export_val = year_data.get('export_value', 0)
                        year_data['export_price'] = int(export_val / year_data['export_quantity']) if export_val else 0
                
                # Save to JSON file
                json_file = save_json_data(area_code, area_name, existing_data)
                print(f"  ✓ Saved to {json_file}")
                
                return True
            else:
                print(f"  ⚠ No data returned for {area_name}")
                return False
        elif response.status_code == 521:
            print(f"  ✗ API returned status code: 521 (Web Server Is Down)")
            return 521
        else:
            print(f"  ✗ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def download_via_api_incremental():
    """
    Download wheat data incrementally - processes up to 5 downloads per run
    Downloads in 10-year chunks for better reliability
    Saves directly as JSON files (no CSV intermediate step)
    Run multiple times to eventually cover all countries and years
    """
    print("Downloading wheat data via FAOSTAT API (incremental approach)...")
    print("Strategy: Download up to 5 chunks per run, 10-year periods for reliability")
    print("Data stored directly as JSON files in data/ folder\n")
    
    # Count existing JSON files
    existing_json_files = list(DATA_DIR.glob("*.json"))
    print(f"✓ Found {len(existing_json_files)} existing JSON files")
    
    # Comprehensive list of priority areas
    priority_areas = [
        # Priority 1: UK and global aggregates
        (229, "United Kingdom"),
        (5000, "World"),
        
        # Priority 2: Continents
        (5100, "Africa"),
        (5200, "Americas"),
        (5300, "Asia"),
        (5400, "Europe"),
        (5500, "Oceania"),
        
        # Priority 3: Major wheat traders
        (231, "United States"),
        (41, "China"),
        (100, "India"),
        (185, "Russian Federation"),
        (33, "Canada"),
        (14, "Australia"),
        (68, "France"),
        (79, "Germany"),
        (165, "Pakistan"),
        (237, "Ukraine"),
        (213, "Turkey"),
        (4, "Argentina"),
        (149, "Poland"),
        (184, "Romania"),
        (138, "Netherlands"),
        (10, "Belgium"),
        (219, "United Arab Emirates"),
        (21, "Brazil"),
        (107, "Italy"),
        (203, "Spain"),
        (81, "Japan"),
        (157, "Saudi Arabia"),
        (85, "Egypt"),
        (115, "Mexico"),
        (1, "Afghanistan"),
        (3, "Algeria"),
        (228, "Sudan"),
        (110, "Kazakhstan"),
        (238, "Uzbekistan"),
    ]
    
    current_year = 2026
    # Break years into 10-year chunks
    year_ranges = []
    start_year = 1961
    while start_year <= current_year:
        end_year = min(start_year + 9, current_year)
        year_ranges.append((start_year, end_year))
        start_year = end_year + 1
    
    print(f"Year ranges: {len(year_ranges)} chunks of ~10 years")
    
    downloads_this_run = 0
    max_downloads = 5
    success_count = 0
    
    # Process each area with year chunks
    for area_code, area_name in priority_areas:
        if downloads_this_run >= max_downloads:
            print(f"\n⏸ Reached limit of {max_downloads} downloads per run")
            break
        
        # Check what years we already have for this area
        existing_data = get_existing_json_data(area_code, area_name)
        existing_years = set(existing_data.keys())
        
        # Find which year ranges are missing
        for start_year, end_year in year_ranges:
            if downloads_this_run >= max_downloads:
                break
            
            # Check if we already have all years in this range
            years_in_range = list(range(start_year, end_year + 1))
            missing_years = [y for y in years_in_range if str(y) not in existing_years]
            
            if not missing_years:
                # Skip this range, we already have it
                continue
            
            # Download this year range
            print(f"\n→ {area_name} ({start_year}-{end_year}): Fetching {len(missing_years)} years")
            
            result = download_area_data(area_code, area_name, years=missing_years)
            
            # Check for server down error (521)
            if result == 521:
                print(f"\n🛑 API server is down (521 error) - stopping download attempts")
                print(f"   Downloaded {downloads_this_run} chunks before server went down")
                print(f"   Run again later when the API is back online")
                return downloads_this_run > 0
            
            if result:
                success_count += 1
                downloads_this_run += 1
                # Update our tracking of what we have
                existing_years.update(str(y) for y in missing_years)
            
            # Rate limiting between requests
            if downloads_this_run < max_downloads:
                time.sleep(2)
        
        # If we've completed all year ranges for this area
        if downloads_this_run < max_downloads and len(existing_years) > 0:
            complete_years = len([y for y in range(1961, current_year + 1) if str(y) in existing_years])
            if complete_years > 0:
                print(f"  ✓ {area_name}: Has {complete_years} years total")
    
    # Count JSON files again
    final_json_files = list(DATA_DIR.glob("*.json"))
    
    print(f"\n{'='*60}")
    print(f"This run: {downloads_this_run} downloads")
    print(f"Total JSON files: {len(final_json_files)}")
    print(f"{'='*60}")
    print("\n💡 Tip: Run again to download more data (5 chunks per run)")
    
    return success_count > 0

def download_via_api():
    """
    Download wheat data using FAOSTAT REST API
    Uses incremental approach for better reliability
    """
    return download_via_api_incremental()

def main():
    print("=" * 60)
    print("FAOSTAT Wheat Data Downloader")
    print("=" * 60)
    print()
    
    # Try the API approach first (more targeted)
    print("Attempting API download (faster, more targeted)...")
    success = download_via_api()
    
    # If API fails, automatically use bulk download
    if not success:
        print("\nAPI download failed. Using bulk download...")
        success = download_bulk_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Download complete!")
        print("=" * 60)
        print("\nWheat data has been saved as JSON files in data/ folder")
        print("Each country/area has its own JSON file")
    else:
        print("\n" + "=" * 60)
        print("✗ Download failed")
        print("=" * 60)
        print("\nPlease visit https://www.fao.org/faostat/en/#data/TCL")
        print("to manually download the data.")

if __name__ == "__main__":
    main()
