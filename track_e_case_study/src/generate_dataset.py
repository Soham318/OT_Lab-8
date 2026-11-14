"""
Railway Network Synthetic Dataset Generator
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Generates a realistic, reproducible 28-station railway network with multiple corridors,
express and regional services, scheduled arrival/departure times, and designated
transfer junctions.

Outputs:
    - data/railway_stations.csv
    - data/train_connections.csv
    - data/railway_network.json
"""

import csv
import json
import math
import os
from typing import Dict, List, Tuple

# Deterministic seed and constants
RANDOM_SEED = 42
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")


def format_hhmm(minutes: int) -> str:
    """Convert minutes from midnight to HH:MM format."""
    hrs = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hrs:02d}:{mins:02d}"


def get_station_definitions() -> List[Dict]:
    """Define 28 realistic stations across 4 interconnected corridors."""
    stations = [
        # Main Trunk Line (South to North)
        {"station_id": "STN_01", "name": "South Central Hub", "code": "SCH", "lat": 18.930, "lon": 72.830, "min_transfer_min": 15, "is_junction": True, "corridor": "Main Trunk"},
        {"station_id": "STN_02", "name": "Grand Harbor", "code": "GHB", "lat": 19.050, "lon": 72.880, "min_transfer_min": 10, "is_junction": False, "corridor": "Main Trunk"},
        {"station_id": "STN_03", "name": "Valley Gate", "code": "VGT", "lat": 19.220, "lon": 73.010, "min_transfer_min": 10, "is_junction": False, "corridor": "Main Trunk"},
        {"station_id": "STN_04", "name": "River Junction", "code": "RJC", "lat": 19.450, "lon": 73.180, "min_transfer_min": 15, "is_junction": True, "corridor": "Main Trunk"},
        {"station_id": "STN_05", "name": "Midland City", "code": "MLC", "lat": 19.780, "lon": 73.450, "min_transfer_min": 10, "is_junction": False, "corridor": "Main Trunk"},
        {"station_id": "STN_06", "name": "Metro Interchange", "code": "MIC", "lat": 20.000, "lon": 73.780, "min_transfer_min": 20, "is_junction": True, "corridor": "Main Trunk"},
        {"station_id": "STN_07", "name": "Highland Junction", "code": "HJC", "lat": 20.350, "lon": 74.120, "min_transfer_min": 15, "is_junction": True, "corridor": "Main Trunk"},
        {"station_id": "STN_08", "name": "Northgate City", "code": "NGC", "lat": 20.720, "lon": 74.450, "min_transfer_min": 12, "is_junction": False, "corridor": "Main Trunk"},
        {"station_id": "STN_09", "name": "Northern Summit", "code": "NSM", "lat": 21.100, "lon": 74.780, "min_transfer_min": 12, "is_junction": True, "corridor": "Main Trunk"},
        {"station_id": "STN_10", "name": "Alpine Peak Terminal", "code": "APT", "lat": 21.500, "lon": 75.100, "min_transfer_min": 10, "is_junction": False, "corridor": "Main Trunk"},

        # Western Coastal Corridor
        {"station_id": "STN_11", "name": "Westport Bay", "code": "WPB", "lat": 19.100, "lon": 72.550, "min_transfer_min": 10, "is_junction": False, "corridor": "Western Coast"},
        {"station_id": "STN_12", "name": "Seaside Sands", "code": "SSS", "lat": 19.350, "lon": 72.650, "min_transfer_min": 10, "is_junction": False, "corridor": "Western Coast"},
        {"station_id": "STN_13", "name": "Oceanview Junction", "code": "OVJ", "lat": 19.650, "lon": 72.780, "min_transfer_min": 15, "is_junction": True, "corridor": "Western Coast"},
        {"station_id": "STN_14", "name": "Dune Plains", "code": "DPL", "lat": 19.850, "lon": 73.050, "min_transfer_min": 10, "is_junction": False, "corridor": "Western Coast"},

        # Eastern Industrial Corridor
        {"station_id": "STN_15", "name": "Eastport Terminal", "code": "EPT", "lat": 19.900, "lon": 74.800, "min_transfer_min": 10, "is_junction": False, "corridor": "Eastern Industrial"},
        {"station_id": "STN_16", "name": "Steel Mill Junction", "code": "SMJ", "lat": 20.050, "lon": 74.500, "min_transfer_min": 15, "is_junction": True, "corridor": "Eastern Industrial"},
        {"station_id": "STN_17", "name": "Ironridge", "code": "IRG", "lat": 20.150, "lon": 74.200, "min_transfer_min": 10, "is_junction": False, "corridor": "Eastern Industrial"},
        {"station_id": "STN_18", "name": "Coalfields City", "code": "CFC", "lat": 20.300, "lon": 74.650, "min_transfer_min": 10, "is_junction": False, "corridor": "Eastern Industrial"},
        {"station_id": "STN_19", "name": "Powergate", "code": "PWG", "lat": 20.550, "lon": 74.850, "min_transfer_min": 12, "is_junction": False, "corridor": "Eastern Industrial"},

        # Southern Ring & Cross Country
        {"station_id": "STN_20", "name": "Lakeside", "code": "LKS", "lat": 18.800, "lon": 73.200, "min_transfer_min": 10, "is_junction": False, "corridor": "Southern Ring"},
        {"station_id": "STN_21", "name": "Forest Edge Junction", "code": "FEJ", "lat": 18.950, "lon": 73.500, "min_transfer_min": 15, "is_junction": True, "corridor": "Southern Ring"},
        {"station_id": "STN_22", "name": "Silver Creek", "code": "SVC", "lat": 19.150, "lon": 73.650, "min_transfer_min": 10, "is_junction": False, "corridor": "Southern Ring"},
        {"station_id": "STN_23", "name": "Orchard Valley", "code": "ORV", "lat": 19.400, "lon": 73.800, "min_transfer_min": 10, "is_junction": False, "corridor": "Southern Ring"},
        {"station_id": "STN_24", "name": "Greenfield Junction", "code": "GFJ", "lat": 19.700, "lon": 73.950, "min_transfer_min": 15, "is_junction": True, "corridor": "Southern Ring"},
        {"station_id": "STN_25", "name": "Delta Marsh", "code": "DTM", "lat": 19.900, "lon": 74.150, "min_transfer_min": 10, "is_junction": False, "corridor": "Southern Ring"},
        {"station_id": "STN_26", "name": "Sunburst", "code": "SBR", "lat": 20.800, "lon": 75.100, "min_transfer_min": 10, "is_junction": False, "corridor": "Northern Spur"},
        {"station_id": "STN_27", "name": "Golden Ridge", "code": "GDR", "lat": 20.950, "lon": 75.350, "min_transfer_min": 10, "is_junction": False, "corridor": "Northern Spur"},
        {"station_id": "STN_28", "name": "Canyon Pass", "code": "CNP", "lat": 21.200, "lon": 75.500, "min_transfer_min": 12, "is_junction": False, "corridor": "Northern Spur"},
    ]
    return stations


