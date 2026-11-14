"""
Journey Result and Itinerary Representation
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything
"""

from dataclasses import dataclass, field
from typing import List, Optional


def format_hhmm(minutes: int) -> str:
    """Format minutes from midnight to HH:MM."""
    hrs = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hrs:02d}:{mins:02d}"


@dataclass
class JourneyLeg:
    connection_id: str
    service_id: str
    service_name: str
    train_type: str
    from_station_id: str
    from_station_name: str
    to_station_id: str
    to_station_name: str
    departure_time: int
    departure_hhmm: str
    arrival_time: int
    arrival_hhmm: str
    duration_min: int
    distance_km: float
    wait_before_dep_min: int = 0
    is_transfer: bool = False


@dataclass
class JourneyResult:
    found: bool
    source_id: str
    destination_id: str
    source_name: str = ""
    destination_name: str = ""
    query_departure_time: int = 0
    actual_departure_time: Optional[int] = None
    arrival_time: Optional[int] = None
    total_journey_time_min: int = 0
    total_travel_time_min: int = 0
    total_waiting_time_min: int = 0
    num_transfers: int = 0
    total_distance_km: float = 0.0
    legs: List[JourneyLeg] = field(default_factory=list)
    algorithm: str = "TimeDependentEarliestArrivalDijkstra"
    computation_time_ms: float = 0.0
    status_message: str = "Success"

    @property
    def departure_hhmm(self) -> str:
        return format_hhmm(self.actual_departure_time) if self.actual_departure_time is not None else "--:--"

    @property
    def arrival_hhmm(self) -> str:
        return format_hhmm(self.arrival_time) if self.arrival_time is not None else "--:--"

    def print_itinerary(self) -> str:
        """Generate human-readable itinerary table."""
        if not self.found:
            return f"No itinerary found from {self.source_id} to {self.destination_id}: {self.status_message}"

        lines = [
            f"================================================================================",
            f"JOURNEY ITINERARY: {self.source_name} -> {self.destination_name}",
            f"Algorithm: {self.algorithm} | Solved in: {self.computation_time_ms:.2f} ms",
            f"Departure: {self.departure_hhmm} | Arrival: {self.arrival_hhmm}",
            f"Total Journey Duration: {self.total_journey_time_min} min ({self.total_journey_time_min / 60:.1f} hrs)",
            f"In-Vehicle Travel Time: {self.total_travel_time_min} min | Transfer Waiting Time: {self.total_waiting_time_min} min",
            f"Transfers: {self.num_transfers} | Total Distance: {self.total_distance_km:.1f} km",
            f"--------------------------------------------------------------------------------",
            f"{'Leg':<4} {'Service / Train':<30} {'From -> To':<32} {'Dep - Arr':<13} {'Dur':<6} {'Wait':<6}"
        ]
        for idx, leg in enumerate(self.legs, 1):
            transfer_tag = " [XFER]" if leg.is_transfer else ""
            route_str = f"{leg.from_station_name[:14]} -> {leg.to_station_name[:14]}"
            times_str = f"{leg.departure_hhmm} - {leg.arrival_hhmm}"
            lines.append(
                f"{idx:<4} {leg.service_name[:28] + transfer_tag:<30} {route_str:<32} "
                f"{times_str:<13} {leg.duration_min:<6} {leg.wait_before_dep_min:<6}"
            )
        lines.append(f"================================================================================")
        return "\n".join(lines)

