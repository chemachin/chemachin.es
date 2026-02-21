#!/usr/bin/env python3
"""
Inject EXIF/IPTC metadata into JPEG images for copyright protection.
Adds invisible metadata: Copyright, Creator, and unique ImageUniqueID hash.
"""

import os
import hashlib
from pathlib import Path
from PIL import Image
import piexif

# Configuration
PHOTOS_DIR = Path("docs/photography")
COPYRIGHT = "© 2026 Chemachin"
CREATOR = "Chemachin"


def inject_exif(image_path):
    """Inject EXIF metadata into a JPEG image."""
    try:
        # Load existing EXIF data or create new structure
        try:
            exif_dict = piexif.load(str(image_path))
        except:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

        # Generate unique SHA256 hash of image content
        with open(image_path, 'rb') as f:
            image_hash = hashlib.sha256(f.read()).hexdigest()[:16]

        # Inject Copyright (IFD 0x8298)
        exif_dict["0th"][piexif.ImageIFD.Copyright] = COPYRIGHT.encode('utf-8')

        # Inject Artist/Creator (IFD 0x013B)
        exif_dict["0th"][piexif.ImageIFD.Artist] = CREATOR.encode('utf-8')

        # Inject unique ImageUniqueID as UserComment (preserves through redistribution)
        image_id = f"sha256:{image_hash}"
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = image_id.encode('utf-8')

        # Save image with embedded EXIF
        exif_bytes = piexif.dump(exif_dict)
        
        # Open and save with EXIF
        img = Image.open(image_path)
        img.save(image_path, "jpeg", quality=70, exif=exif_bytes)

        return True, image_id
    except Exception as e:
        return False, str(e)


def main():
    """Main function: process all images in PHOTOS_DIR."""
    if not PHOTOS_DIR.exists():
        print(f"❌ Directory {PHOTOS_DIR} not found")
        return

    jpg_files = sorted(PHOTOS_DIR.glob("*_hu_*.jpg"))
    
    if not jpg_files:
        print(f"❌ No images found in {PHOTOS_DIR}")
        return

    print(f"📸 Found {len(jpg_files)} images to process\n")

    success = 0
    failed = 0

    for idx, image_path in enumerate(jpg_files, 1):
        success_flag, result = inject_exif(image_path)
        
        if success_flag:
            success += 1
            print(f"✓ [{idx:2d}/{len(jpg_files)}] {image_path.name:<40} ID: {result}")
        else:
            failed += 1
            print(f"✗ [{idx:2d}/{len(jpg_files)}] {image_path.name:<40} Error: {result}")

    print(f"\n{'='*70}")
    print(f"Completed: {success}/{len(jpg_files)} ✓ | {failed} ✗")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
