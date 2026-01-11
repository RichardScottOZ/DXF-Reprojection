# DXF Reprojection - Quick Start Guide

This guide will help you get started with the DXF Reprojection tool quickly.

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
```

## Quick Examples

### Example 1: Convert a Single File

Convert a DXF file from AGD66 (EPSG:20254) to GDA94 (EPSG:28354):

```bash
python dxf_reproject.py -i my_survey.dxf -o my_survey_gda94.dxf -s EPSG:20254 -t EPSG:28354
```

### Example 2: Batch Convert Multiple Files

Convert all DXF files in a directory:

```bash
python dxf_reproject.py -i ./input_folder -o ./output_folder -s EPSG:20254 -t EPSG:28354
```

This will:
- Process all `.dxf` files in `input_folder`
- Save reprojected files to `output_folder`
- Add the suffix `_28354` to each output filename

### Example 3: Convert to WGS84 (GPS Coordinates)

```bash
python dxf_reproject.py -i survey.dxf -o survey_wgs84.dxf -s EPSG:28354 -t EPSG:4326
```

### Example 4: Custom Output Suffix

Use a custom suffix instead of the default EPSG code:

```bash
python dxf_reproject.py -i ./input -o ./output -s EPSG:20254 -t EPSG:28354 --suffix reprojected
```

Output files will be named like: `filename_reprojected.dxf`

### Example 5: Overwrite Without Asking

Skip the overwrite confirmation prompt:

```bash
python dxf_reproject.py -i ./input -o ./output -s EPSG:20254 -t EPSG:28354 --overwrite
```

## Common Use Cases

### Australian Coordinate Systems

**AGD66 to GDA94 (Australian surveys)**
```bash
python dxf_reproject.py -i input.dxf -o output.dxf -s EPSG:20254 -t EPSG:28354
```

**GDA94 to WGS84 (for GPS/web mapping)**
```bash
python dxf_reproject.py -i input.dxf -o output.dxf -s EPSG:28354 -t EPSG:4326
```

### Web Mapping

**Convert to Web Mercator (Google Maps, OpenStreetMap)**
```bash
python dxf_reproject.py -i input.dxf -o output.dxf -s EPSG:4326 -t EPSG:3857
```

## Finding Your EPSG Code

If you're not sure what EPSG code to use:

1. Visit [epsg.io](https://epsg.io/)
2. Search for your coordinate system by name or region
3. Use the EPSG code (e.g., `EPSG:28354`)

Common codes for Australia:
- `EPSG:4326` - WGS 84 (lat/lon)
- `EPSG:28354` - GDA94 / MGA zone 54
- `EPSG:28355` - GDA94 / MGA zone 55
- `EPSG:28356` - GDA94 / MGA zone 56
- `EPSG:20254` - AGD66 / AMG zone 54 (legacy)

## Troubleshooting

### "Invalid source CRS" error
Make sure your CRS string is in the format `EPSG:XXXXX` (with correct case and colon).

### "No AcDbFace sections found" warning
Your DXF file may not contain 3D face data, or it may use a different format. The tool currently only processes `AcDbFace` and `3DFACE` entities.

### Files not being processed
Make sure:
- Files have `.dxf` extension (case-insensitive)
- You have read permissions for input files
- You have write permissions for the output directory

## Getting Help

To see all available options:
```bash
python dxf_reproject.py --help
```

## Performance Notes

- For files with millions of coordinates, processing may take several minutes
- Progress bars show current status during batch operations
- Consider processing files in smaller batches if dealing with very large datasets
