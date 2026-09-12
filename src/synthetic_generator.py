import random
from datetime import datetime, timedelta


HAZARD_TYPES = [
    "pothole",
    "accident",
    "flooding",
    "damaged_road",
    "broken_streetlight",
    "missing_sign"
]

STATUSES = [
    "reported",
    "verified",
    "in_progress",
    "resolved"
]


DESCRIPTIONS = {
    "pothole": "Large pothole reported on the road",
    "accident": "Road accident reported",
    "flooding": "Water accumulation reported on road",
    "damaged_road": "Road surface is damaged",
    "broken_streetlight": "Streetlight is not functioning",
    "missing_sign": "Important road sign is missing"
}


def generate_hazard_id(number):
    return f"RG-{number:06d}"


def generate_timestamp():
    start_date = datetime(2026, 1, 1)
    random_days = random.randint(0, 250)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)

    return (
        start_date
        + timedelta(
            days=random_days,
            hours=random_hours,
            minutes=random_minutes
        )
    ).isoformat()


def generate_record(number):
    hazard_type = random.choice(HAZARD_TYPES)

    latitude = round(random.uniform(12.85, 13.10), 6)
    longitude = round(random.uniform(77.45, 77.75), 6)

    return {
        "hazard_id": generate_hazard_id(number),
        "hazard_type": hazard_type,
        "severity": random.randint(1, 10),
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": generate_timestamp(),
        "status": random.choice(STATUSES),
        "description": DESCRIPTIONS[hazard_type],
        "data_source": "synthetic"
    }


records = []

for number in range(1, 1001):
    records.append(generate_record(number))


print("Total records:", len(records))
print("\nFirst 5 records:")

for record in records[:5]:
    print(record)