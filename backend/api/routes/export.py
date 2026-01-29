"""Export API routes for Power BI and other formats."""
from fastapi import APIRouter, HTTPException, Response, Body, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.dataset import Dataset
from backend.services.data_ingestion import DataIngestionService
from backend.config import settings
import json
import zipfile
import io
import pandas as pd
from datetime import datetime

router = APIRouter(prefix="/api/v1/export", tags=["export"])


class ExportRequest(BaseModel):
    """Request model for dashboard export."""
    widgets: List[Dict[str, Any]]
    datasets: List[Dict[str, Any]]


def convert_widget_to_powerbi_visual(widget: Dict[str, Any], dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a widget to Power BI visual definition."""
    widget_type = widget.get("type", "bar")
    config = widget.get("config", {})
    title = widget.get("title", "Visual")
    
    # Map widget types to Power BI visual types
    visual_type_map = {
        "bar": "columnChart",
        "line": "lineChart",
        "pie": "pieChart",
        "kpi": "card",
        "table": "table"
    }
    
    visual_type = visual_type_map.get(widget_type, "columnChart")
    
    # Get column names
    x_axis = config.get("xAxis") or config.get("x_axis")
    y_axis = config.get("yAxis") or config.get("y_axis")
    
    # Create Power BI visual definition
    visual = {
        "name": f"Visual_{widget.get('id', 'unknown')}",
        "title": title,
        "visualType": visual_type,
        "config": {
            "objects": {}
        },
        "projections": {}
    }
    
    # Add projections based on visual type
    if visual_type == "columnChart" or visual_type == "lineChart":
        if x_axis:
            visual["projections"]["Category"] = {
                "queryRef": "Category",
                "roles": ["Category"]
            }
        if y_axis:
            visual["projections"]["Y"] = {
                "queryRef": "Y",
                "roles": ["Y"]
            }
    elif visual_type == "pieChart":
        if x_axis:
            visual["projections"]["Legend"] = {
                "queryRef": "Legend",
                "roles": ["Legend"]
            }
        if y_axis:
            visual["projections"]["Values"] = {
                "queryRef": "Values",
                "roles": ["Values"]
            }
    elif visual_type == "card":
        if y_axis:
            visual["projections"]["Fields"] = {
                "queryRef": "Fields",
                "roles": ["Fields"]
            }
    elif visual_type == "table":
        # Table shows all columns
        visual["projections"]["Values"] = {
            "queryRef": "Values",
            "roles": ["Values"]
        }
    
    return visual


def create_powerbi_template(export_data: ExportRequest) -> bytes:
    """Create a Power BI Template (.pbit) file with proper structure."""
    widgets = export_data.widgets
    datasets = export_data.datasets
    
    if not datasets:
        raise HTTPException(status_code=400, detail="No datasets to export")
    
    # Use first dataset
    dataset = datasets[0]
    dataset_name = dataset.get("name", "Dataset")
    columns = dataset.get("columns", [])
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Power BI .pbit files require specific file paths and structure
        # The Version file must be at the root with specific content
        
        # 1. Version file (required, must be first or early in the archive)
        # Power BI expects this in a specific format
        version_content = "1.0.0"
        zip_file.writestr("Version", version_content)
        
        # 2. DataModelSchema - Must be valid JSON without BOM
        # Build the M expression with proper newlines (can't use \n in f-string expressions)
        nl = "\n"
        col_names = ', #\"'.join([col.get('name', '') for col in columns])
        m_expression = f"let{nl}    Source = #table(type table [{nl}        #\"{col_names}\"],{nl}        {{}}{nl}    ){nl}in{nl}    Source"
        
        data_model = {
            "name": dataset_name,
            "tables": [
                {
                    "name": dataset_name,
                    "columns": [
                        {
                            "name": col.get("name", ""),
                            "dataType": convert_type_to_powerbi(col.get("type", "string")),
                            "isHidden": False,
                            "formatString": None
                        }
                        for col in columns
                    ],
                    "measures": [],
                    "partitions": [
                        {
                            "name": "Partition",
                            "source": {
                                "type": "m",
                                "expression": m_expression
                            }
                        }
                    ]
                }
            ],
            "relationships": [],
            "cultures": [],
            "version": "1.0"
        }
        
        # Write DataModelSchema as JSON (no BOM, UTF-8)
        data_model_json = json.dumps(data_model, indent=2, ensure_ascii=False)
        zip_file.writestr("DataModelSchema", data_model_json.encode('utf-8'))
        
        # 3. Report/Layout - Report structure
        report_layout = {
            "sections": [
                {
                    "name": "Section1",
                    "displayName": "Dashboard",
                    "visualContainers": [
                        {
                            "x": widget.get("position", {}).get("x", 0) * 50,  # Convert to pixels
                            "y": widget.get("position", {}).get("y", 0) * 50,
                            "z": idx,
                            "width": widget.get("position", {}).get("w", 6) * 50,
                            "height": widget.get("position", {}).get("h", 4) * 50,
                            "config": json.dumps(convert_widget_to_powerbi_visual(widget, dataset))
                        }
                        for idx, widget in enumerate(widgets)
                    ]
                }
            ]
        }
        
        zip_file.writestr("Report/Layout", json.dumps(report_layout, indent=2).encode('utf-8'))
        
        # 4. Metadata - Template metadata
        metadata = {
            "version": "1.0",
            "exportedAt": datetime.now().isoformat(),
            "widgetCount": len(widgets),
            "datasetCount": len(datasets)
        }
        
        zip_file.writestr("Metadata", json.dumps(metadata, indent=2).encode('utf-8'))
        
        # 5. Connections - Data source connections (required for template)
        connections = {
            "version": "1.0",
            "connections": []
        }
        
        zip_file.writestr("Connections", json.dumps(connections, indent=2).encode('utf-8'))
        
        # 6. [Content_Types].xml - Required for Office Open XML format
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="json" ContentType="application/json"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/Version" ContentType="text/plain"/>
    <Override PartName="/DataModelSchema" ContentType="application/json"/>
    <Override PartName="/Report/Layout" ContentType="application/json"/>
    <Override PartName="/Metadata" ContentType="application/json"/>
    <Override PartName="/Connections" ContentType="application/json"/>
</Types>'''
        
        zip_file.writestr("[Content_Types].xml", content_types.encode('utf-8'))
    
    zip_buffer.seek(0)
    return zip_buffer.read()


def convert_type_to_powerbi(data_type: str) -> str:
    """Convert our data type to Power BI data type."""
    type_map = {
        "string": "String",
        "number": "Double",
        "date": "DateTime",
        "boolean": "Boolean"
    }
    return type_map.get(data_type, "String")


def generate_visual_instructions(widget: Dict[str, Any], dataset: Dict[str, Any], visual_def: Dict[str, Any]) -> str:
    """Generate detailed step-by-step instructions for creating a visual in Power BI."""
    widget_type = widget.get("type", "bar")
    config = widget.get("config", {})
    title = widget.get("title", "Visual")
    visual_type = visual_def.get("visualType", "columnChart")
    
    x_axis = config.get("xAxis") or config.get("x_axis")
    y_axis = config.get("yAxis") or config.get("y_axis")
    
    instructions = f"To create '{title}':\n"
    instructions += f"1. Click on the '{visual_type}' visual type in the Visualizations pane\n"
    instructions += f"2. Drag and drop fields from the Fields pane:\n"
    
    if visual_type == "columnChart" or visual_type == "lineChart":
        if x_axis:
            instructions += f"   - Drag '{x_axis}' to the Axis/X-axis field\n"
        if y_axis:
            instructions += f"   - Drag '{y_axis}' to the Values/Y-axis field\n"
    elif visual_type == "pieChart":
        if x_axis:
            instructions += f"   - Drag '{x_axis}' to the Legend field\n"
        if y_axis:
            instructions += f"   - Drag '{y_axis}' to the Values field\n"
    elif visual_type == "card":
        if y_axis:
            instructions += f"   - Drag '{y_axis}' to the Fields field\n"
    elif visual_type == "table":
        instructions += f"   - Drag all columns you want to display to the Values field\n"
    
    instructions += f"3. The visual will automatically update with your data\n"
    instructions += f"4. You can customize colors, titles, and formatting in the Format pane\n"
    
    return instructions


def create_powerbi_pbix(export_data: ExportRequest, db: Session) -> bytes:
    """Create a Power BI .pbix file with embedded data."""
    widgets = export_data.widgets
    datasets = export_data.datasets
    
    if not datasets:
        raise HTTPException(status_code=400, detail="No datasets to export")
    
    # Get first dataset
    frontend_dataset = datasets[0]
    dataset_id = frontend_dataset.get("id")
    
    # Load actual data from database
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found in database")
    
    # Load the actual CSV data
    ingestion_service = DataIngestionService()
    df = ingestion_service.load_dataset(dataset.file_path)
    
    dataset_name = dataset.filename.replace('.csv', '').replace('.xlsx', '')
    columns = dataset.columns
    
    # Create in-memory ZIP file for .pbix
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Version file (required) - Power BI expects plain text version number
        # Must be the first file and in plain text format (not binary)
        # Power BI Desktop expects format like "1.0" or "1.1" etc.
        version_content = "1.0"  # Plain text version string
        zip_file.writestr("Version", version_content.encode('ascii'))  # ASCII encoding for version
        
        # 2. DataModelSchema - with actual table definition
        data_model = {
            "name": dataset_name,
            "tables": [
                {
                    "name": dataset_name,
                    "columns": [
                        {
                            "name": col.get("name", ""),
                            "dataType": convert_type_to_powerbi(col.get("type", "string")),
                            "isHidden": False,
                            "formatString": None,
                            "isNullable": True
                        }
                        for col in columns
                    ],
                    "measures": [],
                    "partitions": [
                        {
                            "name": "Partition",
                            "source": {
                                "type": "m",
                                "expression": f"let\n    Source = Csv.Document(File.Contents(\"data.csv\"),[Delimiter=\",\", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\nin\n    #\"Promoted Headers\""
                            }
                        }
                    ]
                }
            ],
            "relationships": [],
            "cultures": [],
            "version": "1.0"
        }
        
        zip_file.writestr("DataModelSchema", json.dumps(data_model, indent=2).encode('utf-8'))
        
        # 3. Embed actual CSV data as a separate file that Power BI can reference
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        # Store CSV data that can be loaded by Power BI
        zip_file.writestr("Data/data.csv", csv_content.encode('utf-8-sig'))  # UTF-8 with BOM
        
        # Also create DataMashup with M query that references the CSV
        mashup_query = f'''let
    Source = Csv.Document(File.Contents("Data/data.csv"),[Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{'''
        
        # Add column type conversions
        type_conversions = []
        for col in columns:
            col_name = col.get("name", "")
            col_type = col.get("type", "string")
            pbi_type = {
                "string": "type text",
                "number": "type number",
                "date": "type datetime",
                "boolean": "type logical"
            }.get(col_type, "type text")
            type_conversions.append(f'"{col_name}", {pbi_type}')
        
        mashup_query += ', '.join(type_conversions)
        mashup_query += '}})'
        mashup_query += '\nin\n    #"Changed Type"'
        
        zip_file.writestr("DataMashup", mashup_query.encode('utf-8'))
        
        # 4. Report/Layout - Visual definitions
        report_layout = {
            "sections": [
                {
                    "name": "Section1",
                    "displayName": "Dashboard",
                    "visualContainers": [
                        {
                            "x": widget.get("position", {}).get("x", 0) * 50,
                            "y": widget.get("position", {}).get("y", 0) * 50,
                            "z": idx,
                            "width": widget.get("position", {}).get("w", 6) * 50,
                            "height": widget.get("position", {}).get("h", 4) * 50,
                            "config": json.dumps(convert_widget_to_powerbi_visual(widget, frontend_dataset))
                        }
                        for idx, widget in enumerate(widgets)
                    ]
                }
            ]
        }
        
        zip_file.writestr("Report/Layout", json.dumps(report_layout, indent=2).encode('utf-8'))
        
        # 5. Metadata
        metadata = {
            "version": "1.0",
            "exportedAt": datetime.now().isoformat(),
            "visualCount": len(widgets),
            "rowCount": len(df)
        }
        zip_file.writestr("Metadata", json.dumps(metadata, indent=2).encode('utf-8'))
        
        # 6. [Content_Types].xml
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="json" ContentType="application/json"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Default Extension="csv" ContentType="text/csv"/>
    <Override PartName="/Version" ContentType="text/plain"/>
    <Override PartName="/DataModelSchema" ContentType="application/json"/>
    <Override PartName="/DataMashup" ContentType="text/csv"/>
    <Override PartName="/Report/Layout" ContentType="application/json"/>
    <Override PartName="/Metadata" ContentType="application/json"/>
</Types>'''
        zip_file.writestr("[Content_Types].xml", content_types.encode('utf-8'))
    
    zip_buffer.seek(0)
    return zip_buffer.read()


@router.post("/powerbi")
async def export_to_powerbi(request: ExportRequest, db: Session = Depends(get_db)):
    """Export dashboard as Power BI .pbix file with embedded data.
    
    This creates a .pbix file that can be directly opened in Power BI Desktop
    with all data and visuals included.
    """
    try:
        # Create Power BI .pbix file with embedded data
        pbix_content = create_powerbi_pbix(request, db)
        
        # Return as downloadable file
        return Response(
            content=pbix_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=dashboard-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pbix",
                "Content-Type": "application/octet-stream"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error exporting to Power BI: {str(e)}")


@router.post("/powerbi/api")
async def export_to_powerbi_api(request: ExportRequest, db: Session = Depends(get_db)):
    """Export dashboard directly to Power BI Service using REST API.
    
    This creates the dashboard in Power BI Service (cloud) with all data and visuals.
    Requires Power BI API credentials to be configured.
    """
    try:
        if not settings.powerbi_enabled:
            raise HTTPException(
                status_code=400,
                detail="Power BI API is not enabled. Set POWERBI_ENABLED=true and configure credentials in .env"
            )
        
        from backend.services.powerbi_api import PowerBIClient
        
        # Initialize Power BI client
        powerbi_client = PowerBIClient()
        
        # Get dataset data
        frontend_dataset = request.datasets[0]
        dataset_id = frontend_dataset.get("id")
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Load data
        ingestion_service = DataIngestionService()
        df = ingestion_service.load_dataset(dataset.file_path)
        
        dataset_name = dataset.filename.replace('.csv', '').replace('.xlsx', '')
        columns = dataset.columns
        
        # Create dataset in Power BI
        tables = [{
            "name": dataset_name,
            "columns": [
                {
                    "name": col.get("name", ""),
                    "dataType": convert_type_to_powerbi(col.get("type", "string"))
                }
                for col in columns
            ]
        }]
        
        powerbi_dataset_id = powerbi_client.create_dataset(dataset_name, tables)
        
        # Push data to Power BI
        # Convert DataFrame to rows
        rows = df.head(10000).to_dict('records')  # Limit to 10k rows for API
        # Convert to Power BI format
        powerbi_rows = []
        for row in rows:
            powerbi_row = {}
            for col in columns:
                col_name = col.get("name", "")
                value = row.get(col_name)
                # Convert to appropriate type
                if pd.isna(value):
                    powerbi_row[col_name] = None
                elif hasattr(value, 'isoformat'):  # datetime
                    powerbi_row[col_name] = value.isoformat()
                else:
                    powerbi_row[col_name] = value
            powerbi_rows.append(powerbi_row)
        
        # Push data in batches
        batch_size = 1000
        for i in range(0, len(powerbi_rows), batch_size):
            batch = powerbi_rows[i:i + batch_size]
            powerbi_client.push_data(powerbi_dataset_id, dataset_name, batch)
        
        # Create .pbix file for import (with visuals)
        pbix_content = create_powerbi_pbix(request, db)
        
        # Import .pbix to Power BI Service
        import_result = powerbi_client.import_pbix_file(pbix_content, f"{dataset_name}_Dashboard")
        
        return {
            "success": True,
            "message": "Dashboard imported to Power BI Service",
            "import_id": import_result.get("import_id"),
            "status": import_result.get("status"),
            "dataset_id": powerbi_dataset_id,
            "instructions": f"Check import status using import_id: {import_result.get('import_id')}. Once complete, your dashboard will be available in Power BI Service."
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error exporting to Power BI API: {str(e)}")


@router.get("/powerbi/api/status/{import_id}")
async def get_powerbi_import_status(import_id: str):
    """Get the status of a Power BI import operation."""
    try:
        if not settings.powerbi_enabled:
            raise HTTPException(status_code=400, detail="Power BI API is not enabled")
        
        from backend.services.powerbi_api import PowerBIClient
        powerbi_client = PowerBIClient()
        
        status = powerbi_client.get_import_status(import_id)
        
        return {
            "import_id": import_id,
            "status": status.get("importState"),
            "created_at": status.get("createdDateTime"),
            "updated_at": status.get("updatedDateTime"),
            "report_id": status.get("reports", [{}])[0].get("id") if status.get("reports") else None,
            "dataset_id": status.get("datasets", [{}])[0].get("id") if status.get("datasets") else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking import status: {str(e)}")


@router.post("/csv")
async def export_to_csv(request: ExportRequest, db: Session = Depends(get_db)):
    """Export dataset as CSV file with actual data."""
    try:
        datasets = request.datasets
        
        if not datasets:
            raise HTTPException(status_code=400, detail="No datasets to export")
        
        # Get first dataset
        frontend_dataset = datasets[0]
        dataset_id = frontend_dataset.get("id")
        
        # Load actual data from database
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found in database")
        
        # Load the actual CSV data
        ingestion_service = DataIngestionService()
        df = ingestion_service.load_dataset(dataset.file_path)
        
        dataset_name = dataset.filename.replace('.csv', '').replace('.xlsx', '')
        
        # Create CSV with all data
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        return Response(
            content=csv_content.encode('utf-8-sig'),  # UTF-8 with BOM for Excel/Power BI compatibility
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={dataset_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error exporting to CSV: {str(e)}")


@router.post("/powerbi/json")
async def export_to_powerbi_json(request: ExportRequest):
    """Export dashboard as Power BI JSON definition.
    
    This JSON can be used with the conversion script (scripts/json_to_powerbi.py)
    or as a reference to manually recreate the dashboard in Power BI Desktop.
    """
    try:
        widgets = request.widgets
        datasets = request.datasets
        
        if not datasets:
            raise HTTPException(status_code=400, detail="No datasets to export")
        
        dataset = datasets[0]
        dataset_name = dataset.get("name", "Dataset")
        columns = dataset.get("columns", [])
        
        # Create comprehensive Power BI JSON definition
        powerbi_json = {
            "version": "1.0",
            "exportedAt": datetime.now().isoformat(),
            "metadata": {
                "datasetName": dataset_name,
                "visualCount": len(widgets),
                "exportFormat": "Power BI JSON Definition"
            },
            "dataset": {
                "name": dataset_name,
                "columns": [
                    {
                        "name": col.get("name", ""),
                        "type": col.get("type", "string"),
                        "dataType": convert_type_to_powerbi(col.get("type", "string")),
                        "description": f"Column: {col.get('name', '')}"
                    }
                    for col in columns
                ]
            },
            "visuals": [
                {
                    **convert_widget_to_powerbi_visual(widget, dataset),
                    "position": widget.get("position", {}),
                    "datasetId": widget.get("datasetId", dataset_name)
                }
                for widget in widgets
            ],
            "layout": {
                "sections": [
                    {
                        "name": "Section 1",
                        "displayName": "Dashboard",
                        "visualContainers": [
                            {
                                "visualId": widget.get("id", f"visual_{idx}"),
                                "x": widget.get("position", {}).get("x", 0),
                                "y": widget.get("position", {}).get("y", 0),
                                "z": idx,
                                "width": widget.get("position", {}).get("w", 6),
                                "height": widget.get("position", {}).get("h", 4),
                                "visualType": convert_widget_to_powerbi_visual(widget, dataset).get("visualType", "columnChart"),
                                "title": widget.get("title", "Visual"),
                                "config": convert_widget_to_powerbi_visual(widget, dataset)
                            }
                            for idx, widget in enumerate(widgets)
                        ]
                    }
                ]
            },
            "instructions": {
                "step1": "Import your CSV data into Power BI Desktop",
                "step2": "Use the 'visuals' array to recreate each visualization",
                "step3": "Use the 'layout' information to position visuals",
                "step4": "Save as .pbix file",
                "alternative": "Use scripts/json_to_powerbi.py to generate detailed instructions"
            },
            "detailedVisualInstructions": [
                {
                    "visualId": widget.get("id", f"visual_{idx}"),
                    "step": idx + 1,
                    "title": widget.get("title", f"Visual {idx + 1}"),
                    "type": convert_widget_to_powerbi_visual(widget, dataset).get("visualType", "columnChart"),
                    "instructions": generate_visual_instructions(widget, dataset, convert_widget_to_powerbi_visual(widget, dataset)),
                    "fieldMappings": {
                        "xAxis": widget.get("config", {}).get("xAxis") or widget.get("config", {}).get("x_axis"),
                        "yAxis": widget.get("config", {}).get("yAxis") or widget.get("config", {}).get("y_axis")
                    }
                }
                for idx, widget in enumerate(widgets)
            ]
        }
        
        return Response(
            content=json.dumps(powerbi_json, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=powerbi-dashboard-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to Power BI JSON: {str(e)}")

