# DXF-Reprojection

A user-friendly command-line tool for reprojecting coordinates in DXF (AutoCAD) files from one coordinate reference system (CRS) to another.

## Overview

This tool parses DXF files, identifies coordinate sets in AcDbFace and 3DFACE sections, reprojects the X and Y coordinates using pyproj, and writes out new DXF files with the updated coordinates.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/RichardScottOZ/DXF-Reprojection.git
cd DXF-Reprojection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Reproject a single DXF file:
```bash
python dxf_reproject.py -i input.dxf -o output.dxf -s EPSG:20254 -t EPSG:28354
```

Reproject all DXF files in a directory:
```bash
python dxf_reproject.py -i ./input_dir -o ./output_dir -s EPSG:20254 -t EPSG:28354
```

### Command-Line Options

```
  -i, --input INPUT          Input DXF file or directory containing DXF files
  -o, --output OUTPUT        Output DXF file or directory for reprojected files
  -s, --source-crs CRS       Source coordinate reference system (e.g., EPSG:20254)
  -t, --target-crs CRS       Target coordinate reference system (e.g., EPSG:28354)
  --suffix SUFFIX            Suffix to add to output filenames (default: extracted from target CRS)
  --overwrite                Overwrite existing output files without asking
  -h, --help                 Show help message and exit
```

### Examples

**Example 1: Convert from AGD66 to GDA94**
```bash
python dxf_reproject.py -i survey.dxf -o survey_gda94.dxf -s EPSG:20254 -t EPSG:28354
```

**Example 2: Batch process multiple files**
```bash
python dxf_reproject.py -i ./original_files -o ./reprojected_files -s EPSG:20254 -t EPSG:28354
```

**Example 3: Use custom suffix**
```bash
python dxf_reproject.py -i ./input -o ./output -s EPSG:20254 -t EPSG:28354 --suffix wgs84
```

### Common EPSG Codes

- `EPSG:4326` - WGS 84 (GPS coordinates)
- `EPSG:3857` - Web Mercator (used by Google Maps, OpenStreetMap)
- `EPSG:28354` - GDA94 / MGA zone 54 (Australia)
- `EPSG:20254` - AGD66 / AMG zone 54 (Australia, legacy)
- `EPSG:32754` - WGS 84 / UTM zone 54S

You can find more EPSG codes at [epsg.io](https://epsg.io/)

## Features

- ✅ User-friendly command-line interface
- ✅ Support for single file or batch directory processing
- ✅ Progress bars for batch operations
- ✅ CRS validation before processing
- ✅ Error handling and informative messages
- ✅ Automatic output filename generation with CRS suffix
- ✅ Safety check to prevent overwriting files accidentally

## How It Works

The tool uses a text-based parsing approach:

1. Reads the DXF file as text
2. Identifies coordinate sections marked by `AcDbFace` and `3DFACE` tags
3. Extracts X, Y coordinate pairs
4. Reprojects coordinates using pyproj's Transformer
5. Replaces original coordinates with reprojected values
6. Writes out the updated DXF file

**Note:** This approach works well for files with reasonable numbers of coordinates. For DXF files with millions of coordinates, consider a vectorized/parallelized version for better performance.

## Jupyter Notebook

The original Jupyter notebook (`DXF-Parsing.ipynb`) is still available for interactive use and experimentation.

## Requirements

- Python 3.6+
- pandas
- pyproj
- tqdm

## License

This project is open source. Please check the repository for license details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
