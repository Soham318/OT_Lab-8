"""
Database schema definition for Railway Reservation DBMS.
Defines tables, relationships, primary keys, and foreign keys for SQLite.
"""

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- Stations across railway network
CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_code TEXT NOT NULL UNIQUE,
    station_name TEXT NOT NULL,
    zone TEXT NOT NULL,
    platform_count INTEGER NOT NULL
);

-- Train services
CREATE TABLE IF NOT EXISTS trains (
    train_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_number INTEGER NOT NULL UNIQUE,
    train_name TEXT NOT NULL,
    train_type TEXT NOT NULL,
    origin_station_id INTEGER NOT NULL,
    dest_station_id INTEGER NOT NULL,
    total_coaches INTEGER NOT NULL,
    FOREIGN KEY (origin_station_id) REFERENCES stations(station_id),
    FOREIGN KEY (dest_station_id) REFERENCES stations(station_id)
);

-- Timetable stop schedules
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    stop_number INTEGER NOT NULL,
    arrival_time INTEGER NOT NULL,     -- Minutes from midnight (0-1439)
    departure_time INTEGER NOT NULL,   -- Minutes from midnight (0-1439)
    distance_km REAL NOT NULL,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- Registered passengers
CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    gender TEXT NOT NULL,
    age INTEGER NOT NULL,
    loyalty_tier TEXT NOT NULL         -- Bronze, Silver, Gold, Platinum
);

-- PNR Bookings
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pnr_number TEXT NOT NULL UNIQUE,
    passenger_id INTEGER NOT NULL,
    train_id INTEGER NOT NULL,
    journey_date TEXT NOT NULL,        -- YYYY-MM-DD
    booking_status TEXT NOT NULL,      -- CONFIRMED, WAITLIST, CANCELLED
    booking_timestamp INTEGER NOT NULL,-- Unix epoch seconds
    total_fare REAL NOT NULL,
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (train_id) REFERENCES trains(train_id)
);

-- Individual passenger tickets per booking
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    seat_number TEXT NOT NULL,
    coach_class TEXT NOT NULL,         -- 1A, 2A, 3A, SL
    passenger_name TEXT NOT NULL,
    passenger_age INTEGER NOT NULL,
    fare REAL NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- Payment transactions for bookings
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    payment_method TEXT NOT NULL,      -- UPI, CREDIT_CARD, NET_BANKING, WALLET
    payment_status TEXT NOT NULL,      -- SUCCESS, FAILED, PENDING, REFUNDED
    amount REAL NOT NULL,
    transaction_time INTEGER NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);
"""

def create_schema(conn):
    """Execute DDL statements to create database schema."""
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()

