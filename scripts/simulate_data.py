"""
Synthetic Data Generator for Silent Epidemic Detector

Generates realistic hospital events, social media posts, and environmental data
with optional outbreak simulation.

Usage:
    python simulate_data.py --days 120 --outbreak 1 --export ../data/
"""

import argparse
import random
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np


# Mumbai ward names
MUMBAI_WARDS = [
    {"ward": "Colaba", "lat": 18.9067, "lon": 72.8147},
    {"ward": "Marine Lines", "lat": 18.9432, "lon": 72.8236},
    {"ward": "Dadar", "lat": 19.0176, "lon": 72.8481},
    {"ward": "Bandra", "lat": 19.0596, "lon": 72.8295},
    {"ward": "Andheri", "lat": 19.1136, "lon": 72.8697},
    {"ward": "Borivali", "lat": 19.2307, "lon": 72.8567},
    {"ward": "Kurla", "lat": 19.0728, "lon": 72.8826},
    {"ward": "Mulund", "lat": 19.1722, "lon": 72.9565},
    {"ward": "Vikhroli", "lat": 19.1076, "lon": 72.9250},
    {"ward": "Powai", "lat": 19.1168, "lon": 72.9050},
    {"ward": "Worli", "lat": 18.9972, "lon": 72.8174},
    {"ward": "Malad", "lat": 19.1864, "lon": 72.8493},
]

# Symptoms and diseases
SYMPTOMS = [
    "fever", "cough", "headache", "body_ache", "fatigue", "chills",
    "nausea", "vomiting", "diarrhea", "rash", "joint_pain", "weakness",
    "sore_throat", "runny_nose", "difficulty_breathing", "chest_pain"
]

DISEASES = {
    "dengue": ["fever", "headache", "rash", "joint_pain", "body_ache"],
    "malaria": ["fever", "chills", "headache", "nausea", "vomiting"],
    "flu": ["fever", "cough", "sore_throat", "body_ache", "fatigue"],
    "viral_fever": ["fever", "headache", "body_ache", "weakness"],
    "gastroenteritis": ["nausea", "vomiting", "diarrhea", "fever"],
}

# Social media keywords
SOCIAL_KEYWORDS = [
    "fever", "sick", "ill", "dengue", "malaria", "hospital", "doctor",
    "medicine", "outbreak", "disease", "epidemic", "flu", "cold",
    "headache", "weak", "unwell", "clinic", "emergency"
]

# Hospital names
HOSPITALS = [
    "City General Hospital", "Community Health Center", "District Medical Center",
    "Primary Health Clinic", "Municipal Hospital", "Metro Healthcare",
    "Central Medical Institute", "Public Health Center"
]

# Social media platforms
PLATFORMS = ["twitter", "facebook", "reddit", "instagram", "whatsapp"]


