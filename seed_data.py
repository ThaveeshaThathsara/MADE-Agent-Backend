from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["bigfive"]
ocean_collection = db["ocean_scores"]

# Sample Data provided by user
sample_data = {
  "report_id": "697db74afc99986c4c78cc96",
  "timestamp": "2026-01-31T08:03:22.735Z",
  "p_factor": 1.3439,
  "priority_mock": 0.32,
  "ocean_scores": {
    "openness": 78,
    "conscientiousness": 75,
    "extraversion": 61,
    "agreeableness": 96,
    "neuroticism": 62
  },
  "ocean_normalized": {
    "openness": 0.65,
    "conscientiousness": 0.625,
    "extraversion": 0.5083333333333333,
    "agreeableness": 0.8,
    "neuroticism": 0.5166666666666667
  },
  "saved_at": datetime.now().isoformat()
}

def seed_database():
    try:
        # Check if report_id exists to avoid duplicates
        existing = ocean_collection.find_one({"report_id": sample_data["report_id"]})
        if existing:
            print(f"⚠️ Report {sample_data['report_id']} already exists. Updating...")
            ocean_collection.update_one(
                {"report_id": sample_data["report_id"]},
                {"$set": sample_data}
            )
        else:
            ocean_collection.insert_one(sample_data)
            print(f"✅ inserted sample data for Report {sample_data['report_id']}")
            
        print("🎉 Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")

if __name__ == "__main__":
    seed_database()
