"""
Run the complete data pipeline with flexible options.

Usage:
    python run_pipeline.py                    # Process from existing CSVs (default)
    python run_pipeline.py --api              # Fetch ALL releases via API, then process (recommended)
    python run_pipeline.py --api -n 3         # Fetch only last 3 releases via API
    python run_pipeline.py --full             # Full pipeline with ALL releases (same as --api)
    
Note: Raw data is never modified, only read. The API automatically fetches
all available releases to ensure complete historical coverage (2015-present).
"""

import sys
import argparse
from pathlib import Path

# Add pipeline directory to path
sys.path.insert(0, str(Path(__file__).parent))

import fetch_usda_api
import process_usda_data


def run_from_raw():
    """Execute pipeline starting from existing raw CSV files (default)."""
    print("=" * 60)
    print("RUNNING PIPELINE FROM EXISTING RAW DATA")
    print("=" * 60)
    print()
    
    # Check if raw data exists
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw"
    
    if not raw_dir.exists() or not list(raw_dir.glob("*.csv")):
        print("⚠ Warning: No CSV files found in data/raw/")
        print("Please run with --api or manually place CSV files in data/raw/")
        return False
    
    csv_files = list(raw_dir.glob("*.csv"))
    print(f"✓ Found {len(csv_files)} CSV file(s) in data/raw/")
    for csv in csv_files:
        print(f"  - {csv.name}")
    
    print("\n" + "-" * 60)
    
    # Process USDA data
    print("\nProcessing data...")
    if process_usda_data.main() != 0:
        print("\n✗ Pipeline failed at processing step!")
        return False
    
    print("\n" + "=" * 60)
    print("✓ PIPELINE COMPLETE!")
    print("=" * 60)
    print("\nProcessed data ready in data/processed/bee_data.csv")
    
    return True


def run_with_api(num_releases: int = None):
    """Execute pipeline with API fetch (recommended method)."""
    print("=" * 60)
    print("RUNNING PIPELINE WITH API FETCH (RECOMMENDED)")
    print("=" * 60)
    print()
    
    # Step 1: Fetch from API
    if num_releases:
        print(f"Step 1: Fetching {num_releases} most recent release(s) from USDA API...")
    else:
        print("Step 1: Fetching ALL releases from USDA API...")
    
    if not fetch_usda_api.main(num_releases=num_releases):
        print("\n✗ Pipeline failed at API fetch step!")
        return False
    
    print("\n" + "-" * 60)
    
    # Step 2: Process USDA data
    print("\nStep 2: Processing USDA data...")
    if process_usda_data.main() != 0:
        print("\n✗ Pipeline failed at processing step!")
        return False
    
    print("\n" + "=" * 60)
    print("✓ PIPELINE COMPLETE!")
    print("=" * 60)
    print("\nProcessed data ready in data/processed/bee_data.csv")
    
    return True


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run the bee data pipeline with flexible options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                  # Process existing CSVs (default)
  python run_pipeline.py --api            # Fetch ALL releases via API (recommended)
  python run_pipeline.py --api -n 3       # Fetch only 3 most recent releases
  python run_pipeline.py --full           # Complete pipeline with ALL releases (same as --api)
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--api',
        action='store_true',
        help='Fetch data via USDA API before processing (fetches ALL releases by default)'
    )
    group.add_argument(
        '--full',
        action='store_true',
        help='Run full pipeline with API fetch (fetches ALL releases by default)'
    )
    
    parser.add_argument(
        '-n', '--num-releases',
        type=int,
        default=None,
        help='Limit to N most recent releases (only with --api, default: fetch ALL)'
    )
    
    args = parser.parse_args()
    
    # Execute based on arguments
    if args.api or args.full:
        # Default to ALL releases (None = all), unless user specifies -n
        num_releases = args.num_releases
        success = run_with_api(num_releases=num_releases)
    else:
        # Default: process from existing raw data
        success = run_from_raw()
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
