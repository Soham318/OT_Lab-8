# Dataset Description: Intercity Regional Railway Network

> **Track E**: Main Real-Process Case Study  
> **Course**: Optimization Techniques — Lab Assignment 8  
> **Document Version**: 1.0.0  

---

## 1. Network Overview & Design Rationale

The dataset models a comprehensive 28-station regional passenger railway network. It incorporates four major interconnected corridors that reflect real-world railway operational patterns:

```
                  [STN_10: Alpine Peak Terminal]
                                |
                  [STN_09: Northern Summit]
                                |
                  [STN_08: Northgate City]
                                |
                  [STN_07: Highland Junction] <==== [STN_19: Powergate]
                        /              \                  |
                       /                \          [STN_18: Coalfields City]
                      /                  \                |
          [STN_06: Metro Interchange] === [STN_17: Ironridge]
              /            |             \        |
             /             |              \ [STN_16: Steel Mill Jct]
            /              |                     |
[STN_14: Dune Plains] [STN_05: Midland City] [STN_15: Eastport Terminal]
      |                    |
[STN_13: Oceanview Jct] [STN_04: River Junction] === [STN_23: Orchard Valley]
      |                    |                              |
[STN_12: Seaside Sands] [STN_03: Valley Gate]    [STN_24: Greenfield Jct]
      |                    |                      /       |
[STN_11: Westport Bay]  [STN_02: Grand Harbor]   /  [STN_25: Delta Marsh]
                           |                    /
                  [STN_01: South Central Hub] - [STN_20: Lakeside] - [STN_21: Forest Edge]
```

---

## 2. Quantitative Summary

| Dimension | Metric Count | Description |
| :--- | :--- | :--- |
| **Total Physical Stations** | 28 | Spanning coastal, metropolitan, industrial, and mountainous regions. |
| **Interchange Junctions** | 7 | Stations with multiple connecting lines and dedicated transfer facilities. |
| **Train Routes** | 10 | 2 Express Corridors, 6 Regional Corridors, 2 Cross-Links. |
| **Daily Train Services** | 130 | 65 Up-direction + 65 Down-direction scheduled service runs. |
| **Scheduled Connections** | 551 | Elementary non-stop train legs across the 24-hour timeline. |
| **Time Horizon** | 24 Hours | Minutes from midnight $[0, 1440)$ (00:00 to 24:00). |
| **Average Train Speed** | 45 – 85 km/h | High-speed express (85 km/h) vs. regional local (45-55 km/h). |
| **Station Transfer Buffers**| 10 – 20 min | 20 min at Metro Interchange, 15 min at regional junctions, 10 min standard. |

---

## 3. Data File Schema

### 3.1 `data/railway_stations.csv`
* `station_id` *(string)*: Unique primary key (`STN_01` to `STN_28`).
* `name` *(string)*: Full descriptive station name.
* `code` *(string)*: 3-letter passenger telegraph code (e.g. `SCH`, `MIC`).
* `lat`, `lon` *(float)*: Geographical coordinates.
* `min_transfer_min` *(integer)*: Minimum buffer in minutes for passengers changing trains.
* `is_junction` *(boolean)*: True if station connects more than one distinct line.
* `corridor` *(string)*: Regional subsystem identifier.

### 3.2 `data/train_connections.csv`
* `connection_id` *(string)*: Unique leg identifier (`CONN_0001` to `CONN_0551`).
* `service_id` *(string)*: Scheduled train run identifier.
* `service_name` *(string)*: Human-readable service name.
* `train_type` *(string)*: `Express` or `Regional`.
* `from_station_id`, `to_station_id` *(string)*: Origin and destination station keys.
* `departure_time`, `arrival_time` *(integer)*: Departure/arrival minutes from midnight.
* `departure_hhmm`, `arrival_hhmm` *(string)*: Formatted 24-hour time strings.
* `duration_min` *(integer)*: Travel time in minutes.
* `distance_km` *(float)*: Track length in kilometers.
* `seq_in_service` *(integer)*: Stop sequence number along the train route.

### 3.3 `data/railway_network.json`
Consolidated hierarchical JSON holding full metadata, station objects, route definitions, service manifests, and connection arrays.

