#!/usr/bin/env python3
"""
DXF Reprojection Tool

A user-friendly command-line tool for reprojecting coordinates in DXF (AutoCAD) files
from one coordinate reference system (CRS) to another.

This tool parses DXF files, finds coordinate sets in AcDbFace and 3DFACE sections,
reprojects the X and Y coordinates, and writes out new DXF files with the updated coordinates.
"""

import os
import argparse
import sys
from pathlib import Path
from copy import deepcopy
import pandas as pd
from tqdm import tqdm
from pyproj import Transformer, CRS


def validate_crs(crs_string):
    """
    Validate that a CRS string is valid.
    
    Args:
        crs_string: CRS identifier (e.g., 'EPSG:4326', 'epsg:28354')
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        CRS.from_string(crs_string)
        return True
    except Exception:
        return False


def reproject_dxf_file(input_file, output_file, transformer):
    """
    Reproject a single DXF file.
    
    Args:
        input_file: Path to input DXF file
        output_file: Path to output DXF file
        transformer: pyproj Transformer object for coordinate conversion
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        df = pd.DataFrame()
        df['dxf'] = lines
        
        # Find AcDbFace and 3DFACE markers
        acdb = df.loc[df.dxf.str.contains('AcDbFace', na=False)]
        threed = df.loc[df.dxf.str.contains('3DFACE', na=False)]
        
        acdbindex = acdb.index.tolist()
        threedindex = threed.index.tolist()
        
        # Build dictionary of coordinate sections
        flag = False
        polygondict = {}
        for index, row in df.iterrows():
            if index in acdbindex:
                acdbidx = index
                flag = True
                polygondict[acdbidx] = []
            if index in threedindex or 'ENDSEC' in row['dxf']:
                flag = False
            if flag:
                polygondict[acdbidx].append(row['dxf'])
        
        if not polygondict:
            return False, "No AcDbFace sections found in file"
        
        # Create new dictionary with reprojected coordinates
        polygondict_new = deepcopy(polygondict)
        
        coords_transformed = 0
        for key in polygondict:
            if 'AcDbFace\n' not in polygondict[key]:
                continue
            
            # Validate array length before accessing indices
            if len(polygondict[key]) < 6:
                continue
            
            coords_len = len(polygondict[key]) // 6
            for c in range(coords_len):
                try:
                    # Check bounds before accessing
                    if (c*6 + 6) > len(polygondict[key]):
                        break
                    
                    x = polygondict[key][c*6 + 2]
                    y = polygondict[key][c*6 + 4]
                    xnum = float(x.strip())
                    ynum = float(y.strip())
                    
                    # Transform coordinates
                    new_x, new_y = transformer.transform(xnum, ynum)
                    
                    polygondict_new[key][c*6 + 2] = str(new_x) + "\n"
                    polygondict_new[key][c*6 + 4] = str(new_y) + "\n"
                    coords_transformed += 1
                except (ValueError, IndexError) as e:
                    # Skip invalid coordinates
                    continue
        
        # Write out new file with updated coordinates
        linesnew = deepcopy(lines)
        for key in polygondict_new:
            for i, pdata in enumerate(polygondict_new[key]):
                linesnew[key + i] = polygondict_new[key][i]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for l in linesnew:
                f.write(l)
        
        return True, f"Successfully transformed {coords_transformed} coordinate pairs"
    
    except Exception as e:
        return False, f"Error processing file: {str(e)}"