def haversine_dist(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def define_train_routes() -> List[Dict]:
    """
    Define 10 distinct train service routes with varying stops, speeds, and frequencies.
    """
    routes = [
        # Route 1: Mainline Superfast Express (Trunk Line - stops only at major hubs)
        {
            "route_id": "RT_MAIN_EXP",
            "name": "Deccan Superfast Express",
            "train_type": "Express",
            "speed_kmh": 85.0,
            "dwell_min": 5,
            "stops": ["STN_01", "STN_04", "STN_06", "STN_07", "STN_09", "STN_10"],
            "departure_patterns": [360, 480, 660, 840, 1020, 1200],  # 06:00, 08:00, 11:00, 14:00, 17:00, 20:00
            "bidirectional": True
        },
        # Route 2: Mainline Local Passenger (Stops at all 10 stations on Trunk Line)
        {
            "route_id": "RT_MAIN_LOC",
            "name": "Central All-Station Passenger",
            "train_type": "Regional",
            "speed_kmh": 50.0,
            "dwell_min": 3,
            "stops": ["STN_01", "STN_02", "STN_03", "STN_04", "STN_05", "STN_06", "STN_07", "STN_08", "STN_09", "STN_10"],
            "departure_patterns": [330, 450, 570, 690, 810, 930, 1050, 1170],  # Every 2 hours
            "bidirectional": True
        },
        # Route 3: Western Coast Shuttle (Westport to River Jct via Oceanview)
        {
            "route_id": "RT_WEST_SHUTTLE",
            "name": "Coastal Breeze Shuttle",
            "train_type": "Regional",
            "speed_kmh": 55.0,
            "dwell_min": 3,
            "stops": ["STN_11", "STN_12", "STN_13", "STN_14", "STN_04"],
            "departure_patterns": [360, 480, 600, 720, 840, 960, 1080, 1200],
            "bidirectional": True
        },
        # Route 4: Western Express (Westport to Metro Interchange via Oceanview)
        {
            "route_id": "RT_WEST_EXP",
            "name": "Western Harbor Express",
            "train_type": "Express",
            "speed_kmh": 75.0,
            "dwell_min": 4,
            "stops": ["STN_11", "STN_13", "STN_14", "STN_06"],
            "departure_patterns": [420, 540, 720, 900, 1080],  # 07:00, 09:00, 12:00, 15:00, 18:00
            "bidirectional": True
        },
        # Route 5: Eastern Industrial Feeder (Eastport to Metro Interchange via Steel Mill)
        {
            "route_id": "RT_EAST_FEEDER",
            "name": "Industrial Commuter",
            "train_type": "Regional",
            "speed_kmh": 50.0,
            "dwell_min": 3,
            "stops": ["STN_15", "STN_16", "STN_17", "STN_06"],
            "departure_patterns": [390, 510, 630, 750, 870, 990, 1110],
            "bidirectional": True
        },
        # Route 6: Mineral Freight & Passenger (Coalfields to Highland Jct via Steel Mill & Powergate)
        {
            "route_id": "RT_MINERAL_LINK",
            "name": "Highland Coalfields Link",
            "train_type": "Regional",
            "speed_kmh": 48.0,
            "dwell_min": 4,
            "stops": ["STN_18", "STN_16", "STN_19", "STN_07"],
            "departure_patterns": [360, 540, 720, 900, 1080],
            "bidirectional": True
        },
        # Route 7: Southern Ring Line (South Central to Metro Interchange via Lakeside & Forest Edge)
        {
            "route_id": "RT_SOUTH_RING",
            "name": "Southern Valley Circular",
            "train_type": "Regional",
            "speed_kmh": 52.0,
            "dwell_min": 3,
            "stops": ["STN_01", "STN_20", "STN_21", "STN_22", "STN_23", "STN_24", "STN_25", "STN_06"],
            "departure_patterns": [345, 465, 585, 705, 825, 945, 1065, 1185],
            "bidirectional": True
        },
        # Route 8: Cross Country Express (Forest Edge to Highland Jct via Greenfield & Metro Interchange)
        {
            "route_id": "RT_CROSS_EXP",
            "name": "Midland Inter-Corridor Express",
            "train_type": "Express",
            "speed_kmh": 80.0,
            "dwell_min": 5,
            "stops": ["STN_21", "STN_24", "STN_06", "STN_07"],
            "departure_patterns": [400, 580, 760, 940, 1120],
            "bidirectional": True
        },
        # Route 9: Northern Spur Branch (Highland Jct to Canyon Pass via Sunburst)
        {
            "route_id": "RT_NORTH_SPUR",
            "name": "Canyon Mountain Explorer",
            "train_type": "Regional",
            "speed_kmh": 45.0,
            "dwell_min": 3,
            "stops": ["STN_07", "STN_26", "STN_27", "STN_28"],
            "departure_patterns": [420, 540, 660, 780, 900, 1020, 1140],
            "bidirectional": True
        },
        # Route 10: River-to-Greenfield Cross Link
        {
            "route_id": "RT_RIVER_CROSS",
            "name": "Riverdale Plains Link",
            "train_type": "Regional",
            "speed_kmh": 50.0,
            "dwell_min": 3,
            "stops": ["STN_04", "STN_23", "STN_24"],
            "departure_patterns": [400, 550, 700, 850, 1000, 1150],
            "bidirectional": True
        }
    ]
    return routes


def generate_connections(stations: List[Dict], routes: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate realistic scheduled train connections.
    Returns:
        - List of train services
        - List of individual timetable connection segments
    """
    stn_map = {s["station_id"]: s for s in stations}
    services = []
    connections = []
    conn_counter = 1

    for r_idx, route in enumerate(routes):
        directions = [("FWD", route["stops"])]
        if route.get("bidirectional", True):
            directions.append(("REV", list(reversed(route["stops"]))))

        for dir_name, stop_sequence in directions:
            for dep_idx, start_dep_time in enumerate(route["departure_patterns"]):
                service_id = f"SRV_{route['route_id']}_{dir_name}_{dep_idx+1:02d}"
                service_name = f"{route['name']} ({'Up' if dir_name == 'FWD' else 'Down'} #{dep_idx+1})"

                current_time = start_dep_time
                service_legs = []

                for i in range(len(stop_sequence) - 1):
                    u_id = stop_sequence[i]
                    v_id = stop_sequence[i + 1]
                    u_stn = stn_map[u_id]
                    v_stn = stn_map[v_id]

                    dist_km = haversine_dist(u_stn["lat"], u_stn["lon"], v_stn["lat"], v_stn["lon"])
                    # Add 15% track winding factor
                    actual_dist_km = round(dist_km * 1.15, 1)

                    # Travel time calculation in minutes
                    travel_time_min = max(int(round((actual_dist_km / route["speed_kmh"]) * 60.0)), 8)

                    dep_time = current_time
                    arr_time = dep_time + travel_time_min

                    # Don't exceed 24 hours schedule
                    if arr_time >= 1440:
                        break

                    conn_id = f"CONN_{conn_counter:04d}"
                    conn_counter += 1

                    conn_record = {
                        "connection_id": conn_id,
                        "service_id": service_id,
                        "service_name": service_name,
                        "train_type": route["train_type"],
                        "from_station_id": u_id,
                        "to_station_id": v_id,
                        "departure_time": dep_time,
                        "departure_hhmm": format_hhmm(dep_time),
                        "arrival_time": arr_time,
                        "arrival_hhmm": format_hhmm(arr_time),
                        "duration_min": travel_time_min,
                        "distance_km": actual_dist_km,
                        "seq_in_service": i + 1
                    }
                    connections.append(conn_record)
                    service_legs.append(conn_id)

                    # Next departure includes station dwell time
                    current_time = arr_time + route["dwell_min"]

                if service_legs:
                    services.append({
                        "service_id": service_id,
                        "service_name": service_name,
                        "route_id": route["route_id"],
                        "train_type": route["train_type"],
                        "direction": dir_name,
                        "first_departure": start_dep_time,
                        "first_departure_hhmm": format_hhmm(start_dep_time),
                        "final_arrival": connections[-1]["arrival_time"],
                        "final_arrival_hhmm": format_hhmm(connections[-1]["arrival_time"]),
                        "origin_station": stop_sequence[0],
                        "destination_station": stop_sequence[-1],
                        "total_legs": len(service_legs),
                        "connection_ids": service_legs
                    })

    return services, connections


def build_and_save_dataset():
    """Build dataset and persist to CSV and JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    stations = get_station_definitions()
    routes = define_train_routes()
    services, connections = generate_connections(stations, routes)

    # 1. Save data/railway_stations.csv
    stations_csv_path = os.path.join(DATA_DIR, "railway_stations.csv")
    with open(stations_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["station_id", "name", "code", "lat", "lon", "min_transfer_min", "is_junction", "corridor"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stations)

    # 2. Save data/train_connections.csv
    connections_csv_path = os.path.join(DATA_DIR, "train_connections.csv")
    with open(connections_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "connection_id", "service_id", "service_name", "train_type",
            "from_station_id", "to_station_id", "departure_time", "departure_hhmm",
            "arrival_time", "arrival_hhmm", "duration_min", "distance_km", "seq_in_service"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(connections)

    # 3. Save data/railway_network.json
    network_json_path = os.path.join(DATA_DIR, "railway_network.json")
    network_payload = {
        "metadata": {
            "name": "Intercity Regional Railway Network Dataset",
            "version": "1.0.0",
            "is_synthetic": True,
            "random_seed": RANDOM_SEED,
            "description": "Reproducible synthetic multi-corridor railway timetable network modeling realistic train journeys, transfer buffers, and multi-service scheduling.",
            "total_stations": len(stations),
            "total_routes": len(routes),
            "total_services": len(services),
            "total_connections": len(connections)
        },
        "stations": stations,
        "routes": routes,
        "services": services,
        "connections": connections
    }
    with open(network_json_path, mode="w", encoding="utf-8") as f:
        json.dump(network_payload, f, indent=2)

    print(f"Dataset generated successfully:")
    print(f"  Stations: {len(stations)} saved to {stations_csv_path}")
    print(f"  Train Services: {len(services)}")
    print(f"  Train Connections: {len(connections)} saved to {connections_csv_path}")
    print(f"  Complete Network Graph saved to {network_json_path}")


if __name__ == "__main__":
    build_and_save_dataset()

