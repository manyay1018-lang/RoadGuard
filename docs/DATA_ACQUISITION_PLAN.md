# RoadGuard Data Acquisition Plan

## 1. Purpose

This document defines the data required for the RoadGuard
road safety and infrastructure intelligence platform.

## 2. Geographic Scope

### Initial Pilot
Bengaluru, Karnataka, India

### Long-Term
India-wide deployment

## 3. Required Data Categories

### 3.1 Accident Data

Potential fields:

- accident_id
- date
- time
- latitude
- longitude
- location
- vehicles_involved
- injuries
- fatalities
- weather
- road_condition

### 3.2 Road Network Data

Potential fields:

- road_id
- road_name
- road_type
- latitude
- longitude
- speed_limit
- surface_type

### 3.3 Road Hazard Data

Potential fields:

- hazard_id
- hazard_type
- description
- latitude
- longitude
- severity
- reported_at
- status

### 3.4 Weather Data

Potential fields:

- timestamp
- latitude
- longitude
- rainfall
- temperature
- visibility
- weather_condition

### 3.5 Traffic Data

Potential fields:

- timestamp
- road_id
- traffic_volume
- average_speed
- congestion_level

## 4. Data Sources

We will prioritize:

1. Government/open-data sources
2. Public geospatial datasets
3. Public research datasets
4. Legitimate APIs
5. RoadGuard-generated data
6. Clearly labelled synthetic data for scalability testing

## 5. Data Quality Requirements

Every dataset should be evaluated for:

- Missing values
- Duplicate records
- Invalid coordinates
- Invalid timestamps
- Outliers
- Inconsistent categories
- Schema consistency
- Data provenance
- Licensing/usage restrictions

## 6. Data Pipeline

Raw data must remain unchanged.

Pipeline:

Raw
→ Validation
→ Cleaning
→ Transformation
→ Feature Engineering
→ Processed Data

## 7. Data Provenance

For every external dataset we will record:

- Source
- URL
- Download date
- Publisher
- License
- Original filename
- Description
- Transformation performed

## 8. Synthetic Data

Synthetic data may be generated for:

- Large-scale testing
- Kafka streaming demonstrations
- Spark processing demonstrations
- Load testing

Synthetic data must never be presented as real accident statistics.

## 9. Initial Goal

Build a reproducible data-wrangling pipeline using
a real public dataset before introducing distributed
processing with Spark.