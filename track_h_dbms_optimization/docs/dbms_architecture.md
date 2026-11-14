# Track H: DBMS Architecture & SQLite Internals

## 1. Executive Overview

Track H implements a production-grade Database Management System (DBMS) query optimization study using SQLite as the target engine. Database query optimization is fundamentally a multi-objective trade-off between read latency, write overhead, and secondary storage consumption. This track demonstrates how physical access path selection—specifically secondary B-tree index selection—can be formulated, solved, and validated using rigorous mathematical optimization and empirical benchmarking.

---

## 2. SQLite Engine Architecture

SQLite is a serverless, zero-configuration, transactional database engine implementing the relational model via a modular pipeline:

```mermaid
flowchart TD
    SQL["SQL Query Text"] --> Core["Parser & Code Generator"]
    Core --> Planner["Query Planner / Cost Optimizer"]
    Planner --> VDBE["Virtual Database Engine (VDBE)"]
    VDBE --> BTree["B-Tree Subsystem (B-Tree & Pager)"]
    BTree --> OS["OS Interface (VFS & Disk Files)"]
```

### 2.1 The Virtual Database Engine (VDBE)
The VDBE is a register-based virtual machine executing bytecode instructions compiled from SQL statements. When a query is parsed:
1. The SQL text is tokenized and parsed into an Abstract Syntax Tree (AST).
2. The SQLite Query Optimizer analyzes table schemas, available indexes, and catalog statistics (`sqlite_stat1` generated via `ANALYZE`).
3. The optimizer emits an execution plan encoded as VDBE opcodes (such as `OpenRead`, `SeekGE`, `IdxRowid`, `Column`, `ResultRow`).
4. The VDBE executes the bytecode against the underlying B-Tree storage pages.

### 2.2 B-Tree Storage & Page Architecture
SQLite stores all tables and secondary indexes as B-trees inside a single monolithic disk file:
- **Table B-Trees (B* Trees)**: Leaf pages contain the actual data rows (payload). The 64-bit integer rowid serves as the primary search key.
- **Index B-Trees**: Interior and leaf pages store index keys accompanied by rowids. Finding a matching record in an unclustered index requires an initial B-tree traversal to locate the rowid, followed by a secondary seek on the table B-tree to retrieve unindexed payload columns.
- **Covering Indexes**: When all columns requested by a `SELECT` clause, `WHERE` predicate, and `ORDER BY` clause reside within the index itself, SQLite executes an index-only scan, completely bypassing table page lookups.

---

## 3. Relational Schema Design: Railway Reservation System

To evaluate real-world query optimization, Track H models a high-concurrency National Railway Reservation and Ticketing System across 7 normalized relational tables:

```mermaid
erDiagram
    STATIONS ||--o{ SCHEDULES : hosts
    TRAINS ||--o{ SCHEDULES : runs
    TRAINS ||--o{ BOOKINGS : reserves
    PASSENGERS ||--o{ TICKETS : holds
    BOOKINGS ||--o{ TICKETS : contains
    BOOKINGS ||--|| PAYMENTS : settles

    STATIONS {
        int station_id PK
        string station_code
        string station_name
        string division
        int platform_count
    }
    TRAINS {
        int train_id PK
        string train_number
        string train_name
        string train_type
        int total_coaches
    }
    SCHEDULES {
        int schedule_id PK
        int train_id FK
        int station_id FK
        int stop_number
        int arrival_time_min
        int departure_time_min
        real distance_km
    }
    PASSENGERS {
        int passenger_id PK
        string first_name
        string last_name
        string frequent_flyer_tier
        int age
        string gender
    }
    BOOKINGS {
        int booking_id PK
        string pnr_number
        int train_id FK
        string journey_date
        string booking_status
        real base_fare
    }
    TICKETS {
        int ticket_id PK
        int booking_id FK
        int passenger_id FK
        string coach_number
        int seat_number
        string travel_class
        string ticket_status
    }
    PAYMENTS {
        int payment_id PK
        int booking_id FK
        string payment_method
        real amount_paid
        string payment_status
        string transaction_timestamp
    }
```

### 3.1 Scale & Footprint
Under deterministic generation (seed 42, scale factor 0.60):
- **Stations**: 60 major junctions and terminals.
- **Trains**: 300 express and superfast services.
- **Schedules**: 5,348 arrival/departure checkpoints.
- **Passengers**: 15,000 registered accounts.
- **Bookings**: 36,000 reservation transactions.
- **Tickets**: 89,893 issued passenger tickets.
- **Payments**: 36,000 financial settlements.
- **Total Rows**: 179,760 records.
- **Physical SQLite Database Size**: 9.46 MB.

---

## 4. Query Planner & Execution Plan Inspection

SQLite inspects candidate execution paths using a cost-based model. We interrogate the planner using `EXPLAIN QUERY PLAN <sql>`:

### 4.1 Plan Operators
- **`SCAN <table>`**: Full table scan traversing every database page in the table B-tree ($O(N)$ page reads). In the absence of indexes, filtering on non-key attributes requires scanning all 36,000 booking rows or 89,893 ticket rows.
- **`SEARCH <table> USING INDEX <index_name>`**: Logarithmic traversal down an index B-tree ($O(\log M)$ page reads) followed by point lookups.
- **`SEARCH <table> USING COVERING INDEX <index_name>`**: Zero table page reads; all requested columns are satisfied directly from index leaf pages.
- **`USE TEMP B-TREE FOR ORDER BY / GROUP BY`**: When no index exists with matching sort order, SQLite builds an in-memory or spill-to-disk temporary B-tree to sort intermediate result sets ($O(K \log K)$ sorting cost).

### 4.2 SQLite Catalog Statistics (`ANALYZE`)
To enable realistic index cost modeling, our benchmark runner executes `ANALYZE;` immediately following index creation. This populates `sqlite_stat1`, providing the planner with exact distribution histograms and average row estimates for index prefixes.

