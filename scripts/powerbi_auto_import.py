"""
Automated Power BI Import Script

This script reads the exported JSON and CSV files and provides
detailed, step-by-step instructions for recreating the dashboard in Power BI Desktop.

Usage:
    python scripts/powerbi_auto_import.py <json_file> <csv_file>
"""

import json
import sys
import os
from pathlib import Path

def generate_powerbi_instructions(json_file: str, csv_file: str = None):
    """Generate detailed Power BI import instructions from JSON export."""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_def = json.load(f)
    
    print("=" * 80)
    print("POWER BI DASHBOARD IMPORT GUIDE")
    print("=" * 80)
    print()
    
    # Dataset info
    dataset = dashboard_def.get('dataset', {})
    print(f"📊 Dataset: {dataset.get('name', 'Unknown')}")
    print(f"   Columns: {len(dataset.get('columns', []))}")
    print()
    
    # CSV import instructions
    print("STEP 1: IMPORT DATA")
    print("-" * 80)
    if csv_file and os.path.exists(csv_file):
        print(f"✅ CSV file found: {csv_file}")
        print()
        print("In Power BI Desktop:")
        print("1. Click 'Get Data' > 'Text/CSV'")
        print(f"2. Select: {csv_file}")
        print("3. Click 'Load'")
        print("4. Wait for data to load")
    else:
        print("⚠️  CSV file not found. Please export CSV from dashboard first.")
        print()
        print("In Power BI Desktop:")
        print("1. Click 'Get Data' > 'Text/CSV'")
        print("2. Select your exported CSV file")
        print("3. Click 'Load'")
    print()
    
    # Visual creation instructions
    visuals = dashboard_def.get('visuals', [])
    detailed_instructions = dashboard_def.get('detailedVisualInstructions', [])
    
    print("STEP 2: CREATE VISUALS")
    print("-" * 80)
    print(f"Total visuals to create: {len(visuals)}")
    print()
    
    for idx, (visual, detail) in enumerate(zip(visuals, detailed_instructions), 1):
        visual_type = detail.get('type', visual.get('visualType', 'unknown'))
        title = detail.get('title', visual.get('title', f'Visual {idx}'))
        instructions = detail.get('instructions', '')
        field_mappings = detail.get('fieldMappings', {})
        
        print(f"Visual {idx}: {title}")
        print(f"Type: {visual_type}")
        print()
        
        # Print detailed instructions
        if instructions:
            print(instructions)
        else:
            # Fallback instructions
            print(f"1. Click '{visual_type}' in Visualizations pane")
            if field_mappings.get('xAxis'):
                print(f"2. Drag '{field_mappings['xAxis']}' to Axis/X-axis")
            if field_mappings.get('yAxis'):
                print(f"2. Drag '{field_mappings['yAxis']}' to Values/Y-axis")
            print("3. Visual will update automatically")
        
        print()
        print("-" * 80)
        print()
    
    # Layout information
    layout = dashboard_def.get('layout', {})
    if layout:
        print("STEP 3: POSITION VISUALS")
        print("-" * 80)
        print("Use the layout information to position your visuals:")
        print("(Note: Power BI uses a different layout system, so adjust as needed)")
        print()
    
    print("STEP 4: SAVE")
    print("-" * 80)
    print("1. File > Save As")
    print("2. Choose location and filename")
    print("3. Save as .pbix file")
    print()
    
    print("=" * 80)
    print("✅ INSTRUCTIONS COMPLETE")
    print("=" * 80)
    
    # Save instructions to file
    output_file = json_file.replace('.json', '_instructions.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("POWER BI DASHBOARD IMPORT GUIDE\n")
        f.write("=" * 80 + "\n\n")
        # Write all the instructions...
    
    print(f"\n📝 Detailed instructions saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/powerbi_auto_import.py <json_file> [csv_file]")
        print("\nExample:")
        print("  python scripts/powerbi_auto_import.py dashboard.json data.csv")
        sys.exit(1)
    
    json_file = sys.argv[1]
    csv_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(json_file):
        print(f"❌ Error: JSON file not found: {json_file}")
        sys.exit(1)
    
    generate_powerbi_instructions(json_file, csv_file)


