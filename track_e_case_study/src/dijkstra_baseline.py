"""
Time-Dependent Earliest-Arrival Dijkstra Algorithm (Baseline)
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything
"""

import heapq
import time
from typing import Dict, List, Optional, Set, Tuple

from .graph import Connection, RailwayNetwork, Station
from .journey_result import JourneyLeg, JourneyResult, format_hhmm


class TimeDependentEarliestArrivalDijkstra:
    """
    Computes earliest-arrival passenger railway journeys over a time-dependent timetable network.
    Correctly enforces:
      1. Earliest query departure time.
      2. Station-specific transfer buffers (Delta_min) when changing train services.
      3. Seamless through-journey when remaining on the same train service without transfer penalty.
      4. Exact route reconstruction with in-vehicle and interchange waiting time breakdown.
    """

    def __init__(self, network: RailwayNetwork):
        self.network = network

    def find_earliest_arrival(
        self,
        source_id: str,
        destination_id: str,
        departure_time: int
    ) -> JourneyResult:
        """
        Find earliest-arrival journey from source_id to destination_id departing at or after departure_time.

        Args:
            source_id: Station ID of origin.
            destination_id: Station ID of destination.
            departure_time: Earliest allowed departure time in minutes from midnight [0, 1440).

        Returns:
            JourneyResult containing itinerary, duration, waiting time, and transfers.
        """
        start_time_wall = time.perf_counter()

        # Validation 1: Check station validity
        if not self.network.has_station(source_id):
            raise ValueError(f"Invalid station ID: '{source_id}' does not exist in network.")
        if not self.network.has_station(destination_id):
            raise ValueError(f"Invalid station ID: '{destination_id}' does not exist in network.")

        src_station = self.network.get_station(source_id)
        dst_station = self.network.get_station(destination_id)

        # Validation 2: Source equals destination
        if source_id == destination_id:
            elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0
            return JourneyResult(
                found=True,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                actual_departure_time=departure_time,
                arrival_time=departure_time,
                total_journey_time_min=0,
                total_travel_time_min=0,
                total_waiting_time_min=0,
                num_transfers=0,
                total_distance_km=0.0,
                legs=[],
                algorithm="TimeDependentEarliestArrivalDijkstra",
                computation_time_ms=elapsed_ms,
                status_message="Source and destination are identical."
            )

        # Priority Queue: entries are (arrival_time, current_station_id, incoming_service_id, path_history)
        # path_history is list of tuples: (connection, wait_time, is_transfer)
        # Using counter to avoid tie-breaker comparisons on complex objects
        entry_counter = 0
        pq: List[Tuple[int, int, str, Optional[str], List[Tuple[Connection, int, bool]]]] = []

        # Best settled arrival time at (station_id, service_id)
        # Key: (station_id, service_id) -> earliest arrival time
        visited: Dict[Tuple[str, Optional[str]], int] = {}
        # Also track global best arrival per station for pruning
        best_station_arrival: Dict[str, int] = {}

        # Initial state: passenger at source station at departure_time
        heapq.heappush(pq, (departure_time, entry_counter, source_id, None, []))
        entry_counter += 1

        best_result_path: Optional[List[Tuple[Connection, int, bool]]] = None
        best_arrival_time = float("inf")

        while pq:
            curr_time, _, curr_stn, incoming_srv, path = heapq.heappop(pq)

            # Destination check: first time we reach destination, if it's earlier, save
            if curr_stn == destination_id:
                best_result_path = path
                best_arrival_time = curr_time
                break

            # Pruning check
            state_key = (curr_stn, incoming_srv)
            if state_key in visited and visited[state_key] <= curr_time:
                continue
            visited[state_key] = curr_time

            # Station level pruning: if we have reached this station earlier with another service
            # and that was long enough ago to allow any transfer, skip
            if curr_stn != source_id:
                if curr_stn in best_station_arrival:
                    stn_buffer = self.network.get_station(curr_stn).min_transfer_min
                    if curr_time > best_station_arrival[curr_stn] + stn_buffer:
                        # Cannot be optimal because an earlier passenger has already cleared transfer buffer
                        continue
                else:
                    best_station_arrival[curr_stn] = curr_time

            # Explore outgoing scheduled connections
            outgoing = self.network.outgoing_by_station.get(curr_stn, [])
            for conn in outgoing:
                # 1. Determine ready time at curr_stn
                if incoming_srv is None:
                    # Initial departure from origin
                    ready_time = departure_time
                    wait_time = conn.departure_time - departure_time
                    is_transfer = False
                elif conn.service_id == incoming_srv:
                    # Continuing on the exact same train (no transfer needed)
                    ready_time = curr_time
                    wait_time = conn.departure_time - curr_time
                    is_transfer = False
                else:
                    # Changing to a different train service (requires transfer buffer)
                    transfer_buffer = self.network.get_station(curr_stn).min_transfer_min
                    ready_time = curr_time + transfer_buffer
                    wait_time = conn.departure_time - curr_time
                    is_transfer = True

                # Check feasibility: does train depart at or after ready time?
                if conn.departure_time < ready_time:
                    continue

                next_stn = conn.to_station_id
                next_arr_time = conn.arrival_time
                next_srv = conn.service_id

                next_state_key = (next_stn, next_srv)
                if next_state_key in visited and visited[next_state_key] <= next_arr_time:
                    continue

                new_path = path + [(conn, wait_time, is_transfer)]
                heapq.heappush(pq, (next_arr_time, entry_counter, next_stn, next_srv, new_path))
                entry_counter += 1

        elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0

        if best_result_path is None:
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="TimeDependentEarliestArrivalDijkstra",
                computation_time_ms=elapsed_ms,
                status_message="No feasible route found departing on or after specified time."
            )

        # Reconstruct journey details
        legs: List[JourneyLeg] = []
        total_travel_time = 0
        total_waiting_time = 0
        num_transfers = 0
        total_distance = 0.0

        for conn, wait_time, is_xfer in best_result_path:
            from_stn = self.network.get_station(conn.from_station_id)
            to_stn = self.network.get_station(conn.to_station_id)

            leg = JourneyLeg(
                connection_id=conn.connection_id,
                service_id=conn.service_id,
                service_name=conn.service_name,
                train_type=conn.train_type,
                from_station_id=conn.from_station_id,
                from_station_name=from_stn.name,
                to_station_id=conn.to_station_id,
                to_station_name=to_stn.name,
                departure_time=conn.departure_time,
                departure_hhmm=conn.departure_hhmm,
                arrival_time=conn.arrival_time,
                arrival_hhmm=conn.arrival_hhmm,
                duration_min=conn.duration_min,
                distance_km=conn.distance_km,
                wait_before_dep_min=wait_time,
                is_transfer=is_xfer
            )
            legs.append(leg)
            total_travel_time += conn.duration_min
            total_distance += conn.distance_km
            if is_xfer:
                total_waiting_time += wait_time
                num_transfers += 1

        actual_dep = legs[0].departure_time
        final_arr = legs[-1].arrival_time
        total_journey_duration = final_arr - actual_dep

        return JourneyResult(
            found=True,
            source_id=source_id,
            destination_id=destination_id,
            source_name=src_station.name,
            destination_name=dst_station.name,
            query_departure_time=departure_time,
            actual_departure_time=actual_dep,
            arrival_time=final_arr,
            total_journey_time_min=total_journey_duration,
            total_travel_time_min=total_travel_time,
            total_waiting_time_min=total_waiting_time,
            num_transfers=num_transfers,
            total_distance_km=total_distance,
            legs=legs,
            algorithm="TimeDependentEarliestArrivalDijkstra",
            computation_time_ms=elapsed_ms,
            status_message="Optimal earliest-arrival itinerary found."
        )


