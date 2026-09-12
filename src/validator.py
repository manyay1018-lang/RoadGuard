from datetime import datetime


# Allowed hazard types
HAZARD_TYPES = [
    "pothole",
    "accident",
    "flooding",
    "damaged_road",
    "broken_streetlight",
    "missing_sign"
]


# Allowed statuses
STATUSES = [
    "reported",
    "verified",
    "in_progress",
    "resolved"
]


# Check hazard type
def validate_hazard_type(value):
    if value not in HAZARD_TYPES:
        return "INVALID_VALUE"

    return None


# Check severity
def validate_severity(value):
    if not isinstance(value, int) or isinstance(value, bool):
        return "INVALID_TYPE"

    if value < 1 or value > 10:
        return "OUT_OF_RANGE"

    return None


# Check latitude and longitude
def validate_location(latitude, longitude):
    errors = []

    # Latitude check
    if not isinstance(latitude, (int, float)):
        errors.append("INVALID_LATITUDE")
    elif latitude < 12.85 or latitude > 13.10:
        errors.append("LATITUDE_OUT_OF_RANGE")

    # Longitude check
    if not isinstance(longitude, (int, float)):
        errors.append("INVALID_LONGITUDE")
    elif longitude < 77.45 or longitude > 77.75:
        errors.append("LONGITUDE_OUT_OF_RANGE")

    return errors


# Check status
def validate_status(value):
    if value not in STATUSES:
        return "INVALID_STATUS"

    return None


# Check timestamp
def validate_timestamp(value):
    try:
        datetime.fromisoformat(value)
        return None
    except (ValueError, TypeError):
        return "INVALID_TIMESTAMP"


# Check complete hazard record
def validate_record(record):

    errors = []

    # 1. Check hazard ID
    if "hazard_id" not in record or not record["hazard_id"]:
        errors.append("MISSING_HAZARD_ID")

    # 2. Check hazard type
    hazard_type_error = validate_hazard_type(
        record.get("hazard_type")
    )

    if hazard_type_error:
        errors.append(hazard_type_error)

    # 3. Check severity
    severity_error = validate_severity(
        record.get("severity")
    )

    if severity_error:
        errors.append(severity_error)

    # 4. Check location
    location_errors = validate_location(
        record.get("latitude"),
        record.get("longitude")
    )

    errors.extend(location_errors)

    # 5. Check status
    status_error = validate_status(
        record.get("status")
    )

    if status_error:
        errors.append(status_error)

    # 6. Check timestamp
    timestamp_error = validate_timestamp(
        record.get("timestamp")
    )

    if timestamp_error:
        errors.append(timestamp_error)

    # 7. Check description
    if not record.get("description"):
        errors.append("MISSING_DESCRIPTION")

    # 8. Check data source
    if not record.get("data_source"):
        errors.append("MISSING_DATA_SOURCE")

    # Final result
    if len(errors) == 0:

        return {
            "is_valid": True,
            "status": "VALID",
            "errors": []
        }

    return {
        "is_valid": False,
        "status": "INVALID",
        "errors": errors
    }


# --------------------------------------------------
# TESTING
# --------------------------------------------------

valid_record = {
    "hazard_id": "RG-000001",
    "hazard_type": "pothole",
    "severity": 7,
    "latitude": 12.95,
    "longitude": 77.60,
    "timestamp": "2026-07-28T09:33:00",
    "status": "reported",
    "description": "Large pothole reported on the road",
    "data_source": "synthetic"
}


bad_record = {
    "hazard_id": "RG-BAD-001",
    "hazard_type": "unknown_problem",
    "severity": 15,
    "latitude": 50,
    "longitude": 200,
    "timestamp": "not-a-date",
    "status": "something_wrong",
    "description": "",
    "data_source": ""
}


print("\nValid record:")
print(validate_record(valid_record))


print("\nBad record:")
print(validate_record(bad_record))