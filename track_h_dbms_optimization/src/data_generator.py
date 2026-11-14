"""
Deterministic synthetic data generator for Railway Reservation DBMS.
Uses fixed random seed (42) to guarantee reproducible benchmark databases.
"""

import sqlite3
import random
import datetime

def populate_database(conn, seed=42, scale_factor=1.0):
    """
    Populate database with realistic railway reservation data.
    scale_factor allows scaling the dataset up or down.
    """
    rng = random.Random(seed)
    cursor = conn.cursor()

    # Optimization pragmas for fast bulk load
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")

    # 1. Stations (~100 stations)
    num_stations = int(100 * scale_factor)
    zones = ["NR", "CR", "WR", "SR", "ER", "NCR", "WCR", "SWR", "ECR", "SCR"]
    cities = [
        "New Delhi", "Mumbai", "Kolkata", "Chennai", "Bengaluru", "Hyderabad",
        "Ahmedabad", "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore",
        "Bhopal", "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik",
        "Varanasi", "Surat", "Amritsar", "Allahabad", "Ranchi", "Coimbatore",
        "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur",
        "Kota", "Guwahati", "Chandigarh", "Solapur", "Bareilly", "Moradabad",
        "Mysuru", "Gurgaon", "Aligarh", "Jalandhar", "Bhubaneswar", "Salem",
        "Warangal", "Thiruvananthapuram", "Bhiwandi", "Saharanpur", "Gorakhpur", "Bikaner"
    ]
    station_rows = []
    for i in range(1, num_stations + 1):
        code = f"STN{i:03d}" if i > len(cities) else f"{cities[i-1][:3].upper()}{i:02d}"
        city_name = cities[(i - 1) % len(cities)]
        name = f"{city_name} Junction" if i % 3 == 0 else f"{city_name} Central"
        zone = zones[i % len(zones)]
        platforms = rng.randint(4, 16)
        station_rows.append((i, code, name, zone, platforms))

    cursor.executemany(
        "INSERT INTO stations (station_id, station_code, station_name, zone, platform_count) VALUES (?, ?, ?, ?, ?);",
        station_rows
    )

    # 2. Trains (~500 trains)
    num_trains = int(500 * scale_factor)
    train_types = ["Rajdhani", "Shatabdi", "Superfast", "Express", "Duronto", "JanShatabdi"]
    train_rows = []
    for t_id in range(1, num_trains + 1):
        t_num = 12000 + t_id
        t_type = rng.choice(train_types)
        orig = rng.randint(1, num_stations)
        dest = rng.randint(1, num_stations)
        while dest == orig:
            dest = rng.randint(1, num_stations)
        t_name = f"{t_type} Express {t_num}"
        coaches = rng.choice([16, 18, 20, 22, 24])
        train_rows.append((t_id, t_num, t_name, t_type, orig, dest, coaches))

    cursor.executemany(
        "INSERT INTO trains (train_id, train_number, train_name, train_type, origin_station_id, dest_station_id, total_coaches) VALUES (?, ?, ?, ?, ?, ?, ?);",
        train_rows
    )

    # 3. Schedules (~12,500 stops, ~25 stops per train)
    schedule_rows = []
    sched_id = 1
    max_possible_stops = min(30, num_stations)
    min_possible_stops = min(5, max_possible_stops)
    for t_id in range(1, num_trains + 1):
        stops_count = rng.randint(min_possible_stops, max_possible_stops)
        selected_stations = rng.sample(range(1, num_stations + 1), stops_count)
        current_time = rng.randint(240, 480) # Start between 04:00 and 08:00
        cum_dist = 0.0

        for stop_num in range(1, stops_count + 1):
            stn = selected_stations[stop_num - 1]
            arr = current_time
            dept = arr + rng.randint(3, 15) if stop_num < stops_count else arr
            dist_leg = rng.uniform(40.0, 110.0) if stop_num > 1 else 0.0
            cum_dist += dist_leg

            schedule_rows.append((sched_id, t_id, stn, stop_num, arr % 1440, dept % 1440, round(cum_dist, 1)))
            sched_id += 1
            current_time = dept + rng.randint(30, 90)

    cursor.executemany(
        "INSERT INTO schedules (schedule_id, train_id, station_id, stop_number, arrival_time, departure_time, distance_km) VALUES (?, ?, ?, ?, ?, ?, ?);",
        schedule_rows
    )

    # 4. Passengers (~25,000 passengers)
    num_passengers = int(25000 * scale_factor)
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
                   "Diya", "Saanvi", "Aanya", "Aadhya", "Pari", "Ananya", "Myra", "Riya", "Isha", "Kavya",
                   "Rohan", "Rahul", "Pooja", "Neha", "Amit", "Priya", "Vikram", "Sneha", "Anil", "Sunita"]
    last_names = ["Sharma", "Verma", "Patel", "Mehta", "Chopra", "Gupta", "Singh", "Kumar", "Iyer", "Rao",
                  "Joshi", "Deshmukh", "Nair", "Kulkarni", "Reddy", "Chavan", "Pillai", "Das", "Bose", "Banerjee"]
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    tier_weights = [0.50, 0.30, 0.15, 0.05]

    passenger_rows = []
    for p_id in range(1, num_passengers + 1):
        fn = rng.choice(first_names)
        ln = rng.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{p_id}@example.com"
        phone = f"98{rng.randint(10000000, 99999999)}"
        gender = rng.choice(["M", "F"])
        age = rng.randint(18, 75)
        tier = rng.choices(tiers, weights=tier_weights)[0]
        passenger_rows.append((p_id, fn, ln, email, phone, gender, age, tier))

    cursor.executemany(
        "INSERT INTO passengers (passenger_id, first_name, last_name, email, phone, gender, age, loyalty_tier) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        passenger_rows
    )

    # 5. Bookings (~60,000 bookings)
    num_bookings = int(60000 * scale_factor)
    base_date = datetime.date(2026, 6, 1)
    status_choices = ["CONFIRMED", "WAITLIST", "CANCELLED"]
    status_weights = [0.75, 0.15, 0.10]

    booking_rows = []
    ticket_rows = []
    payment_rows = []
    t_ticket_id = 1

    payment_methods = ["UPI", "CREDIT_CARD", "NET_BANKING", "WALLET"]
    classes = ["1A", "2A", "3A", "SL"]
    class_fares = {"1A": 2400.0, "2A": 1500.0, "3A": 1050.0, "SL": 420.0}

    for b_id in range(1, num_bookings + 1):
        pnr = f"PNR-{2026}-{b_id:06d}"
        pass_id = rng.randint(1, num_passengers)
        tr_id = rng.randint(1, num_trains)
        j_offset = rng.randint(0, 90) # Travel within 90 days of June 1, 2026
        j_date = (base_date + datetime.timedelta(days=j_offset)).strftime("%Y-%m-%d")
        status = rng.choices(status_choices, weights=status_weights)[0]
        booking_ts = 1775000000 + rng.randint(0, 5000000)

        # Generate 1 to 4 tickets per booking
        num_tix = rng.randint(1, 4)
        c_class = rng.choice(classes)
        base_fare = class_fares[c_class]
        total_fare = 0.0

        for s_idx in range(num_tix):
            seat = f"{c_class[:2]}-{rng.randint(1, 72)}"
            t_name = f"Passenger {t_ticket_id}"
            t_age = rng.randint(5, 75)
            fare = base_fare * (0.5 if t_age < 12 else 1.0)
            total_fare += fare
            ticket_rows.append((t_ticket_id, b_id, seat, c_class, t_name, t_age, round(fare, 2)))
            t_ticket_id += 1

        booking_rows.append((b_id, pnr, pass_id, tr_id, j_date, status, booking_ts, round(total_fare, 2)))

        # Payments: 1 payment per booking
        p_status = "SUCCESS" if status == "CONFIRMED" else ("REFUNDED" if status == "CANCELLED" else "PENDING")
        p_method = rng.choice(payment_methods)
        payment_rows.append((b_id, b_id, p_method, p_status, round(total_fare, 2), booking_ts + 60))

    cursor.executemany(
        "INSERT INTO bookings (booking_id, pnr_number, passenger_id, train_id, journey_date, booking_status, booking_timestamp, total_fare) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        booking_rows
    )

    cursor.executemany(
        "INSERT INTO tickets (ticket_id, booking_id, seat_number, coach_class, passenger_name, passenger_age, fare) VALUES (?, ?, ?, ?, ?, ?, ?);",
        ticket_rows
    )

    cursor.executemany(
        "INSERT INTO payments (payment_id, booking_id, payment_method, payment_status, amount, transaction_time) VALUES (?, ?, ?, ?, ?, ?);",
        payment_rows
    )

    conn.commit()

    # Re-enable normal pragma defaults
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA journal_mode = DELETE;")
    cursor.execute("ANALYZE;") # Populate sqlite_stat1 for query planner cost models
    conn.commit()

    return {
        "stations": num_stations,
        "trains": num_trains,
        "schedules": len(schedule_rows),
        "passengers": num_passengers,
        "bookings": num_bookings,
        "tickets": len(ticket_rows),
        "payments": len(payment_rows)
    }
