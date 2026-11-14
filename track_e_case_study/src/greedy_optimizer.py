"""
Greedy Railway Route Optimizer
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Heuristic multi-objective search balancing:
  - Journey duration (alpha)
  - Transfer waiting time (beta)
  - Number of transfers (gamma)
  - Estimated remaining time to destination (heuristic h(v))
  - Cycle prevention and transfer buffer enforcement.
"""

import math
import time
from typing import Dict, List, Optional, Set, Tuple

from .graph import Connection, RailwayNetwork, Station
from .journey_result import JourneyLeg, JourneyResult, format_hhmm


class GreedyRailwayOptimizer:
    """
    Greedy optimization heuristic for railway route and transfer selection.

    At each decision station, the algorithm evaluates all feasible outgoing connections
    and greedily selects the step minimizing a composite cost function:
        score(c) = alpha * duration(c) + beta * wait(c) + gamma * is_transfer + h(to_station)

    Why it is a heuristic:
    Greedy algorithms make myopic, locally optimal choices at each decision point.
    In scheduled timetable networks, a locally optimal choice (e.g. boarding the immediately
    departing train or taking a fast express segment) can cause the passenger to miss a critical
    tight connection downstream, requiring an extensive dwell for the next service.
    Hence, greedy selection does NOT guarantee a globally optimal solution.
    """

    def __init__(
        self,
        network: RailwayNetwork,
        alpha: float = 1.0,
        beta: float = 1.5,
        gamma: float = 30.0,
        max_transfers: int = 4
    ):
        """
        Initialize the greedy optimizer with configurable objective weights.

        Args:
            network: RailwayNetwork instance.
            alpha: Weight on in-vehicle travel duration.
            beta: Weight on transfer waiting time.
            gamma: Fixed penalty per interchange transfer.
            max_transfers: Maximum allowed service transfers along the route.
        """
        self.network = network
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.max_transfers = max_transfers
        self.max_speed_kmh = 85.0  # Max network express speed for admissible heuristic

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in km."""
        R = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
        return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _heuristic_remaining_time(self, current_stn_id: str, dest_stn_id: str) -> float:
        """Lower-bound estimate of remaining in-vehicle travel time in minutes."""
        if current_stn_id == dest_stn_id:
            return 0.0
        u = self.network.get_station(current_stn_id)
        v = self.network.get_station(dest_stn_id)
        dist = self._haversine_km(u.lat, u.lon, v.lat, v.lon)
        return (dist / self.max_speed_kmh) * 60.0

    def find_route(
        self,
        source_id: str,
        destination_id: str,
        departure_time: int
    ) -> JourneyResult:
        """
        Execute greedy path search from source_id to destination_id at or after departure_time.
        """
        start_time_wall = time.perf_counter()

        # Validation 1: Check station IDs
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
                algorithm="GreedyRailwayOptimizer",
                computation_time_ms=elapsed_ms,
                status_message="Source and destination are identical."
            )

        # Greedy Search with backtracking stack to avoid getting stuck in dead ends
        # Each stack state: (curr_station, curr_time, incoming_service, path, visited_stations, num_transfers)
        best_solution: Optional[List[Tuple[Connection, int, bool]]] = None
        best_objective_value = float("inf")

        # Priority/Beam list of exploration states
        # For a greedy heuristic, we maintain the search frontier sorted by cumulative composite cost
        frontier = [(0.0, source_id, departure_time, None, [], {source_id}, 0)]
        max_steps = 500  # Avoid runaway search
        steps = 0

        while frontier and steps < max_steps:
            steps += 1
            # Sort frontier by composite cost and pick the greedily best state
            frontier.sort(key=lambda s: s[0])
            cost_so_far, curr_stn, curr_time, incoming_srv, path, visited_stns, xfer_count = frontier.pop(0)

            # Destination check
            if curr_stn == destination_id:
                if cost_so_far < best_objective_value:
                    best_solution = path
                    best_objective_value = cost_so_far
                # For pure greedy, first arrival at destination is accepted
                break

            # Find feasible outgoing connections
            outgoing = self.network.outgoing_by_station.get(curr_stn, [])
            candidate_branches = []

            for conn in outgoing:
                next_stn = conn.to_station_id

                # Cycle prevention: do not revisit stations already in path
                if next_stn in visited_stns and next_stn != destination_id:
                    continue

                # Feasibility check
                if incoming_srv is None:
                    # Initial departure from origin
                    ready_time = departure_time
                    wait_time = conn.departure_time - departure_time
                    is_transfer = False
                    new_xfer_count = 0
                elif conn.service_id == incoming_srv:
                    # Staying on same train
                    ready_time = curr_time
                    wait_time = conn.departure_time - curr_time
                    is_transfer = False
                    new_xfer_count = xfer_count
                else:
                    # Changing service
                    transfer_buffer = self.network.get_station(curr_stn).min_transfer_min
                    ready_time = curr_time + transfer_buffer
                    wait_time = conn.departure_time - curr_time
                    is_transfer = True
                    new_xfer_count = xfer_count + 1

                # Buffer feasibility and maximum transfer limit
                if conn.departure_time < ready_time:
                    continue
                if new_xfer_count > self.max_transfers:
                    continue

                # Compute step cost and heuristic estimate
                step_cost = (
                    self.alpha * conn.duration_min +
                    self.beta * wait_time +
                    self.gamma * (1.0 if is_transfer else 0.0)
                )
                h_remaining = self.alpha * self._heuristic_remaining_time(next_stn, destination_id)
                projected_total = cost_so_far + step_cost + h_remaining

                candidate_branches.append((
                    projected_total,
                    cost_so_far + step_cost,
                    next_stn,
                    conn.arrival_time,
                    conn.service_id,
                    path + [(conn, wait_time, is_transfer)],
                    visited_stns | {next_stn},
                    new_xfer_count
                ))

            # Greedily retain top candidate branches
            if candidate_branches:
                candidate_branches.sort(key=lambda b: b[0])
                # Keep top 3 best greedy branches to allow local exploration
                for b in candidate_branches[:3]:
                    frontier.append((b[1], b[2], b[3], b[4], b[5], b[6], b[7]))

        elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0

        if best_solution is None:
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="GreedyRailwayOptimizer",
                computation_time_ms=elapsed_ms,
                status_message="No feasible route found satisfying greedy constraints."
            )

        # Reconstruct journey
        legs: List[JourneyLeg] = []
        total_travel_time = 0
        total_waiting_time = 0
        num_transfers = 0
        total_distance = 0.0

        for conn, wait_time, is_xfer in best_solution:
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
            algorithm="GreedyRailwayOptimizer",
            computation_time_ms=elapsed_ms,
            status_message="Greedy heuristic solution found."
        )