class StaticDijkstraBaseline:
    """
    Standard static Dijkstra algorithm operating on the physical station graph.
    Ignores timetables, departure schedules, and transfer waiting buffers.
    Used explicitly as a baseline to demonstrate the deficiency of static graph search.
    """

    def __init__(self, network: RailwayNetwork):
        self.network = network
        # Build static adjacency with minimum observed travel time between adjacent stations
        self.static_edges: Dict[str, Dict[str, Tuple[float, float]]] = {}
        for stn_id in self.network.stations:
            self.static_edges[stn_id] = {}

        for conn in self.network.connections:
            u = conn.from_station_id
            v = conn.to_station_id
            dur = float(conn.duration_min)
            dist = float(conn.distance_km)
            if v not in self.static_edges[u] or dur < self.static_edges[u][v][0]:
                self.static_edges[u][v] = (dur, dist)

    def find_shortest_path(self, source_id: str, destination_id: str) -> Dict:
        """Find theoretical shortest topological path ignoring timetables."""
        if not self.network.has_station(source_id) or not self.network.has_station(destination_id):
            raise ValueError("Invalid station ID.")

        start_time_wall = time.perf_counter()
        dist: Dict[str, float] = {s: float("inf") for s in self.network.stations}
        prev: Dict[str, Optional[str]] = {s: None for s in self.network.stations}
        dist[source_id] = 0.0

        pq = [(0.0, source_id)]
        visited = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            if u == destination_id:
                break

            for v, (travel_time, _) in self.static_edges[u].items():
                if dist[u] + travel_time < dist[v]:
                    dist[v] = dist[u] + travel_time
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))

        elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0

        if dist[destination_id] == float("inf"):
            return {"found": False, "duration_min": None, "path": []}

        # Reconstruct path
        path = []
        curr: Optional[str] = destination_id
        while curr is not None:
            path.append(curr)
            curr = prev[curr]
        path.reverse()

        return {
            "found": True,
            "duration_min": dist[destination_id],
            "path": path,
            "computation_time_ms": elapsed_ms,
            "stations_visited": len(path)
        }

