# RoadGuard Data Model

## Purpose

This document defines the initial data entities and fields
used by the RoadGuard platform.

## 1. Road Hazard

| Field | Type | Description |
|---|---|---|
| hazard_id | String | Unique hazard identifier |
| hazard_type | Category | Type of road hazard |
| description | Text | Citizen description |
| latitude | Float | Geographic latitude |
| longitude | Float | Geographic longitude |
| city | String | City |
| district | String | District |
| ward | String | Ward |
| severity | Integer | Severity score |
| reported_at | Timestamp | Time of report |
| status | Category | Current status |

## 2. Accident

| Field | Type | Description |
|---|---|---|
| accident_id | String | Unique accident identifier |
| date | Date | Accident date |
| time | Time | Accident time |
| latitude | Float | Geographic latitude |
| longitude | Float | Geographic longitude |
| city | String | City |
| vehicles_involved | Integer | Number of vehicles |
| injuries | Integer | Number of injuries |
| fatalities | Integer | Number of fatalities |
| weather | Category | Weather condition |
| road_condition | Category | Road condition |

## 3. Road Segment

| Field | Type | Description |
|---|---|---|
| road_id | String | Unique road identifier |
| road_name | String | Road name |
| road_type | Category | Type of road |
| city | String | City |
| latitude | Float | Geographic latitude |
| longitude | Float | Geographic longitude |
| speed_limit | Integer | Speed limit |

## 4. Future Data Sources

Potential sources include:

- Citizen reports
- Historical accident records
- Road network data
- Weather data
- Traffic data
- Government/open datasets
- Geospatial data
- Synthetic data for scalability testing

## Geographic Scope

Initial implementation:

Bengaluru, Karnataka, India

Long-term:

India-wide deployment
---

## RoadGuard Data Model v0.2

The initial RoadGuard implementation uses a practical schema designed
for Bengaluru while remaining scalable to India-wide deployment.

### Core Fields

- hazard_id
- hazard_type
- hazard_category
- description
- latitude
- longitude
- coordinate_accuracy_m
- geometry_type
- road_name
- road_segment_id
- country_code
- state_code
- district_code
- city_code
- ward_code
- severity
- status
- status_reason
- reported_at
- created_at
- updated_at
- ingestion_time
- source_type
- source_id
- detection_method
- source_confidence
- model_confidence
- schema_version
- is_synthetic

### Design Principles

1. Synthetic records must be explicitly marked.
2. Raw data must remain separate from processed data.
3. Administrative codes are preferred over names as join keys.
4. Timestamps must have consistent semantics.
5. Geographic coordinates must be validated.
6. Hazard, severity, and status values should use controlled vocabularies.
7. AI confidence must remain separate from source confidence.
8. The schema must support future Kafka and Spark processing.
9. The schema must support expansion from Bengaluru to India.
10. Personal information must not be stored in the core hazard dataset.