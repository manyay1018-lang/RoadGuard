from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round as spark_round

# Create Spark session
spark = SparkSession.builder \
    .appName("RoadGuard") \
    .master("local[2]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("RoadGuard Spark started successfully!")


# Read valid hazard data
df = spark.read.csv(
    "data/processed/valid_hazards.csv",
    header=True,
    inferSchema=True
)

# Show first 5 records
print("\n===== FIRST 5 RECORDS =====")
df.show(5)

# Show schema
print("\n===== DATA SCHEMA =====")
df.printSchema()

# Show total records
print("\n===== TOTAL RECORDS =====")
print("Total records:", df.count())
# Count hazards by type using Spark
print("\n===== HAZARD COUNT BY TYPE =====")

hazard_counts = df.groupBy("hazard_type").count()

hazard_counts.orderBy("count", ascending=False).show()
print("\n===== AVERAGE SEVERITY BY HAZARD TYPE =====")

severity_by_type = df.groupBy("hazard_type").agg(
    spark_round(avg("severity"), 2).alias("average_severity")
)

severity_by_type.orderBy(
    "average_severity",
    ascending=False
).show()
print("\n===== HIGH-RISK HAZARDS =====")

high_risk_df = df.filter(df["severity"] >= 8)

print("High-risk records:", high_risk_df.count())

high_risk_percentage = (
    high_risk_df.count() / df.count()
) * 100

print("High-risk percentage:", round(high_risk_percentage, 2), "%")


print("\n===== HIGH-RISK BY HAZARD TYPE =====")

high_risk_by_type = high_risk_df.groupBy("hazard_type").count()

high_risk_by_type.orderBy(
    "count",
    ascending=False
).show(truncate=False)
# Stop Spark
spark.stop()