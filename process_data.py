#!/usr/bin/env python3
"""
Process cached all-crops data into individual country JSON files
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

def process_cached_data():
    """
    Read the cached all-crops CSV and generate country JSON files
    """
    cache_file = Path("data/cache/all_crops_FAOSTAT.csv")
    
    if not cache_file.exists():
        print("❌ No cached data found!")
        print("Please run: python3 download_wheat_data.py")
        return False
    
    print(f"Processing {cache_file}...")
    
    # Data structure: country -> crop -> year -> data
    data_by_country = defaultdict(lambda: defaultdict(dict))
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            country = row.get('Area') or row.get('AreaName', '').lower().replace(' ', '_')
            crop = row.get('Item') or row.get('ItemName', '').lower().replace(' ', '_')
            year = row.get('Year')
            element = row.get('Element') or row.get('ElementName', '')
            value = row.get('Value', '')
            
            if not country or not crop or not year:
                continue
            
            # Normalize country name
            country_key = country.lower().replace(' ', '_').replace('-', '_')
            crop_key = crop.lower().replace(' ', '_').replace('-', '_')
            
            # Initialize year data if needed
            if year not in data_by_country[country_key][crop_key]:
                data_by_country[country_key][crop_key][year] = {
                    'year': year,
                    'import_price': None,
                    'import_quantity': None,
                    'import_value': None,
                    'export_price': None,
                    'export_quantity': None,
                    'export_value': None
                }
            
            # Parse value
            try:
                val = float(value) if value else None
            except ValueError:
                val = None
            
            # Store based on element type
            if 'Import' in element and 'Quantity' in element:
                data_by_country[country_key][crop_key][year]['import_quantity'] = val
            elif 'Import' in element and 'Value' in element:
                data_by_country[country_key][crop_key][year]['import_value'] = val
            elif 'Export' in element and 'Quantity' in element:
                data_by_country[country_key][crop_key][year]['export_quantity'] = val
            elif 'Export' in element and 'Value' in element:
                data_by_country[country_key][crop_key][year]['export_value'] = val
    
    print(f"Found {len(data_by_country)} countries/regions")
    
    # Calculate import/export prices and write files
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    crop_dir = Path("data/crops")
    crop_dir.mkdir(exist_ok=True)
    
    files_written = 0
    
    for country, crops in data_by_country.items():
        for crop, years in crops.items():
            # Calculate prices (value / quantity)
            for year_data in years.values():
                if year_data['import_value'] and year_data['import_quantity'] and year_data['import_quantity'] > 0:
                    year_data['import_price'] = year_data['import_value'] / year_data['import_quantity'] * 1000  # per tonne
                if year_data['export_value'] and year_data['export_quantity'] and year_data['export_quantity'] > 0:
                    year_data['export_price'] = year_data['export_value'] / year_data['export_quantity'] * 1000  # per tonne
            
            # Sort by year
            sorted_data = sorted(years.values(), key=lambda x: x['year'])
            
            # Write crop-specific file
            crop_country_file = crop_dir / f"{crop}_{country}.json"
            with open(crop_country_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, indent=2)
            
            files_written += 1
    
    print(f"✅ Wrote {files_written} crop-country combination files to {crop_dir}/")
    
    # Also update the existing wheat country files for backward compatibility
    print("\nUpdating existing country wheat files for compatibility...")
    
    wheat_countries = 0
    for country, crops in data_by_country.items():
        if 'wheat' in crops:
            output_file = output_dir / f"{country}.json"
            sorted_data = sorted(crops['wheat'].values(), key=lambda x: x['year'])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_data, f, indent=2)
            
            wheat_countries += 1
    
    print(f"✅ Updated {wheat_countries} country files with wheat data")
    
    # Generate crop list
    all_crops = set()
    for crops in data_by_country.values():
        all_crops.update(crops.keys())
    
    crops_file = Path("data/crops_list.txt")
    with open(crops_file, 'w', encoding='utf-8') as f:
        for crop in sorted(all_crops):
            f.write(f"{crop}\n")
    
    print(f"✅ Generated crops list: {crops_file}")
    print(f"   Total crops: {len(all_crops)}")
    
    return True

def main():
    print("=" * 60)
    print("FAOSTAT Data Processor")
    print("=" * 60)
    print()
    
    success = process_cached_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Processing complete!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Open output/index.html in a browser")
        print("2. Select any crop and country to visualize")
        print("3. Use direct URLs like:")
        print("   output/index.html?crop=wheat&country=world")
        print("   output/index.html?crop=rice&country=china")
    else:
        print("\n" + "=" * 60)
        print("✗ Processing failed")
        print("=" * 60)

if __name__ == "__main__":
    main()
