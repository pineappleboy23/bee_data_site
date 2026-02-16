"""
Fetch USDA Honey Bee Colony data using the ESMIS API.

This is the recommended method - it uses the official USDA API
to get direct download links for all bee colony reports.
"""

import requests
import zipfile
import io
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


API_ENDPOINT = "https://esmis.nal.usda.gov/api/v1/release/findByPubId/1585"
CHUNK_SIZE = 8192  # For streaming downloads


def fetch_releases(num_releases: Optional[int] = None) -> List[Dict]:
    """
    Fetch bee colony releases from USDA ESMIS API.
    
    Args:
        num_releases: Number of most recent releases to fetch. None = all releases.
        
    Returns:
        List of release dictionaries with metadata and file URLs
    """
    try:
        print(f"📡 Calling USDA API: {API_ENDPOINT}")
        response = requests.get(API_ENDPOINT, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        print(f"✓ API returned {len(results)} total releases")
        
        if num_releases:
            results = results[:num_releases]
            print(f"  Limiting to {num_releases} most recent release(s)")
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error calling API: {e}")
        return []
    except Exception as e:
        print(f"✗ Error processing API response: {e}")
        return []


def download_and_extract_zip(url: str, output_dir: Path, release_name: str = "") -> List[Path]:
    """
    Download ZIP file from URL and extract CSVs to a subdirectory.
    
    Args:
        url: Direct URL to ZIP file
        output_dir: Base directory (each release extracts to output_dir/release_subdir/)
        release_name: Name/identifier for the release (for logging)
        
    Returns:
        List of paths to extracted CSV files
    """
    # Extract zip filename without extension to use as subdirectory
    zip_filename = url.split('/')[-1]
    release_subdir = zip_filename.replace('.zip', '')
    
    # Create subdirectory for this release
    extract_dir = output_dir / release_subdir
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download with streaming for large files
        print(f"  ⬇ Downloading: {url.split('/')[-1]}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))
        if total_size:
            print(f"    Size: {total_size / 1024:.1f} KB")
        
        # Read the entire response into memory
        zip_data = io.BytesIO()
        downloaded = 0
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                zip_data.write(chunk)
                downloaded += len(chunk)
        
        print(f"  ✓ Downloaded {downloaded / 1024:.1f} KB")
        
        # Extract CSVs
        extracted_files = []
        zip_data.seek(0)
        
        with zipfile.ZipFile(zip_data) as zf:
            csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
            
            if not csv_files:
                print(f"  ⚠ No CSV files found in ZIP")
                return []
            
            print(f"  📦 Extracting {len(csv_files)} CSV file(s) to {release_subdir}/...")
            
            for filename in csv_files:
                # Extract to release subdirectory
                output_path = extract_dir / Path(filename).name
                
                with zf.open(filename) as source:
                    with open(output_path, 'wb') as target:
                        target.write(source.read())
                
                extracted_files.append(output_path)
                print(f"    ✓ {output_path.name}")
        
        return extracted_files
        
    except zipfile.BadZipFile:
        print(f"  ✗ Error: Downloaded file is not a valid ZIP")
        return []
    except Exception as e:
        print(f"  ✗ Error downloading/extracting: {e}")
        return []


def get_zip_url(release: Dict) -> Optional[str]:
    """
    Extract ZIP file URL from release data.
    
    Args:
        release: Release dictionary from API
        
    Returns:
        URL of ZIP file, or None if not found
    """
    files = release.get('files', [])
    for file_url in files:
        if file_url.endswith('.zip'):
            return file_url
    return None


def main(num_releases: int = 1) -> bool:
    """
    Main execution function.
    
    Args:
        num_releases: Number of most recent releases to download (default: 1)
        
    Returns:
        True if successful, False otherwise
    """
    print("=" * 70)
    print("USDA BEE DATA API FETCHER")
    print("=" * 70)
    print()
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    raw_data_dir = base_dir / "data" / "raw"
    
    # Note: Each release extracts to its own subdirectory (e.g., raw/hcny0825/)
    # This preserves all historical data without overwrites
    
    # Fetch releases from API
    releases = fetch_releases(num_releases)
    
    if not releases:
        print("\n✗ No releases found")
        return False
    
    print("\n" + "-" * 70)
    print("DOWNLOADING RELEASES")
    print("-" * 70)
    
    # Download and extract each release
    all_extracted = []
    
    for i, release in enumerate(releases, 1):
        release_date = release.get('release_datetime', 'Unknown')
        title = release.get('title', 'Unknown')
        release_id = release.get('id', 'Unknown')
        
        print(f"\n[{i}/{len(releases)}] {title}")
        print(f"  📅 Released: {release_date}")
        print(f"  🆔 ID: {release_id}")
        
        # Get ZIP file URL
        zip_url = get_zip_url(release)
        
        if not zip_url:
            print(f"  ⚠ No ZIP file found for this release")
            continue
        
        # Download and extract
        extracted = download_and_extract_zip(
            zip_url, 
            raw_data_dir, 
            release_name=f"{title}_{release_date}"
        )
        
        all_extracted.extend(extracted)
    
    # Summary
    print("\n" + "=" * 70)
    if all_extracted:
        print("✓ SUCCESS")
        print("=" * 70)
        print(f"\nExtracted {len(all_extracted)} CSV file(s) to: {raw_data_dir}")
        print("\nFiles:")
        for f in all_extracted:
            print(f"  • {f.name}")
        print("\n💡 Next step: python pipeline/process_usda_data.py")
        return True
    else:
        print("✗ FAILED")
        print("=" * 70)
        print("\nNo CSV files were extracted.")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch USDA bee colony data using the ESMIS API"
    )
    parser.add_argument(
        '-n', '--num-releases',
        type=int,
        default=1,
        help='Number of most recent releases to download (default: 1)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all available releases'
    )
    
    args = parser.parse_args()
    
    num = None if args.all else args.num_releases
    
    try:
        success = main(num_releases=num)
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
