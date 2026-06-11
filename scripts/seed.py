#!/usr/bin/env python3
"""
Seed script for ML layer demo data.

Creates synthetic demo data for testing without Supabase.
All data is clearly labeled as synthetic demo data.

Usage:
    python scripts/seed.py
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.embeddings import get_demo_data


def main():
    """Generate and save demo data to JSON file."""
    print("Generating synthetic demo data...")
    
    demo_data = get_demo_data()
    
    # Save to demo/demo_cases.json
    output_path = Path(__file__).parent.parent / "demo" / "demo_cases.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print(f"Demo data saved to {output_path}")
    print(f"\nSummary:")
    print(f"  - Users: {len(demo_data['users'])}")
    print(f"  - Products: {len(demo_data['products'])}")
    print(f"  - Deals: {len(demo_data['deals'])}")
    print(f"  - Events: {len(demo_data['events'])}")
    print(f"\nNote: All data is synthetic demo data for hackathon demonstration purposes.")
    
    # Print main demo deal info
    main_deal = next((d for d in demo_data['deals'] if d['current_participants'] == 14), None)
    if main_deal:
        product = demo_data['products'].get(main_deal['product_id'], {})
        print(f"\nMain demo deal:")
        print(f"  - Product: {product.get('name_ru', 'Unknown')}")
        print(f"  - Progress: {main_deal['current_participants']}/{main_deal['target_participants']} participants")
        print(f"  - City: {main_deal['city']}")


if __name__ == "__main__":
    main()
