"""
Workload specification for Railway Reservation DBMS.
Contains 8 representative analytical and transactional queries covering:
- Filtering on single and composite columns
- Multi-table joins (inner and outer)
- Group by aggregations
- Range predicates and sorting
- Subqueries
- Transactional point lookups
"""

WORKLOAD_QUERIES = [
    {
        "id": "Q1",
        "name": "Active Confirmed Bookings in Date Range",
        "type": "range_filter",
        "weight": 25, # High frequency transactional query
        "description": "Filters confirmed bookings in a two-week travel window.",
        "sql": """
            SELECT booking_id, pnr_number, journey_date, total_fare
            FROM bookings
            WHERE booking_status = 'CONFIRMED'
              AND journey_date BETWEEN '2026-06-15' AND '2026-06-30'
            ORDER BY journey_date ASC;
        """
    },
    {
        "id": "Q2",
        "name": "Passenger Manifest for Date",
        "type": "join_filter",
        "weight": 20,
        "description": "Joins bookings, passengers, and tickets for travel date manifest.",
        "sql": """
            SELECT b.pnr_number, p.first_name, p.last_name, t.seat_number, t.coach_class, t.fare
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN tickets t ON b.booking_id = t.booking_id
            WHERE b.journey_date = '2026-07-04'
              AND b.booking_status = 'CONFIRMED'
            ORDER BY b.pnr_number, t.seat_number;
        """
    },
    {
        "id": "Q3",
        "name": "Train Revenue & Booking Aggregation",
        "type": "aggregation_group",
        "weight": 10,
        "description": "Aggregates revenue, ticket count, and average fare grouped by train.",
        "sql": """
            SELECT tr.train_number, tr.train_name,
                   COUNT(b.booking_id) AS total_bookings,
                   SUM(b.total_fare) AS total_revenue,
                   AVG(b.total_fare) AS avg_fare
            FROM trains tr
            JOIN bookings b ON tr.train_id = b.train_id
            WHERE b.booking_status = 'CONFIRMED'
            GROUP BY tr.train_id, tr.train_number, tr.train_name
            ORDER BY total_revenue DESC
            LIMIT 20;
        """
    },
    {
        "id": "Q4",
        "name": "Station Morning Departures",
        "type": "range_sort",
        "weight": 15,
        "description": "Finds all departures from station 42 between 06:00 and 12:00 ordered by departure time.",
        "sql": """
            SELECT s.station_id, s.train_id, s.departure_time, s.stop_number, s.distance_km
            FROM schedules s
            WHERE s.station_id = 42
              AND s.departure_time BETWEEN 360 AND 720
            ORDER BY s.departure_time ASC;
        """
    },
    {
        "id": "Q5",
        "name": "Payment Method Summary for High-Fare Bookings",
        "type": "join_multi_predicate",
        "weight": 10,
        "description": "Aggregates successful payments grouped by payment method for high-fare bookings.",
        "sql": """
            SELECT pay.payment_method,
                   COUNT(pay.payment_id) AS tx_count,
                   SUM(pay.amount) AS total_amount,
                   AVG(pay.amount) AS avg_amount
            FROM payments pay
            JOIN bookings b ON pay.booking_id = b.booking_id
            WHERE pay.payment_status = 'SUCCESS'
              AND b.total_fare >= 2000.0
            GROUP BY pay.payment_method
            ORDER BY total_amount DESC;
        """
    },
    {
        "id": "Q6",
        "name": "Premium Tier Passenger Bookings",
        "type": "subquery",
        "weight": 8,
        "description": "Finds high-class (1A, 2A) tickets booked by Platinum loyalty tier passengers.",
        "sql": """
            SELECT t.ticket_id, t.seat_number, t.coach_class, t.fare, b.journey_date
            FROM tickets t
            JOIN bookings b ON t.booking_id = b.booking_id
            WHERE t.coach_class IN ('1A', '2A')
              AND b.passenger_id IN (
                  SELECT passenger_id FROM passengers WHERE loyalty_tier = 'Platinum'
              )
            ORDER BY t.fare DESC
            LIMIT 50;
        """
    },
    {
        "id": "Q7",
        "name": "Monthly Class Demographics & Occupancy",
        "type": "analytical_group",
        "weight": 7,
        "description": "Complex analytical join reporting ticket count, average passenger age, and revenue by class.",
        "sql": """
            SELECT b.journey_date, t.coach_class,
                   COUNT(t.ticket_id) AS ticket_count,
                   AVG(t.passenger_age) AS avg_age,
                   SUM(t.fare) AS total_class_fare
            FROM bookings b
            JOIN tickets t ON b.booking_id = t.booking_id
            WHERE b.journey_date BETWEEN '2026-06-01' AND '2026-06-30'
              AND b.booking_status = 'CONFIRMED'
            GROUP BY b.journey_date, t.coach_class
            ORDER BY b.journey_date ASC, total_class_fare DESC;
        """
    },
    {
        "id": "Q8",
        "name": "Transactional PNR Itinerary & Payment Lookup",
        "type": "point_lookup",
        "weight": 30, # Very high transactional frequency
        "description": "Point-lookup verifying passenger itinerary and payment receipt for a specific PNR.",
        "sql": """
            SELECT b.pnr_number, b.booking_status, b.journey_date, b.total_fare,
                   p.first_name || ' ' || p.last_name AS booker_name,
                   pay.payment_method, pay.payment_status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            LEFT JOIN payments pay ON b.booking_id = pay.booking_id
            WHERE b.pnr_number = 'PNR-2026-004281';
        """
    }
]

def get_workload_queries():
    """Return all 8 workload queries."""
    return WORKLOAD_QUERIES