class SyntheticDataGenerator:
    """Generate synthetic disease outbreak data"""
    
    def __init__(self, days: int, outbreak_config: dict = None):
        self.days = days
        self.start_date = datetime.now() - timedelta(days=days)
        self.outbreak_config = outbreak_config or {}
        
        self.hospital_events = []
        self.social_posts = []
        self.environment_data = []
    
    def generate_all(self):
        """Generate all data types"""
        print(f"Generating {self.days} days of synthetic data...")
        
        for day in range(self.days):
            current_date = self.start_date + timedelta(days=day)
            
            # Check if this is an outbreak day
            is_outbreak = self._is_outbreak_day(day)
            multiplier = 5.0 if is_outbreak else 1.0
            
            print(f"Day {day+1}/{self.days}: {current_date.strftime('%Y-%m-%d')} {'[OUTBREAK]' if is_outbreak else ''}")
            
            # Generate data for each ward
            for ward_info in MUMBAI_WARDS:
                # Hospital events
                num_events = int(random.randint(5, 15) * multiplier)
                for _ in range(num_events):
                    self.hospital_events.append(
                        self._generate_hospital_event(current_date, ward_info, is_outbreak)
                    )
                
                # Social media posts
                num_posts = int(random.randint(10, 30) * multiplier)
                for _ in range(num_posts):
                    self.social_posts.append(
                        self._generate_social_post(current_date, ward_info, is_outbreak)
                    )
                
                # Environmental data (multiple readings per day)
                for hour in [0, 6, 12, 18]:
                    self.environment_data.append(
                        self._generate_environment_data(current_date, ward_info, hour, is_outbreak)
                    )
        
        print(f"\nGeneration complete!")
        print(f"  Hospital events: {len(self.hospital_events)}")
        print(f"  Social posts: {len(self.social_posts)}")
        print(f"  Environment readings: {len(self.environment_data)}")
    
    def _is_outbreak_day(self, day: int) -> bool:
        """Check if this day is part of an outbreak"""
        if not self.outbreak_config:
            return False
        
        outbreak_start = self.outbreak_config.get("start_day", 60)
        outbreak_duration = self.outbreak_config.get("duration", 14)
        
        return outbreak_start <= day < (outbreak_start + outbreak_duration)
    
    def _generate_hospital_event(self, date: datetime, ward_info: dict, is_outbreak: bool) -> dict:
        """Generate a hospital event"""
        # Choose disease (more dengue/malaria during outbreak)
        if is_outbreak:
            disease = random.choice(["dengue", "malaria", "dengue", "malaria", "flu"])
        else:
            disease = random.choice(list(DISEASES.keys()))
        
        symptoms = DISEASES[disease].copy()
        
        # Add some random symptoms
        if random.random() > 0.7:
            symptoms.append(random.choice(SYMPTOMS))
        
        # Random timestamp during the day
        timestamp = date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        event = {
            "timestamp": timestamp.isoformat(),
            "location": {
                "lat": ward_info["lat"] + random.uniform(-0.01, 0.01),
                "lon": ward_info["lon"] + random.uniform(-0.01, 0.01),
                "ward": ward_info["ward"]
            },
            "hospital_id": f"H{random.randint(1, 8):03d}",
            "hospital_name": random.choice(HOSPITALS),
            "symptoms": symptoms,
            "diagnosis": disease if random.random() > 0.3 else None,
            "patient_count": random.randint(1, 3) if is_outbreak else 1,
            "severity": random.choice(["mild", "moderate", "severe"]) if is_outbreak else random.choice(["mild", "mild", "moderate"]),
            "age_group": random.choice(["0-10", "11-20", "21-40", "41-60", "60+"]),
            "metadata": {}
        }
        
        return event
    
    def _generate_social_post(self, date: datetime, ward_info: dict, is_outbreak: bool) -> dict:
        """Generate a social media post"""
        # More disease-related keywords during outbreak
        if is_outbreak:
            keywords = random.sample(
                ["fever", "sick", "dengue", "malaria", "hospital", "outbreak", "ill"],
                k=random.randint(2, 4)
            )
        else:
            keywords = random.sample(SOCIAL_KEYWORDS, k=random.randint(1, 3))
        
        # Generate text with keywords
        templates = [
            f"Feeling {keywords[0]} today 😷",
            f"So many people with {keywords[0]} in my area",
            f"Another case of {keywords[0]} reported nearby",
            f"Is there a {keywords[0]} going around?",
            f"Lots of {keywords[0]} cases lately",
            f"My neighbor has {keywords[0]}, worried about spread",
        ]
        
        timestamp = date + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        post = {
            "timestamp": timestamp.isoformat(),
            "location": {
                "lat": ward_info["lat"] + random.uniform(-0.01, 0.01),
                "lon": ward_info["lon"] + random.uniform(-0.01, 0.01),
                "ward": ward_info["ward"]
            },
            "platform": random.choice(PLATFORMS),
            "post_id": f"POST{random.randint(100000, 999999)}",
            "text": random.choice(templates),
            "keywords": keywords,
            "sentiment": random.uniform(-0.8, -0.2) if is_outbreak else random.uniform(-0.5, 0.5),
            "engagement": random.randint(5, 100) if is_outbreak else random.randint(1, 20),
            "metadata": {}
        }
        
        return post
    
    def _generate_environment_data(self, date: datetime, ward_info: dict, hour: int, is_outbreak: bool) -> dict:
        """Generate environmental data"""
        timestamp = date + timedelta(hours=hour)
        
        # Simulate seasonal patterns
        day_of_year = date.timetuple().tm_yday
        
        # Temperature (Mumbai: 25-35°C, higher in summer)
        base_temp = 28 + 5 * np.sin(2 * np.pi * day_of_year / 365)
        temperature = base_temp + random.uniform(-2, 2)
        
        # Humidity (60-90% in monsoon season)
        monsoon_factor = 1.0 if 150 < day_of_year < 270 else 0.5
        humidity = 50 + 30 * monsoon_factor + random.uniform(-10, 10)
        
        # Rainfall (higher in monsoon)
        if 150 < day_of_year < 270:
            rainfall = random.uniform(0, 50) if random.random() > 0.3 else 0
        else:
            rainfall = random.uniform(0, 5) if random.random() > 0.8 else 0
        
        # Mosquito index (higher during outbreak and monsoon)
        base_mosquito = 3.0
        if is_outbreak:
            base_mosquito = 7.0
        elif 150 < day_of_year < 270:
            base_mosquito = 5.0
        
        mosquito_index = base_mosquito + random.uniform(-1, 2)
        mosquito_index = max(0, min(10, mosquito_index))
        
        # Air quality
        air_quality_index = random.uniform(50, 150)
        
        env_data = {
            "timestamp": timestamp.isoformat(),
            "location": {
                "lat": ward_info["lat"] + random.uniform(-0.005, 0.005),
                "lon": ward_info["lon"] + random.uniform(-0.005, 0.005),
                "ward": ward_info["ward"]
            },
            "temperature": round(temperature, 1),
            "humidity": round(max(0, min(100, humidity)), 1),
            "rainfall": round(rainfall, 1),
            "mosquito_index": round(mosquito_index, 1),
            "air_quality_index": round(air_quality_index, 1),
            "water_quality": random.choice(["good", "moderate", "poor"]),
            "metadata": {}
        }
        
        return env_data
    
    def export_json(self, output_dir: Path):
        """Export data as JSON files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export hospital events
        with open(output_dir / "hospital_events.json", "w") as f:
            json.dump(self.hospital_events, f, indent=2)
        
        # Export social posts
        with open(output_dir / "social_posts.json", "w") as f:
            json.dump(self.social_posts, f, indent=2)
        
        # Export environment data
        with open(output_dir / "environment_data.json", "w") as f:
            json.dump(self.environment_data, f, indent=2)
        
        print(f"\nJSON files exported to: {output_dir}")
    
    def export_csv(self, output_dir: Path):
        """Export data as CSV files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export hospital events
        with open(output_dir / "hospital_events.csv", "w", newline="", encoding="utf-8") as f:
            if self.hospital_events:
                # Flatten nested structure
                flattened = []
                for event in self.hospital_events:
                    flat = {
                        "timestamp": event["timestamp"],
                        "ward": event["location"]["ward"],
                        "lat": event["location"]["lat"],
                        "lon": event["location"]["lon"],
                        "hospital_id": event["hospital_id"],
                        "hospital_name": event["hospital_name"],
                        "symptoms": "|".join(event["symptoms"]),
                        "diagnosis": event.get("diagnosis", ""),
                        "patient_count": event["patient_count"],
                        "severity": event["severity"],
                        "age_group": event["age_group"]
                    }
                    flattened.append(flat)
                
                writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                writer.writeheader()
                writer.writerows(flattened)
        
        # Export social posts
        with open(output_dir / "social_posts.csv", "w", newline="", encoding="utf-8") as f:
            if self.social_posts:
                flattened = []
                for post in self.social_posts:
                    flat = {
                        "timestamp": post["timestamp"],
                        "ward": post["location"]["ward"],
                        "lat": post["location"]["lat"],
                        "lon": post["location"]["lon"],
                        "platform": post["platform"],
                        "post_id": post["post_id"],
                        "text": post["text"],
                        "keywords": "|".join(post["keywords"]),
                        "sentiment": post["sentiment"],
                        "engagement": post["engagement"]
                    }
                    flattened.append(flat)
                
                writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                writer.writeheader()
                writer.writerows(flattened)
        
        # Export environment data
        with open(output_dir / "environment_data.csv", "w", newline="", encoding="utf-8") as f:
            if self.environment_data:
                flattened = []
                for env in self.environment_data:
                    flat = {
                        "timestamp": env["timestamp"],
                        "ward": env["location"]["ward"],
                        "lat": env["location"]["lat"],
                        "lon": env["location"]["lon"],
                        "temperature": env["temperature"],
                        "humidity": env["humidity"],
                        "rainfall": env["rainfall"],
                        "mosquito_index": env["mosquito_index"],
                        "air_quality_index": env["air_quality_index"],
                        "water_quality": env["water_quality"]
                    }
                    flattened.append(flat)
                
                writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                writer.writeheader()
                writer.writerows(flattened)
        
        print(f"CSV files exported to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic disease outbreak data for Silent Epidemic Detector"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=120,
        help="Number of days to simulate (default: 120)"
    )
    
    parser.add_argument(
        "--outbreak",
        type=int,
        default=1,
        help="Number of outbreak periods to simulate (default: 1)"
    )
    
    parser.add_argument(
        "--outbreak-start",
        type=int,
        default=60,
        help="Day to start outbreak (default: 60)"
    )
    
    parser.add_argument(
        "--outbreak-duration",
        type=int,
        default=14,
        help="Duration of outbreak in days (default: 14)"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        default="./data",
        help="Export directory path (default: ./data)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "both"],
        default="both",
        help="Export format (default: both)"
    )
    
    args = parser.parse_args()
    
    # Configure outbreak
    outbreak_config = {
        "start_day": args.outbreak_start,
        "duration": args.outbreak_duration
    }
    
    # Generate data
    generator = SyntheticDataGenerator(args.days, outbreak_config)
    generator.generate_all()
    
    # Export data
    output_dir = Path(args.export)
    
    if args.format in ["json", "both"]:
        generator.export_json(output_dir)
    
    if args.format in ["csv", "both"]:
        generator.export_csv(output_dir)
    
    print("\n✅ Data generation complete!")
    print(f"\nTo import this data into the system, use:")
    print(f"  python scripts/import_data.py --dir {output_dir}")


if __name__ == "__main__":
    main()
