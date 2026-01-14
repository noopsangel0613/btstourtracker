#!/usr/bin/env python3
"""
Monitor BTS tour schedule JSON file and save snapshots when data changes.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


def download_json(url: str) -> dict:
    """Download JSON data from URL."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def calculate_hash(data: dict) -> str:
    """Calculate SHA256 hash of JSON data with stable serialization."""
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


def read_last_hash(file_path: Path) -> str:
    """Read the last saved hash from file."""
    if file_path.exists():
        return file_path.read_text(encoding='utf-8').strip()
    return ""


def save_hash(file_path: Path, hash_value: str):
    """Save hash to file with UTF-8 encoding and trailing newline."""
    file_path.write_text(hash_value + '\n', encoding='utf-8')


def save_snapshot(data: dict, snapshots_dir: Path):
    """Save timestamped snapshot of data."""
    snapshots_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_file = snapshots_dir / f"tour_{timestamp}.json"
    
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write('\n')
    
    print(f"Snapshot saved: {snapshot_file}")


def main():
    """Main monitoring function."""
    url = "https://ibighit.com/data/tour_ticket/tour_schedule_list.json"
    repo_root = Path(__file__).parent
    last_hash_file = repo_root / "last_hash.txt"
    snapshots_dir = repo_root / "snapshots"
    
    print(f"Downloading data from {url}")
    try:
        data = download_json(url)
    except requests.RequestException as e:
        print(f"Error downloading data: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return
    
    current_hash = calculate_hash(data)
    last_hash = read_last_hash(last_hash_file)
    
    print(f"Current hash: {current_hash}")
    print(f"Last hash: {last_hash}")
    
    if current_hash != last_hash:
        print("Data has changed!")
        save_snapshot(data, snapshots_dir)
        save_hash(last_hash_file, current_hash)
        print("Hash updated successfully")
    else:
        print("No changes detected")


if __name__ == "__main__":
    main()
