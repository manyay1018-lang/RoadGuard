import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from validator import (
    validate_hazard_type,
    validate_severity,
    validate_location,
    validate_status,
    validate_timestamp,
    validate_record
)

print("===== ROADGUARD VALIDATOR TESTS =====")


# Test 1: Valid hazard type
print("\n1. Hazard type:")
print(validate_hazard_type("pothole"))


# Test 2: Invalid hazard type
print("\n2. Invalid hazard type:")
print(validate_hazard_type("unknown_problem"))


# Test 3: Valid severity
print("\n3. Valid severity:")
print(validate_severity(7))


# Test 4: Invalid severity
print("\n4. Invalid severity:")
print(validate_severity(15))


# Test 5: Valid location
print("\n5. Valid location:")
print(validate_location(12.95, 77.60))


# Test 6: Invalid location
print("\n6. Invalid location:")
print(validate_location(50, 200))


# Test 7: Valid status
print("\n7. Valid status:")
print(validate_status("reported"))


# Test 8: Invalid status
print("\n8. Invalid status:")
print(validate_status("wrong_status"))


# Test 9: Valid timestamp
print("\n9. Valid timestamp:")
print(validate_timestamp("2026-07-28T09:33:00"))


# Test 10: Invalid timestamp
print("\n10. Invalid timestamp:")
print(validate_timestamp("not-a-date"))


# Complete valid record
valid_record = {
    "hazard_id": "RG-000001",
    "hazard_type": "pothole",
    "severity": 7,
    "latitude": 12.95,
    "longitude": 77.60,
    "timestamp": "2026-07-28T09:33:00",
    "status": "reported",
    "description": "Large pothole on road",
    "data_source": "synthetic"
}


# Complete invalid record
bad_record = {
    "hazard_id": "RG-BAD-001",
    "hazard_type": "unknown_problem",
    "severity": 15,
    "latitude": 50,
    "longitude": 200,
    "timestamp": "not-a-date",
    "status": "wrong_status",
    "description": "",
    "data_source": ""
}


# Test 11: Valid record
print("\n11. Complete valid record:")
print(validate_record(valid_record))


# Test 12: Invalid record
print("\n12. Complete invalid record:")
print(validate_record(bad_record))


print("\n===== TESTS COMPLETED =====")