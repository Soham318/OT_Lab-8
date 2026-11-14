"""
Automated Test Suite for Track E: Time-Dependent Earliest-Arrival Routing
Assignment 8 - Optimize Anything

Tests all 9 compulsory scenarios:
1. Direct journey.
2. One-transfer journey.
3. Multiple-transfer journey.
4. No available route.
5. Source equals destination.
6. Invalid station ID.
7. Missing train connection.
8. Transfer with insufficient connection time.
9. Journey departing on next available service.
"""

import os
import unittest
from typing import List

from track_e_case_study.src.graph import Connection, RailwayNetwork, Station, load_network_from_data
from track_e_case_study.src.dijkstra_baseline import TimeDependentEarliestArrivalDijkstra


class TestRailwayRoutingBaseline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load full 28-station network dataset."""
        cls.network = load_network_from_data()
        cls.router = TimeDependentEarliestArrivalDijkstra(cls.network)

    def test_01_direct_journey(self):
        """Scenario 1: Direct journey between adjacent mainline stations without transfer."""
        # STN_01 (South Central) to STN_04 (River Junction), departing 06:00 (360 min)
        result = self.router.find_earliest_arrival("STN_01", "STN_04", departure_time=360)

        self.assertTrue(result.found, "Direct route should be found")
        self.assertEqual(result.source_id, "STN_01")
        self.assertEqual(result.destination_id, "STN_04")
        self.assertEqual(result.num_transfers, 0, "Direct journey must have 0 transfers")
        self.assertGreater(len(result.legs), 0)

        # All legs should belong to the same service
        service_ids = {leg.service_id for leg in result.legs}
        self.assertEqual(len(service_ids), 1, "Direct journey legs must belong to the exact same service")
        self.assertEqual(result.total_waiting_time_min, 0, "No transfer wait for direct journey")
        self.assertEqual(result.total_journey_time_min, result.arrival_time - result.actual_departure_time)

    def test_02_one_transfer_journey(self):
        """Scenario 2: Journey requiring exactly one interchange transfer."""
        # Westport Bay (STN_11) to Metro Interchange (STN_06), departing 06:00 (360 min)
        # Coastal Shuttle transfers to Western Express at Dune Plains (STN_14)
        result = self.router.find_earliest_arrival("STN_11", "STN_06", departure_time=360)

        self.assertTrue(result.found, "One-transfer route should be found")
        self.assertEqual(result.num_transfers, 1, "Journey should have exactly 1 transfer")

        # Verify that the transfer occurred at an intermediate station
        transfer_legs = [leg for leg in result.legs if leg.is_transfer]
        self.assertEqual(len(transfer_legs), 1)
        transfer_station_id = transfer_legs[0].from_station_id
        transfer_station = self.network.get_station(transfer_station_id)

        # Verify transfer buffer was respected
        transfer_leg = transfer_legs[0]
        self.assertGreaterEqual(
            transfer_leg.wait_before_dep_min,
            transfer_station.min_transfer_min,
            f"Transfer wait ({transfer_leg.wait_before_dep_min}m) must be >= station buffer ({transfer_station.min_transfer_min}m)"
        )

    def test_03_multiple_transfer_journey(self):
        """Scenario 3: Cross-network journey requiring multiple transfers."""
        # Seaside Sands (STN_12) to Canyon Pass (STN_28), departing 06:00 (360 min)
        # Requires traversing Western Coast -> Mainline Trunk -> Northern Spur
        result = self.router.find_earliest_arrival("STN_12", "STN_28", departure_time=360)

        self.assertTrue(result.found, "Multi-transfer route should be found")
        self.assertGreaterEqual(result.num_transfers, 2, "Journey should require at least 2 transfers")
        self.assertGreater(result.total_waiting_time_min, 0, "Multi-transfer journey must incur waiting time")

        # Verify chronological ordering of all legs
        for i in range(len(result.legs) - 1):
            curr_leg = result.legs[i]
            next_leg = result.legs[i + 1]
            self.assertEqual(curr_leg.to_station_id, next_leg.from_station_id, "Connected stations must match")
            self.assertLessEqual(curr_leg.arrival_time, next_leg.departure_time, "Arrival must precede next departure")

    def test_04_no_available_route(self):
        """Scenario 4: Querying at the end of the day when all services have concluded."""
        # Query at 23:55 (1435 min) when no more trains depart for the day
        result = self.router.find_earliest_arrival("STN_01", "STN_10", departure_time=1435)

        self.assertFalse(result.found, "Should report no route found when schedule has ended")
        self.assertIn("No feasible route", result.status_message)
        self.assertEqual(len(result.legs), 0)

    def test_05_source_equals_destination(self):
        """Scenario 5: Origin and destination stations are identical."""
        result = self.router.find_earliest_arrival("STN_06", "STN_06", departure_time=480)

        self.assertTrue(result.found)
        self.assertEqual(result.total_journey_time_min, 0)
        self.assertEqual(result.total_travel_time_min, 0)
        self.assertEqual(result.total_waiting_time_min, 0)
        self.assertEqual(result.num_transfers, 0)
        self.assertEqual(len(result.legs), 0)
        self.assertIn("identical", result.status_message)

    def test_06_invalid_station_id(self):
        """Scenario 6: Input station ID does not exist in network."""
        with self.assertRaises(ValueError) as ctx:
            self.router.find_earliest_arrival("STN_INVALID_99", "STN_01", departure_time=400)
        self.assertIn("does not exist", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            self.router.find_earliest_arrival("STN_01", "NON_EXISTENT_DEST", departure_time=400)
        self.assertIn("does not exist", str(ctx2.exception))

    def test_07_missing_train_connection(self):
        """Scenario 7: Isolated station with no outgoing connection in a controlled subnetwork."""
        isolated_net = RailwayNetwork()
        isolated_net.add_station(Station("ISO_A", "Island A", "ISA", 10.0, 10.0, 10, False, "Test"))
        isolated_net.add_station(Station("ISO_B", "Island B", "ISB", 10.5, 10.5, 10, False, "Test"))
        isolated_net.finalize()

        isolated_router = TimeDependentEarliestArrivalDijkstra(isolated_net)
        result = isolated_router.find_earliest_arrival("ISO_A", "ISO_B", departure_time=360)

        self.assertFalse(result.found)
        self.assertIn("No feasible route", result.status_message)

    def test_08_transfer_with_insufficient_connection_time(self):
        """
        Scenario 8: Manually calculated 3-station example testing strict transfer buffer enforcement.
        Station A -> Station B -> Station C.
        Transfer buffer at Station B = 15 minutes.
        Train 1: Dep A at 600 (10:00), Arr B at 630 (10:30).
        Train 2 (INSUFFICIENT BUFFER): Dep B at 635 (10:35) -> only 5 mins buffer (< 15 min)!
        Train 3 (SUFFICIENT BUFFER): Dep B at 660 (11:00) -> 30 mins buffer (>= 15 min), Arr C at 700 (11:40).
        """
        custom_net = RailwayNetwork()
        stn_a = Station("MAN_A", "Manual A", "MNA", 0.0, 0.0, 10, False, "Test")
        stn_b = Station("MAN_B", "Manual B (Junction)", "MNB", 0.0, 1.0, 15, True, "Test")  # 15 min buffer!
        stn_c = Station("MAN_C", "Manual C", "MNC", 0.0, 2.0, 10, False, "Test")
        custom_net.add_station(stn_a)
        custom_net.add_station(stn_b)
        custom_net.add_station(stn_c)

        # Train 1: A -> B
        conn1 = Connection("C1", "SRV_1", "Service 1", "Regional", "MAN_A", "MAN_B", 600, "10:00", 630, "10:30", 30, 40.0, 1)
        # Train 2: B -> C (Departs at 635: buffer = 5 mins, INVALID)
        conn2 = Connection("C2", "SRV_2", "Service 2 (Tight)", "Regional", "MAN_B", "MAN_C", 635, "10:35", 670, "11:10", 35, 40.0, 1)
        # Train 3: B -> C (Departs at 660: buffer = 30 mins, VALID)
        conn3 = Connection("C3", "SRV_3", "Service 3 (Valid)", "Regional", "MAN_B", "MAN_C", 660, "11:00", 700, "11:40", 40, 40.0, 1)

        custom_net.add_connection(conn1)
        custom_net.add_connection(conn2)
        custom_net.add_connection(conn3)
        custom_net.finalize()

        custom_router = TimeDependentEarliestArrivalDijkstra(custom_net)
        result = custom_router.find_earliest_arrival("MAN_A", "MAN_C", departure_time=600)

        self.assertTrue(result.found)
        self.assertEqual(len(result.legs), 2)
        # Must select Train 3 (SRV_3), NOT Train 2 (SRV_2)
        self.assertEqual(result.legs[1].service_id, "SRV_3", "Must skip connection with insufficient buffer")
        self.assertEqual(result.legs[1].departure_time, 660)
        self.assertEqual(result.arrival_time, 700)
        # Manual verification of waiting time: 660 - 630 = 30 minutes
        self.assertEqual(result.total_waiting_time_min, 30)
        # Manual verification of total journey: 700 - 600 = 100 minutes
        self.assertEqual(result.total_journey_time_min, 100)
        self.assertEqual(result.num_transfers, 1)

    def test_09_journey_departing_on_next_available_service(self):
        """
        Scenario 9: Passenger requests departure after a train has already departed;
        must board the next scheduled service.
        """
        # First express train departs STN_01 at 360 (06:00). Second departs at 480 (08:00).
        # Passenger queries at 06:15 (375 min).
        result = self.router.find_earliest_arrival("STN_01", "STN_07", departure_time=375)

        self.assertTrue(result.found)
        # Actual departure must be >= 375
        self.assertGreaterEqual(result.actual_departure_time, 375)
        # In our schedule, next trunk line departure is 450 (Passenger) or 480 (Express)
        self.assertIn(result.actual_departure_time, [450, 480])
        self.assertGreater(result.arrival_time, result.actual_departure_time)


if __name__ == "__main__":
    unittest.main()
