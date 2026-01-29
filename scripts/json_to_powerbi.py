"""
Script to convert JSON dashboard definition to Power BI .pbix file.

This script uses the exported JSON definition to create a Power BI report.
Note: This requires Power BI REST API or manual conversion.

Usage:
    python scripts/json_to_powerbi.py <json_file> <output.pbix>
"""

import json
import sys
import os
from pathlib import Path

def convert_json_to_powerbi_instructions(json_file: str, output_file: str):
    """
    Convert JSON definition to Power BI format.
    
    Since Power BI .pbix files are complex binary formats, this script
    provides instructions and creates a data model that can be imported.
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_def = json.load(f)
    
    print(f"📊 Dashboard Definition Loaded:")
    print(f"   - Dataset: {dashboard_def.get('dataset', {}).get('name', 'Unknown')}")
    print(f"   - Visuals: {len(dashboard_def.get('visuals', []))}")
    print(f"\n📝 Creating Power BI import instructions...")
    
    # Create a detailed instruction file
    instructions = f"""# Power BI Dashboard Import Instructions

## Dashboard Information
- Dataset: {dashboard_def.get('dataset', {}).get('name', 'Unknown')}
- Visuals: {len(dashboard_def.get('visuals', []))}
- Exported: {dashboard_def.get('exportedAt', 'Unknown')}

## Step 1: Import Data
1. Open Power BI Desktop
2. Click "Get Data" > "Text/CSV"
3. Select your CSV file
4. Click "Load"

## Step 2: Create Visuals

"""
    
    # Add instructions for each visual
    for idx, visual in enumerate(dashboard_def.get('visuals', []), 1):
        visual_type = visual.get('visualType', 'unknown')
        title = visual.get('title', f'Visual {idx}')
        
        instructions += f"### Visual {idx}: {title}\n"
        instructions += f"- Type: {visual_type}\n"
        
        # Add field mappings
        projections = visual.get('projections', {})
        if projections:
            instructions += "- Fields:\n"
            for role, projection in projections.items():
                instructions += f"  - {role}: {projection.get('queryRef', 'N/A')}\n"
        
        instructions += "\n"
    
    instructions += """
## Step 3: Apply Layout
Use the layout information from the JSON file to position your visuals.

## Step 4: Save
Save your report as a .pbix file.

---
Note: This is a manual process. For automated import, use Power BI REST API.
"""
    
    # Save instructions
    instructions_file = output_file.replace('.pbix', '_instructions.md')
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Instructions saved to: {instructions_file}")
    print(f"\n💡 Next Steps:")
    print(f"   1. Open Power BI Desktop")
    print(f"   2. Import your CSV data")
    print(f"   3. Follow instructions in: {instructions_file}")
    
    return instructions_file


def create_powerbi_dax_queries(json_file: str):
    """Create DAX queries that can be used in Power BI."""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_def = json.load(f)
    
    dataset = dashboard_def.get('dataset', {})
    columns = dataset.get('columns', [])
    
    # Create table definition
    dax_queries = []
    
    # Create a table query
    table_name = dataset.get('name', 'Table1')
    column_defs = []
    for col in columns:
        col_name = col.get('name', '')
        col_type = col.get('type', 'string')
        dax_type = {
            'string': 'STRING',
            'number': 'DOUBLE',
            'date': 'DATETIME',
            'boolean': 'BOOLEAN'
        }.get(col_type, 'STRING')
        column_defs.append(f"    \"{col_name}\" {dax_type}")
    
    dax_table = f"""// Table Definition for {table_name}
EVALUATE
SUMMARIZECOLUMNS(
{chr(10).join(column_defs)}
)"""
    
    dax_queries.append(dax_table)
    
    # Save DAX queries
    dax_file = json_file.replace('.json', '_dax.txt')
    with open(dax_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(dax_queries))
    
    print(f"✅ DAX queries saved to: {dax_file}")
    return dax_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/json_to_powerbi.py <json_file> [output.pbix]")
        print("\nExample:")
        print("  python scripts/json_to_powerbi.py dashboard.json dashboard.pbix")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else json_file.replace('.json', '.pbix')
    
    if not os.path.exists(json_file):
        print(f"❌ Error: File not found: {json_file}")
        sys.exit(1)
    
    print("🔄 Converting JSON to Power BI format...\n")
    
    # Create instructions
    instructions_file = convert_json_to_powerbi_instructions(json_file, output_file)
    
    # Create DAX queries
    dax_file = create_powerbi_dax_queries(json_file)
    
    print(f"\n✅ Conversion complete!")
    print(f"   - Instructions: {instructions_file}")
    print(f"   - DAX Queries: {dax_file}")
    print(f"\n⚠️  Note: Direct .pbix creation requires Power BI REST API.")
    print(f"   Use the instructions file to manually create the dashboard.")