def main():
    """Main entry point for the DXF reprojection tool."""
    parser = argparse.ArgumentParser(
        description='Reproject DXF files from one coordinate reference system to another.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reproject a single DXF file
  python dxf_reproject.py -i input.dxf -o output.dxf -s EPSG:20254 -t EPSG:28354
  
  # Reproject all DXF files in a directory
  python dxf_reproject.py -i ./input_dir -o ./output_dir -s EPSG:20254 -t EPSG:28354
  
  # Add custom suffix to output files
  python dxf_reproject.py -i ./input_dir -o ./output_dir -s EPSG:20254 -t EPSG:28354 --suffix reprojected

Common EPSG codes:
  EPSG:4326  - WGS 84 (GPS coordinates)
  EPSG:3857  - Web Mercator (Google Maps)
  EPSG:28354 - GDA94 / MGA zone 54
  EPSG:20254 - AGD66 / AMG zone 54
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input DXF file or directory containing DXF files'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output DXF file or directory for reprojected files'
    )
    
    parser.add_argument(
        '-s', '--source-crs',
        required=True,
        help='Source coordinate reference system (e.g., EPSG:20254)'
    )
    
    parser.add_argument(
        '-t', '--target-crs',
        required=True,
        help='Target coordinate reference system (e.g., EPSG:28354)'
    )
    
    parser.add_argument(
        '--suffix',
        default=None,
        help='Suffix to add to output filenames (default: extracted from target CRS)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files without asking'
    )
    
    args = parser.parse_args()
    
    # Validate CRS inputs
    print("Validating coordinate reference systems...")
    if not validate_crs(args.source_crs):
        print(f"Error: Invalid source CRS '{args.source_crs}'")
        return 1
    if not validate_crs(args.target_crs):
        print(f"Error: Invalid target CRS '{args.target_crs}'")
        return 1
    
    print(f"✓ Source CRS: {args.source_crs}")
    print(f"✓ Target CRS: {args.target_crs}")
    
    # Create transformer
    try:
        transformer = Transformer.from_crs(args.source_crs, args.target_crs, always_xy=True)
    except Exception as e:
        print(f"Error creating coordinate transformer: {e}")
        return 1
    
    # Determine suffix for output files
    if args.suffix:
        suffix = args.suffix
    else:
        suffix = args.target_crs.split(':')[-1]
    
    # Check if input is file or directory
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist")
        return 1
    
    # Collect files to process
    files_to_process = []
    
    if input_path.is_file():
        # Single file mode
        if not input_path.suffix.lower() == '.dxf':
            print(f"Error: Input file must be a DXF file")
            return 1
        files_to_process.append((input_path, output_path))
    else:
        # Directory mode
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all DXF files in input directory
        dxf_files = list(input_path.glob('**/*.dxf')) + list(input_path.glob('**/*.DXF'))
        
        if not dxf_files:
            print(f"Error: No DXF files found in '{input_path}'")
            return 1
        
        print(f"Found {len(dxf_files)} DXF file(s) to process")
        
        for dxf_file in dxf_files:
            # Create output filename with suffix
            output_filename = dxf_file.stem + '_' + suffix + '.dxf'
            output_file = output_path / output_filename
            files_to_process.append((dxf_file, output_file))
    
    # Check for existing output files
    if not args.overwrite:
        existing_files = [out for inp, out in files_to_process if out.exists()]
        if existing_files:
            print(f"\nWarning: {len(existing_files)} output file(s) already exist:")
            for f in existing_files[:5]:  # Show first 5
                print(f"  - {f}")
            if len(existing_files) > 5:
                print(f"  ... and {len(existing_files) - 5} more")
            
            response = input("\nOverwrite existing files? (y/n): ")
            if response.lower() != 'y':
                print("Operation cancelled")
                return 0
    
    # Process files
    print(f"\nReprojecting {len(files_to_process)} file(s)...")
    print(f"From: {args.source_crs}")
    print(f"To:   {args.target_crs}\n")
    
    success_count = 0
    error_count = 0
    
    for input_file, output_file in tqdm(files_to_process, desc="Processing files"):
        success, message = reproject_dxf_file(input_file, output_file, transformer)
        
        if success:
            success_count += 1
        else:
            error_count += 1
            tqdm.write(f"✗ {input_file.name}: {message}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  ✓ Success: {success_count} file(s)")
    if error_count > 0:
        print(f"  ✗ Errors:  {error_count} file(s)")
    print(f"{'='*60}")
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
