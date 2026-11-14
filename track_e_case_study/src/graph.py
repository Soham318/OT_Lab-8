"""
Railway Network Data Structures and Loader
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything
"""

import csv
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Station:
    station_id: str
    name: str
    code: str
    lat: float
    lon: float
    min_transfer_min: int
    is_junction: bool
    corridor: str


@dataclass
class Connection:
    connection_id: str
    service_id: str
    service_name: str
    train_type: str
    from_station_id: str
    to_station_id: str
    departure_time: int  # minutes from midnight [0, 1440)
    departure_hhmm: str
    arrival_time: int    # minutes from midnight [0, 1440)
    arrival_hhmm: str
    duration_min: int
    distance_km: float
    seq_in_service: int


@dataclass
class RailwayNetwork:
    stations: Dict[str, Station] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)
    # Fast index: station_id -> list of outgoing connections sorted by departure_time
    outgoing_by_station: Dict[str, List[Connection]] = field(default_factory=dict)
    # Adjacency: station_id -> set of direct neighbor station_ids
    adjacent_stations: Dict[str, Set[str]] = field(default_factory=dict)

    def add_station(self, station: Station):
        self.stations[station.station_id] = station
        if station.station_id not in self.outgoing_by_station:
            self.outgoing_by_station[station.station_id] = []
        if station.station_id not in self.adjacent_stations:
            self.adjacent_stations[station.station_id] = set()

    def add_connection(self, conn: Connection):
        self.connections.append(conn)
        if conn.from_station_id not in self.outgoing_by_station:
            self.outgoing_by_station[conn.from_station_id] = []
        self.outgoing_by_station[conn.from_station_id].append(conn)

        if conn.from_station_id not in self.adjacent_stations:
            self.adjacent_stations[conn.from_station_id] = set()
        self.adjacent_stations[conn.from_station_id].add(conn.to_station_id)

    def finalize(self):
        """Sort outgoing connections by departure time for efficient timetable search."""
        for stn_id in self.outgoing_by_station:
            self.outgoing_by_station[stn_id].sort(key=lambda c: c.departure_time)

    def get_station(self, station_id: str) -> Optional[Station]:
        return self.stations.get(station_id)

    def has_station(self, station_id: str) -> bool:
        return station_id in self.stations


def load_network_from_data(data_dir: Optional[str] = None) -> RailwayNetwork:
    """Load railway network from data/railway_stations.csv and data/train_connections.csv."""
    if data_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_dir = os.path.join(base_dir, "data")

    stations_path = os.path.join(data_dir, "railway_stations.csv")
    connections_path = os.path.join(data_dir, "train_connections.csv")

    if not os.path.exists(stations_path) or not os.path.exists(connections_path):
        raise FileNotFoundError(f"Dataset files missing in {data_dir}. Run generate_dataset.py first.")

    network = RailwayNetwork()

    # 1. Load stations
    with open(stations_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stn = Station(
                station_id=row["station_id"],
                name=row["name"],
                code=row["code"],
                lat=float(row["lat"]),
                lon=float(row["lon"]),
                min_transfer_min=int(row["min_transfer_min"]),
                is_junction=row["is_junction"].lower() in ("true", "1", "yes"),
                corridor=row["corridor"]
            )
            network.add_station(stn)

    # 2. Load connections
    with open(connections_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn = Connection(
                connection_id=row["connection_id"],
                service_id=row["service_id"],
                service_name=row["service_name"],
                train_type=row["train_type"],
                from_station_id=row["from_station_id"],
                to_station_id=row["to_station_id"],
                departure_time=int(row["departure_time"]),
                departure_hhmm=row["departure_hhmm"],
                arrival_time=int(row["arrival_time"]),
                arrival_hhmm=row["arrival_hhmm"],
                duration_min=int(row["duration_min"]),
                distance_km=float(row["distance_km"]),
                seq_in_service=int(row["seq_in_service"])
            )
            network.add_connection(conn)

    network.finalize()
    return network

