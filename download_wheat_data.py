#!/usr/bin/env python3
"""
Download the latest wheat trade data from FAOSTAT API
"""

import requests
import json
import csv
import time
from pathlib import Path

# FAOSTAT API endpoints
BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en"
BULK_URL = "https://fenixservices.fao.org/faostat/static/bulkdownloads"

def download_bulk_data():
    """
    Download wheat data using FAOSTAT bulk download
    This is the simpler approach - downloads the entire Trade dataset
    """
    print("Downloading FAOSTAT Trade data (bulk download)...")
    
    # The bulk download for Trade - Crops and Livestock Products
    bulk_file_url = f"{BULK_URL}/Trade_CropsLivestock_E_All_Data_(Normalized).zip"
    
    print(f"Downloading from: {bulk_file_url}")
    response = requests.get(bulk_file_url, stream=True)
    
    if response.status_code == 200:
        output_file = Path("data/Trade_CropsLivestock_E_All_Data_(Normalized).zip")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded to: {output_file}")
        print("\nNow extracting and filtering for wheat data...")
        
        # Extract and filter
        import zipfile
        with zipfile.ZipFile(output_file, 'r') as zip_ref:
            zip_ref.extractall("data/temp_trade")
        
        # Find the CSV file
        csv_files = list(Path("data/temp_trade").glob("*.csv"))
        if csv_files:
            filter_wheat_data(csv_files[0])
        
        return True
    else:
        print(f"Error downloading: {response.status_code}")
        return False

def filter_wheat_data(input_csv):
    """
    Filter the full trade data to only include wheat
    """
    print(f"Filtering wheat data from {input_csv}...")
    
    output_file = Path("data/wheat-FAOSTAT.csv")
    wheat_rows = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        for row in reader:
            # Filter for wheat (Item Code = 15 or Item = "Wheat")
            if row.get('Item Code') == '15' or row.get('Item') == 'Wheat':
                wheat_rows.append(row)
    
    print(f"Found {len(wheat_rows)} wheat records")
    
    # Write filtered data
    if wheat_rows:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(wheat_rows)
        
        print(f"Saved filtered wheat data to: {output_file}")
        
        # Clean up temp directory
        import shutil
        shutil.rmtree("data/temp_trade", ignore_errors=True)
        Path("data/Trade_CropsLivestock_E_All_Data_(Normalized).zip").unlink(missing_ok=True)
    
    return output_file

def download_area_data(area_code, area_name, append=False):
    """
    Download wheat data for a specific area/country
    
    Args:
        area_code: FAO area code (e.g., 229 for UK, 5000 for World)
        area_name: Human-readable name for logging
        append: If True, append to existing file; if False, create new file
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\nDownloading wheat data for {area_name} (code: {area_code})...")
    
    # API parameters for wheat trade data
    api_url = f"{BASE_URL}/data/TCL"
    elements_str = '5610,5622,5910,5922'  # Import Qty, Import Value, Export Qty, Export Value
    years_str = ','.join(map(str, range(1961, 2026)))  # 1961 to 2025
    
    # Build query with area filter
    full_url = f"{api_url}?item=15&element={elements_str}&year={years_str}&area={area_code}"
    
    print(f"  Request: ...area={area_code}")
    
    try:
        response = requests.get(full_url, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                print(f"  ✓ Received {len(data['data'])} records")
                
                # Save to CSV
                output_file = Path("data/wheat-FAOSTAT.csv")
                
                # Determine write mode
                mode = 'a' if append and output_file.exists() else 'w'
                write_header = not append or not output_file.exists()
                
                with open(output_file, mode, encoding='utf-8', newline='') as f:
                    if data['data']:
                        fieldnames = data['data'][0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        if write_header:
                            writer.writeheader()
                        writer.writerows(data['data'])
                
                return True
            else:
                print(f"  ⚠ No data returned for {area_name}")
                return False
        else:
            print(f"  ✗ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def download_via_api_incremental():
    """
    Download wheat data incrementally - UK first, then continents
    This builds up cached data slowly with smaller API calls
    """
    print("Downloading wheat data via FAOSTAT API (incremental approach)...")
    print("Strategy: UK first, then continents\n")
    
    # Priority areas to download
    # Area codes from FAOSTAT: https://www.fao.org/faostat/en/#definitions
    priority_areas = [
        (229, "United Kingdom"),
        (5000, "World"),  # Global aggregate
        (5100, "Africa"),
        (5200, "Americas"),
        (5300, "Asia"),
        (5400, "Europe"),
        (5500, "Oceania"),
    ]
    
    success_count = 0
    total_areas = len(priority_areas)
    
    for i, (area_code, area_name) in enumerate(priority_areas):
        is_first = (i == 0)
        result = download_area_data(area_code, area_name, append=not is_first)
        
        if result:
            success_count += 1
        
        # Rate limiting - be nice to the API
        if i < total_areas - 1:
            time.sleep(2)  # Wait 2 seconds between requests
    
    print(f"\n{'='*60}")
    print(f"Downloaded data for {success_count}/{total_areas} areas")
    print(f"{'='*60}")
    
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
    
    # If API fails, fall back to bulk download
    if not success:
        print("\nAPI download failed. Trying bulk download...")
        print("(This will download ~100MB and may take a few minutes)")
        response = input("Continue with bulk download? (y/n): ")
        
        if response.lower() == 'y':
            success = download_bulk_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Download complete!")
        print("=" * 60)
        print("\nYour wheat data has been updated in data/wheat-FAOSTAT.csv")
    else:
        print("\n" + "=" * 60)
        print("✗ Download failed")
        print("=" * 60)
        print("\nPlease visit https://www.fao.org/faostat/en/#data/TCL")
        print("to manually download the data.")

if __name__ == "__main__":
    main()
