import pandas as pd

from .synthetic_generator import records
from .validator import validate_record


valid_records = []
invalid_records = []


# Validate every record
for record in records:

    result = validate_record(record)

    if result["is_valid"]:

        valid_records.append(record)

    else:

        invalid_record = record.copy()

        invalid_record["validation_errors"] = ",".join(
            result["errors"]
        )

        invalid_records.append(invalid_record)


# Convert to DataFrames
valid_df = pd.DataFrame(valid_records)
invalid_df = pd.DataFrame(invalid_records)


# Display results
print("\n===== ROADGUARD DATA PIPELINE =====")

print("Total records:", len(records))
print("Valid records:", len(valid_records))
print("Invalid records:", len(invalid_records))


# Save valid data
valid_df.to_csv(
    "data/processed/valid_hazards.csv",
    index=False
)


# Save invalid data
invalid_df.to_csv(
    "data/processed/invalid_hazards.csv",
    index=False
)


print("\nValid data saved to:")
print("data/processed/valid_hazards.csv")

print("\nInvalid data saved to:")
print("data/processed/invalid_hazards.csv")

print("\nPipeline completed successfully!")