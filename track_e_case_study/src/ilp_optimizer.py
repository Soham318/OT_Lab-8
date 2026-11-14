r"""
Exact Integer Linear Programming (ILP) Railway Route Optimizer
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Solves the multi-objective railway routing problem to proven global optimality using:
    scipy.optimize.milp (HiGHS solver)

Formulation:
  Binary decision variables:
    x_c \in {0, 1}: Indicator for connection c
    y_{c1, c2} \in {0, 1}: Indicator for transfer/transition from c1 to c2

  Objective:
    min \alpha \sum \tau(c) x_c + \beta \sum w(c1, c2) y_{c1, c2} + \gamma \sum \delta_{xfer}(c1, c2) y_{c1, c2}

  Constraints:
    - Flow conservation and connection continuity (x_c linked with y_{c1, c2})
    - Single origin departure on or after query time
    - Single destination arrival
    - Station-specific transfer buffer enforcement
    - Maximum transfer count limit
"""

import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
from scipy.optimize import LinearConstraint, milp
from scipy.sparse import csc_matrix, dok_matrix

from .graph import Connection, RailwayNetwork, Station
from .journey_result import JourneyLeg, JourneyResult, format_hhmm


class ILPRailwayOptimizer:
    """
    Exact Integer Linear Programming (ILP) Optimizer for Railway Route and Transfer Selection.
    Uses HiGHS via scipy.optimize.milp.
    """

    def __init__(
        self,
        network: RailwayNetwork,
        alpha: float = 1.0,
        beta: float = 1.5,
        gamma: float = 30.0,
        max_transfers: int = 4,
        time_limit_sec: float = 30.0
    ):
        self.network = network
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.max_transfers = max_transfers
        self.time_limit_sec = time_limit_sec

    def solve(
        self,
        source_id: str,
        destination_id: str,
        departure_time: int
    ) -> JourneyResult:
        """
        Solve the exact binary ILP for routing from source_id to destination_id.
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
                algorithm="ILPRailwayOptimizer (HiGHS)",
                computation_time_ms=elapsed_ms,
                status_message="Source and destination are identical."
            )

        # 1. Filter candidate connections
        # A connection can only be used if it departs on or after departure_time,
        # or can be reached downstream after departure_time
        candidate_conns: List[Connection] = []
        conn_to_idx: Dict[str, int] = {}

        for conn in self.network.connections:
            # Connections departing origin before query departure_time are strictly excluded
            if conn.from_station_id == source_id and conn.departure_time < departure_time:
                continue
            # Connections departing too early anywhere in the network are pruned
            if conn.departure_time < departure_time:
                continue

            conn_to_idx[conn.connection_id] = len(candidate_conns)
            candidate_conns.append(conn)

        num_conns = len(candidate_conns)
        if num_conns == 0:
            elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="ILPRailwayOptimizer (HiGHS)",
                computation_time_ms=elapsed_ms,
                status_message="No connections available on or after departure time."
            )

        # 2. Identify feasible transfers / transitions (c1 -> c2)
        # c1 arrives at station u, c2 departs from station u
        transfers: List[Tuple[int, int, int, bool]] = []
        # Index outgoing candidates by from_station_id
        outgoing_cands: Dict[str, List[int]] = {}
        for c2_idx, c2 in enumerate(candidate_conns):
            if c2.from_station_id not in outgoing_cands:
                outgoing_cands[c2.from_station_id] = []
            outgoing_cands[c2.from_station_id].append(c2_idx)

        for c1_idx, c1 in enumerate(candidate_conns):
            # Don't need outgoing transfers from destination
            if c1.to_station_id == destination_id:
                continue

            stn_u = c1.to_station_id
            stn_obj = self.network.get_station(stn_u)
            transfer_buffer = stn_obj.min_transfer_min

            possible_c2 = outgoing_cands.get(stn_u, [])
            for c2_idx in possible_c2:
                c2 = candidate_conns[c2_idx]

                if c1.service_id == c2.service_id:
                    # Same train continuation
                    if c2.departure_time >= c1.arrival_time:
                        wait = c2.departure_time - c1.arrival_time
                        transfers.append((c1_idx, c2_idx, wait, False))
                else:
                    # Service transfer: requires min_transfer_min buffer
                    if c2.departure_time >= c1.arrival_time + transfer_buffer:
                        wait = c2.departure_time - c1.arrival_time
                        transfers.append((c1_idx, c2_idx, wait, True))

        num_transfers = len(transfers)
        total_vars = num_conns + num_transfers

        # Mapping for variable indices:
        # 0 <= i < num_conns: x_c
        # num_conns <= j < num_conns + num_transfers: y_{c1, c2}
        x_indices = np.arange(num_conns)
        y_indices = np.arange(num_conns, total_vars)

        # 3. Build Cost Vector (c)
        c_cost = np.zeros(total_vars, dtype=np.float64)
        for i, conn in enumerate(candidate_conns):
            c_cost[i] = self.alpha * conn.duration_min

        for j, (c1_idx, c2_idx, wait, is_xfer) in enumerate(transfers):
            var_idx = num_conns + j
            xfer_penalty = self.gamma if is_xfer else 0.0
            c_cost[var_idx] = self.beta * wait + xfer_penalty

        # 4. Build Constraints
        # Let's count rows:
        # - Row 0: Origin departure balance: sum_{c from orig} (x_c - sum_{incoming} y) = 1
        # - Row 1: Destination arrival balance: sum_{c to dest} (x_c - sum_{outgoing} y) = 1
        # - Forward linking for intermediate conns: sum_{c2: (c, c2)} y_{c, c2} == x_c  (for c where c.to != dest)
        # - Backward linking for intermediate conns: sum_{c1: (c1, c)} y_{c1, c} == x_c  (for c where c.from != orig)
        # - Max transfer constraint: sum_{transfers with is_xfer} y <= max_transfers

        # Index transfers by c1 and c2
        transfers_by_c1: Dict[int, List[int]] = {i: [] for i in range(num_conns)}
        transfers_by_c2: Dict[int, List[int]] = {i: [] for i in range(num_conns)}
        for j, (c1_idx, c2_idx, wait, is_xfer) in enumerate(transfers):
            transfers_by_c1[c1_idx].append(num_conns + j)
            transfers_by_c2[c2_idx].append(num_conns + j)

        rows = []
        b_l = []
        b_u = []

        # Constraint 1: Exactly 1 journey start at origin
        # sum_{c: from=orig} x_c - sum_{incoming to those c} y == 1
        # More simply, exactly one connection departing origin has no incoming transfer:
        orig_conn_indices = [i for i, conn in enumerate(candidate_conns) if conn.from_station_id == source_id]
        if not orig_conn_indices:
            elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="ILPRailwayOptimizer (HiGHS)",
                computation_time_ms=elapsed_ms,
                status_message="No train departures from origin station on or after departure time."
            )

        row_orig = {}
        for c_idx in orig_conn_indices:
            row_orig[c_idx] = 1.0
            for y_var in transfers_by_c2[c_idx]:
                row_orig[y_var] = -1.0
        rows.append(row_orig)
        b_l.append(1.0)
        b_u.append(1.0)

        # Constraint 2: Exactly 1 journey termination at destination
        # sum_{c: to=dest} x_c - sum_{outgoing from those c} y == 1
        dest_conn_indices = [i for i, conn in enumerate(candidate_conns) if conn.to_station_id == destination_id]
        if not dest_conn_indices:
            elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="ILPRailwayOptimizer (HiGHS)",
                computation_time_ms=elapsed_ms,
                status_message="No train arrivals at destination station in timetable."
            )

        row_dest = {}
        for c_idx in dest_conn_indices:
            row_dest[c_idx] = 1.0
            for y_var in transfers_by_c1[c_idx]:
                row_dest[y_var] = -1.0
        rows.append(row_dest)
        b_l.append(1.0)
        b_u.append(1.0)

        # Constraint 3: Forward linking for intermediate connections
        # For every c where c.to != destination:
        # sum_{c2: (c, c2) \in T} y_{c, c2} == x_c  <=> sum y - x_c == 0
        for c_idx, conn in enumerate(candidate_conns):
            if conn.to_station_id != destination_id:
                row = {c_idx: -1.0}
                for y_var in transfers_by_c1[c_idx]:
                    row[y_var] = 1.0
                rows.append(row)
                b_l.append(0.0)
                b_u.append(0.0)

        # Constraint 4: Backward linking for intermediate connections
        # For every c where c.from != origin:
        # sum_{c1: (c1, c) \in T} y_{c1, c} == x_c <=> sum y - x_c == 0
        for c_idx, conn in enumerate(candidate_conns):
            if conn.from_station_id != source_id:
                row = {c_idx: -1.0}
                for y_var in transfers_by_c2[c_idx]:
                    row[y_var] = 1.0
                rows.append(row)
                b_l.append(0.0)
                b_u.append(0.0)

        # Constraint 5: Maximum transfer count
        # sum_{(c1, c2) with is_xfer} y <= max_transfers
        xfer_vars = [num_conns + j for j, (_, _, _, is_xfer) in enumerate(transfers) if is_xfer]
        if xfer_vars:
            row_xfer = {v: 1.0 for v in xfer_vars}
            rows.append(row_xfer)
            b_l.append(0.0)
            b_u.append(float(self.max_transfers))

        # 5. Construct Sparse Matrix
        num_rows = len(rows)
        A = dok_matrix((num_rows, total_vars), dtype=np.float64)
        for r_idx, r_dict in enumerate(rows):
            for col_idx, val in r_dict.items():
                A[r_idx, col_idx] = val

        A_csc = A.tocsc()
        b_l_arr = np.array(b_l, dtype=np.float64)
        b_u_arr = np.array(b_u, dtype=np.float64)
        constraints = LinearConstraint(A_csc, b_l_arr, b_u_arr)

        # All variables are binary: integrality = 1 (1 means integer variable in scipy.optimize.milp)
        integrality = np.ones(total_vars, dtype=np.int32)
        # Variable bounds: 0 <= z <= 1
        from scipy.optimize import Bounds
        bounds = Bounds(lb=0.0, ub=1.0)

        # 6. Solve via HiGHS
        options = {
            "time_limit": self.time_limit_sec,
            "presolve": True,
            "mip_rel_gap": 1e-4
        }
        res = milp(
            c=c_cost,
            integrality=integrality,
            bounds=bounds,
            constraints=constraints,
            options=options
        )

        elapsed_ms = (time.perf_counter() - start_time_wall) * 1000.0

        if not res.success or res.x is None:
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="ILPRailwayOptimizer (HiGHS)",
                computation_time_ms=elapsed_ms,
                status_message=f"HiGHS termination: {res.status} ({res.message})"
            )

        # 7. Solution Reconstruction
        sol_z = res.x
        active_conns = [candidate_conns[i] for i in range(num_conns) if sol_z[i] > 0.5]
        active_transfers = set()
        for j, (c1_idx, c2_idx, wait, is_xfer) in enumerate(transfers):
            if sol_z[num_conns + j] > 0.5:
                active_transfers.add((candidate_conns[c1_idx].connection_id, candidate_conns[c2_idx].connection_id))

        if not active_conns:
            return JourneyResult(
                found=False,
                source_id=source_id,
                destination_id=destination_id,
                source_name=src_station.name,
                destination_name=dst_station.name,
                query_departure_time=departure_time,
                algorithm="ILPRailwayOptimizer (HiGHS)",
                computation_time_ms=elapsed_ms,
                status_message="Empty solution returned by solver."
            )

        # Order active connections starting from source_id
        conn_by_id = {c.connection_id: c for c in active_conns}
        # Find start connection
        # Start connection has from_station_id == source_id and is not the target of an active transfer
        curr_conn: Optional[Connection] = None
        for c in active_conns:
            if c.from_station_id == source_id:
                has_incoming = any(t[1] == c.connection_id for t in active_transfers)
                if not has_incoming:
                    curr_conn = c
                    break

        if curr_conn is None:
            # Fallback: connection from source with earliest departure
            curr_conn = min([c for c in active_conns if c.from_station_id == source_id], key=lambda c: c.departure_time)

        ordered_conns = []
        visited_ids = set()

        while curr_conn is not None and curr_conn.connection_id not in visited_ids:
            ordered_conns.append(curr_conn)
            visited_ids.add(curr_conn.connection_id)
            if curr_conn.to_station_id == destination_id:
                break

            # Find next connection
            next_conn = None
            for t_from, t_to in active_transfers:
                if t_from == curr_conn.connection_id and t_to in conn_by_id:
                    next_conn = conn_by_id[t_to]
                    break
            curr_conn = next_conn

        # Build JourneyLegs
        legs: List[JourneyLeg] = []
        total_travel_time = 0
        total_waiting_time = 0
        num_xfers = 0
        total_distance = 0.0

        for idx, conn in enumerate(ordered_conns):
            from_stn = self.network.get_station(conn.from_station_id)
            to_stn = self.network.get_station(conn.to_station_id)

            if idx == 0:
                wait_time = conn.departure_time - departure_time
                is_xfer = False
            else:
                prev_conn = ordered_conns[idx - 1]
                wait_time = conn.departure_time - prev_conn.arrival_time
                is_xfer = (conn.service_id != prev_conn.service_id)
                if is_xfer:
                    total_waiting_time += wait_time
                    num_xfers += 1

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

        actual_dep = legs[0].departure_time
        final_arr = legs[-1].arrival_time
        total_journey_duration = final_arr - actual_dep

        # HiGHS status 0 means Optimal solution proved
        status_desc = "Globally optimal itinerary proved by HiGHS" if res.status == 0 else f"HiGHS status: {res.status}"

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
            num_transfers=num_xfers,
            total_distance_km=total_distance,
            legs=legs,
            algorithm="ILPRailwayOptimizer (HiGHS)",
            computation_time_ms=elapsed_ms,
            status_message=status_desc
        )
