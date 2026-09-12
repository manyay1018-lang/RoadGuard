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