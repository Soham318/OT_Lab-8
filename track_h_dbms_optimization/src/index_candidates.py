"""
Candidate Index definitions and cost/benefit models for Railway Reservation DBMS.
Defines 12 candidate single-column and composite secondary indexes.
"""

CANDIDATE_INDEXES = [
    {
        "id": "IDX_01",
        "name": "idx_bookings_status_date",
        "table": "bookings",
        "columns": ["booking_status", "journey_date"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_bookings_status_date ON bookings(booking_status, journey_date);",
        "storage_cost_mb": 2.4, # ~60,000 rows * (12 bytes status + 10 bytes date + 8 bytes rowid)
        "applicable_queries": ["Q1", "Q7"],
        "base_benefits_ms": {"Q1": 120.0, "Q7": 140.0},
        "description": "Composite index covering booking_status filter and journey_date range."
    },
    {
        "id": "IDX_02",
        "name": "idx_bookings_journey_date",
        "table": "bookings",
        "columns": ["journey_date"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_bookings_journey_date ON bookings(journey_date);",
        "storage_cost_mb": 1.5,
        "applicable_queries": ["Q1", "Q2", "Q7"],
        "base_benefits_ms": {"Q1": 85.0, "Q2": 95.0, "Q7": 90.0},
        "description": "Single-column index on journey_date for date-range scanning."
    },
    {
        "id": "IDX_03",
        "name": "idx_bookings_passenger_id",
        "table": "bookings",
        "columns": ["passenger_id"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_bookings_passenger_id ON bookings(passenger_id);",
        "storage_cost_mb": 1.2,
        "applicable_queries": ["Q2", "Q6", "Q8"],
        "base_benefits_ms": {"Q2": 60.0, "Q6": 80.0, "Q8": 40.0},
        "description": "Foreign key index on bookings.passenger_id accelerating joins with passengers."
    },
    {
        "id": "IDX_04",
        "name": "idx_bookings_train_id",
        "table": "bookings",
        "columns": ["train_id"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_bookings_train_id ON bookings(train_id);",
        "storage_cost_mb": 1.2,
        "applicable_queries": ["Q3"],
        "base_benefits_ms": {"Q3": 110.0},
        "description": "Foreign key index on bookings.train_id accelerating train revenue aggregation join."
    },
    {
        "id": "IDX_05",
        "name": "idx_tickets_booking_id",
        "table": "tickets",
        "columns": ["booking_id"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_tickets_booking_id ON tickets(booking_id);",
        "storage_cost_mb": 2.8, # ~120,000 rows
        "applicable_queries": ["Q2", "Q6", "Q7"],
        "base_benefits_ms": {"Q2": 150.0, "Q6": 130.0, "Q7": 160.0},
        "description": "Critical foreign key index on tickets.booking_id for passenger and manifest joins."
    },
    {
        "id": "IDX_06",
        "name": "idx_tickets_class",
        "table": "tickets",
        "columns": ["coach_class"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_tickets_class ON tickets(coach_class);",
        "storage_cost_mb": 1.8,
        "applicable_queries": ["Q6", "Q7"],
        "base_benefits_ms": {"Q6": 45.0, "Q7": 35.0},
        "description": "Filter index on tickets.coach_class."
    },
    {
        "id": "IDX_07",
        "name": "idx_payments_booking_id",
        "table": "payments",
        "columns": ["booking_id"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON payments(booking_id);",
        "storage_cost_mb": 1.4,
        "applicable_queries": ["Q5", "Q8"],
        "base_benefits_ms": {"Q5": 85.0, "Q8": 50.0},
        "description": "Foreign key index on payments.booking_id accelerating payment receipt joins."
    },
    {
        "id": "IDX_08",
        "name": "idx_payments_status_method",
        "table": "payments",
        "columns": ["payment_status", "payment_method"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_payments_status_method ON payments(payment_status, payment_method);",
        "storage_cost_mb": 1.7,
        "applicable_queries": ["Q5"],
        "base_benefits_ms": {"Q5": 65.0},
        "description": "Composite index covering payment_status filter and payment_method grouping."
    },
    {
        "id": "IDX_09",
        "name": "idx_schedules_station_dept",
        "table": "schedules",
        "columns": ["station_id", "departure_time"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_schedules_station_dept ON schedules(station_id, departure_time);",
        "storage_cost_mb": 0.8, # ~12,500 rows
        "applicable_queries": ["Q4"],
        "base_benefits_ms": {"Q4": 95.0},
        "description": "Composite index covering station filtering and ordered departure time range."
    },
    {
        "id": "IDX_10",
        "name": "idx_passengers_tier",
        "table": "passengers",
        "columns": ["loyalty_tier"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_passengers_tier ON passengers(loyalty_tier);",
        "storage_cost_mb": 0.6,
        "applicable_queries": ["Q6"],
        "base_benefits_ms": {"Q6": 55.0},
        "description": "Filter index on passengers.loyalty_tier for premium passenger subqueries."
    },
    {
        "id": "IDX_11",
        "name": "idx_bookings_fare",
        "table": "bookings",
        "columns": ["total_fare"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_bookings_fare ON bookings(total_fare);",
        "storage_cost_mb": 1.2,
        "applicable_queries": ["Q5"],
        "base_benefits_ms": {"Q5": 40.0},
        "description": "Range index on bookings.total_fare."
    },
    {
        "id": "IDX_12",
        "name": "idx_schedules_train_id",
        "table": "schedules",
        "columns": ["train_id"],
        "sql": "CREATE INDEX IF NOT EXISTS idx_schedules_train_id ON schedules(train_id);",
        "storage_cost_mb": 0.7,
        "applicable_queries": [], # Low workload benefit
        "base_benefits_ms": {},
        "description": "Schedule train lookup index (low utility for current workload)."
    }
]

def get_candidate_indexes():
    """Return all 12 candidate indexes."""
    return CANDIDATE_INDEXES

