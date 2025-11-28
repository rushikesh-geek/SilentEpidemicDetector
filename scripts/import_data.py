"""
Import synthetic data into MongoDB

Usage:
    python import_data.py --dir ../data/
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from core.database import db
from core.logging_config import logger


def import_json_data(data_dir: Path):
    """Import JSON data files into MongoDB"""
    
    print("Connecting to MongoDB...")
    db.connect()
    
    # Import hospital events
    hospital_file = data_dir / "hospital_events.json"
    if hospital_file.exists():
        print(f"\nImporting hospital events from {hospital_file}...")
        with open(hospital_file, "r") as f:
            events = json.load(f)
        
        # Convert timestamp strings to datetime
        for event in events:
            event["timestamp"] = datetime.fromisoformat(event["timestamp"])
        
        if events:
            result = db.get_collection("hospital_events").insert_many(events)
            print(f"  ✅ Imported {len(result.inserted_ids)} hospital events")
    
    # Import social posts
    social_file = data_dir / "social_posts.json"
    if social_file.exists():
        print(f"\nImporting social posts from {social_file}...")
        with open(social_file, "r") as f:
            posts = json.load(f)
        
        for post in posts:
            post["timestamp"] = datetime.fromisoformat(post["timestamp"])
        
        if posts:
            result = db.get_collection("social_posts").insert_many(posts)
            print(f"  ✅ Imported {len(result.inserted_ids)} social posts")
    
    # Import environment data
    env_file = data_dir / "environment_data.json"
    if env_file.exists():
        print(f"\nImporting environment data from {env_file}...")
        with open(env_file, "r") as f:
            env_data = json.load(f)
        
        for env in env_data:
            env["timestamp"] = datetime.fromisoformat(env["timestamp"])
        
        if env_data:
            result = db.get_collection("environment_data").insert_many(env_data)
            print(f"  ✅ Imported {len(result.inserted_ids)} environment readings")
    
    print("\n✅ Data import complete!")
    
    db.close()


def main():
    parser = argparse.ArgumentParser(description="Import synthetic data into MongoDB")
    
    parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="Directory containing JSON data files"
    )
    
    args = parser.parse_args()
    
    data_dir = Path(args.dir)
    
    if not data_dir.exists():
        print(f"❌ Error: Directory {data_dir} does not exist")
        sys.exit(1)
    
    import_json_data(data_dir)


if __name__ == "__main__":
    main()
