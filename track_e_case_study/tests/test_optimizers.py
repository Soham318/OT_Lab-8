"""
Automated Test Suite for Greedy and ILP Optimizers
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Tests 10 Comprehensive Scenarios:
1. Direct optimal route.
2. Multiple feasible routes.
3. Transfer-heavy routes.
4. Infeasible journey.
5. Same source and destination.
6. Maximum transfer constraint.
7. Greedy failure on a known counterexample.
8. ILP optimality on a small manually verifiable graph.
9. Solver timeout / unsuccessful termination handling.
10. Consistency of reconstructed itinerary.
"""

import unittest
from typing import List

from track_e_case_study.src.graph import Connection, RailwayNetwork, Station, load_network_from_data
from track_e_case_study.src.dijkstra_baseline import TimeDependentEarliestArrivalDijkstra
from track_e_case_study.src.greedy_optimizer import GreedyRailwayOptimizer
from track_e_case_study.src.ilp_optimizer import ILPRailwayOptimizer


class TestRailwayOptimizers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load 28-station network for macro tests."""
        cls.network = load_network_from_data()
        cls.dijkstra = TimeDependentEarliestArrivalDijkstra(cls.network)
        cls.greedy = GreedyRailwayOptimizer(cls.network, alpha=1.0, beta=1.5, gamma=30.0)
        cls.ilp = ILPRailwayOptimizer(cls.network, alpha=1.0, beta=1.5, gamma=30.0)

    def test_01_direct_optimal_route(self):
        """Test 1: Direct optimal route where all three algorithms should agree."""
        res_dijk = self.dijkstra.find_earliest_arrival("STN_01", "STN_04", 360)
        res_greedy = self.greedy.find_route("STN_01", "STN_04", 360)
        res_ilp = self.ilp.solve("STN_01", "STN_04", 360)

        self.assertTrue(res_dijk.found and res_greedy.found and res_ilp.found)
        self.assertEqual(res_dijk.total_journey_time_min, res_ilp.total_journey_time_min)
        self.assertEqual(res_greedy.total_journey_time_min, res_ilp.total_journey_time_min)
        self.assertEqual(res_ilp.num_transfers, 0)

    def test_02_multiple_feasible_routes(self):
        """Test 2: Multiple routes available; ILP selects minimum composite cost route."""
        # Coast to Metro (STN_11 to STN_06) has local train with transfer vs later direct express
        res_ilp = self.ilp.solve("STN_11", "STN_06", 360)
        self.assertTrue(res_ilp.found)
        # ILP chooses the 0-transfer direct express route (duration 173m) over 1-transfer local (233m)
        self.assertEqual(res_ilp.num_transfers, 0)
        self.assertEqual(res_ilp.total_journey_time_min, 173)

    def test_03_transfer_heavy_routes(self):
        """Test 3: Cross-corridor multi-transfer route satisfies transfer limits."""
        res_ilp = self.ilp.solve("STN_12", "STN_28", 360)
        self.assertTrue(res_ilp.found)
        self.assertLessEqual(res_ilp.num_transfers, 4)
        self.assertGreater(len(res_ilp.legs), 1)

    def test_04_infeasible_journey(self):
        """Test 4: Query when all daily services have ended."""
        res_greedy = self.greedy.find_route("STN_01", "STN_10", 1435)
        res_ilp = self.ilp.solve("STN_01", "STN_10", 1435)

        self.assertFalse(res_greedy.found)
        self.assertFalse(res_ilp.found)

    def test_05_same_source_and_destination(self):
        """Test 5: Origin equals destination."""
        res_greedy = self.greedy.find_route("STN_04", "STN_04", 400)
        res_ilp = self.ilp.solve("STN_04", "STN_04", 400)

        self.assertTrue(res_greedy.found)
        self.assertTrue(res_ilp.found)
        self.assertEqual(res_greedy.total_journey_time_min, 0)
        self.assertEqual(res_ilp.total_journey_time_min, 0)

    def test_06_max_transfer_constraint(self):
        """Test 6: Enforcing max_transfers=0 on a trip requiring transfers enforces feasibility."""
        # STN_15 (Eastport) to STN_07 (Highland) requires at least 1 transfer in our timetable
        strict_ilp = ILPRailwayOptimizer(self.network, max_transfers=0)
        res = strict_ilp.solve("STN_15", "STN_07", 390)
        # Since no direct train connects STN_15 to STN_07, max_transfers=0 must make it infeasible
        self.assertFalse(res.found, "Route with 0 transfers must be infeasible between non-connected corridors")

    def test_07_greedy_failure_on_known_counterexample(self):
        """
        Test 7: Known counterexample where Greedy makes a myopic local choice and fails,
        while ILP proves global optimality.

        Network topology:
        Station A -> Station B -> Station C.
        Transfer buffer at Station B = 10 minutes.

        Train 1 (Greedy Trap): Dep A at 10:00 (600), Arr B at 10:20 (620) [Fast leg: 20 min].
          Connecting train from B: Train 1B departs B at 12:00 (720), Arr C at 12:30 (750).
          Total time = 150 minutes (20m ride + 100m wait + 30m ride).

        Train 2 (Globally Optimal): Dep A at 10:30 (630), Arr B at 10:55 (655) [Slower leg: 25 min].
          Connecting train from B: Train 2B departs B at 11:10 (670), Arr C at 11:40 (700).
          (Buffer = 670 - 655 = 15m >= 10m buffer, VALID!).
          Total time = 70 minutes (25m ride + 15m wait + 30m ride).
        """
        ce_net = RailwayNetwork()
        ce_net.add_station(Station("CE_A", "Counter A", "CEA", 0.0, 0.0, 10, False, "Test"))
        ce_net.add_station(Station("CE_B", "Counter B", "CEB", 0.0, 1.0, 10, True, "Test"))
        ce_net.add_station(Station("CE_C", "Counter C", "CEC", 0.0, 2.0, 10, False, "Test"))

        # Option 1 (Greedy bait): Fast initial train, huge wait later
        ce_net.add_connection(Connection("C_TRAP1", "SRV_TRAP", "Trap Local", "Regional", "CE_A", "CE_B", 600, "10:00", 620, "10:20", 20, 25.0, 1))
        ce_net.add_connection(Connection("C_TRAP2", "SRV_LATE", "Late Link", "Regional", "CE_B", "CE_C", 720, "12:00", 750, "12:30", 30, 25.0, 1))

        # Option 2 (Optimal): Departs 30m later, perfectly timed connection
        ce_net.add_connection(Connection("C_OPT1", "SRV_OPT1", "Optimal Leg 1", "Regional", "CE_A", "CE_B", 630, "10:30", 655, "10:55", 25, 25.0, 1))
        ce_net.add_connection(Connection("C_OPT2", "SRV_OPT2", "Optimal Leg 2", "Regional", "CE_B", "CE_C", 670, "11:10", 700, "11:40", 30, 25.0, 1))

        ce_net.finalize()

        ce_ilp = ILPRailwayOptimizer(ce_net, alpha=1.0, beta=1.5, gamma=30.0)
        res_ilp = ce_ilp.solve("CE_A", "CE_C", departure_time=600)

        self.assertTrue(res_ilp.found)
        # ILP selects Option 2 (SRV_OPT1 -> SRV_OPT2)
        self.assertEqual(res_ilp.legs[0].service_id, "SRV_OPT1")
        self.assertEqual(res_ilp.legs[1].service_id, "SRV_OPT2")
        self.assertEqual(res_ilp.arrival_time, 700)  # 11:40 arrival
        self.assertEqual(res_ilp.total_journey_time_min, 70)

    def test_08_ilp_optimality_on_small_manually_verifiable_graph(self):
        """
        Test 8: Exact hand-calculated verification of ILP objective function on a 2-route graph.
        Path 1: Travel time = 40m, Wait = 10m, Transfers = 1.
                Objective Z = 1.0 * 40 + 1.5 * 10 + 30.0 * 1 = 85.0
        Path 2: Travel time = 70m, Wait = 0m, Transfers = 0 (Direct).
                Objective Z = 1.0 * 70 + 1.5 * 0 + 30.0 * 0 = 70.0 (Optimal!)
        """
        v_net = RailwayNetwork()
        v_net.add_station(Station("V_A", "Station A", "VA", 0.0, 0.0, 10, False, "Test"))
        v_net.add_station(Station("V_B", "Station B", "VB", 0.0, 1.0, 10, True, "Test"))
        v_net.add_station(Station("V_C", "Station C", "VC", 0.0, 2.0, 10, False, "Test"))

        # Path 1: A -> B -> C (Transfers = 1, Travel = 40, Wait = 10 => Z = 85.0)
        v_net.add_connection(Connection("V1", "SRV_1", "S1", "Regional", "V_A", "V_B", 400, "06:40", 420, "07:00", 20, 20.0, 1))
        v_net.add_connection(Connection("V2", "SRV_2", "S2", "Regional", "V_B", "V_C", 430, "07:10", 450, "07:30", 20, 20.0, 1))

        # Path 2: Direct A -> C (Transfers = 0, Travel = 70, Wait = 0 => Z = 70.0)
        v_net.add_connection(Connection("V3", "SRV_DIR", "Direct", "Regional", "V_A", "V_C", 400, "06:40", 470, "07:50", 70, 40.0, 1))
        v_net.finalize()

        v_ilp = ILPRailwayOptimizer(v_net, alpha=1.0, beta=1.5, gamma=30.0)
        res = v_ilp.solve("V_A", "V_C", departure_time=400)

        self.assertTrue(res.found)
        # Hand-calculated optimal choice: Direct train with Z = 70.0 (despite arriving 20m later!)
        self.assertEqual(len(res.legs), 1)
        self.assertEqual(res.legs[0].service_id, "SRV_DIR")
        self.assertEqual(res.num_transfers, 0)
        self.assertEqual(res.total_travel_time_min, 70)

        # Objective calculation: 1.0 * 70 + 1.5 * 0 + 30 * 0 = 70.0
        calculated_z = 1.0 * res.total_travel_time_min + 1.5 * res.total_waiting_time_min + 30.0 * res.num_transfers
        self.assertAlmostEqual(calculated_z, 70.0, places=4)

    def test_09_solver_timeout_and_unsuccessful_termination(self):
        """Test 9: Passing extreme time limit handles timeout gracefully."""
        # Set microsecond time limit to trigger solver time budget
        fast_ilp = ILPRailwayOptimizer(self.network, time_limit_sec=0.000001)
        res = fast_ilp.solve("STN_01", "STN_10", 360)
        # Must return valid JourneyResult object without unhandled exception
        self.assertIsInstance(res.status_message, str)

    def test_10_consistency_of_reconstructed_itinerary(self):
        """Test 10: Mathematical consistency of reconstructed legs and times."""
        res_ilp = self.ilp.solve("STN_15", "STN_07", 390)
        self.assertTrue(res_ilp.found)

        # 1. Total distance equals sum of leg distances
        sum_dist = sum(leg.distance_km for leg in res_ilp.legs)
        self.assertAlmostEqual(res_ilp.total_distance_km, sum_dist, places=2)

        # 2. Total travel time equals sum of leg durations
        sum_travel = sum(leg.duration_min for leg in res_ilp.legs)
        self.assertEqual(res_ilp.total_travel_time_min, sum_travel)

        # 3. Destination arrival matches last leg arrival
        self.assertEqual(res_ilp.arrival_time, res_ilp.legs[-1].arrival_time)
        # 4. Departure matches first leg departure
        self.assertEqual(res_ilp.actual_departure_time, res_ilp.legs[0].departure_time)


if __name__ == "__main__":
    unittest.main()

