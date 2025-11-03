# Data Model Documentation
## European Railway Network System - Database Schema

This document describes the relational database schema used for persistence in the Railway Network System.

### Database: SQLite (`railway_system.db`)

---

## Tables

### 1. `routes` Table
Stores all train routes/connections available in the system.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `route_id` | TEXT | PRIMARY KEY | Unique identifier for the route |
| `departure_city` | TEXT | NOT NULL | City where the train departs |
| `arrival_city` | TEXT | NOT NULL | City where the train arrives |
| `departure_time` | TEXT | NOT NULL | Departure time (format: HH:MM or HH:MM (+Nd)) |
| `arrival_time` | TEXT | NOT NULL | Arrival time (format: HH:MM or HH:MM (+Nd)) |
| `train_type` | TEXT | NOT NULL | Type of train (e.g., TGV, ICE, EuroCity) |
| `days_of_operation` | TEXT | NOT NULL | Days when route operates (e.g., Daily, Mon-Fri) |
| `first_class_rate` | REAL | NOT NULL | First class ticket price in euros |
| `second_class_rate` | REAL | NOT NULL | Second class ticket price in euros |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when route was added |

**Keys:**
- **Primary Key:** `route_id`

**Indexes:**
- None (route_id is unique by primary key constraint)

---

### 2. `clients` Table
Stores client/traveller information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `client_id` | TEXT | PRIMARY KEY | Unique identifier (passport, state ID, etc.) |
| `first_name` | TEXT | NOT NULL | Client's first name |
| `last_name` | TEXT | NOT NULL | Client's last name |
| `age` | INTEGER | NOT NULL | Client's age |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when client was first registered |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when client info was last updated |

**Keys:**
- **Primary Key:** `client_id`

**Indexes:**
- None (client_id is unique by primary key constraint)

---

### 3. `trips` Table
Stores trip bookings. Each trip can contain multiple reservations.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `trip_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique numerical trip identifier |
| `booking_date` | TIMESTAMP | NOT NULL | Date and time when trip was booked |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when trip record was created |

**Keys:**
- **Primary Key:** `trip_id` (auto-incrementing integer)

**Indexes:**
- None

**Relationships:**
- One-to-Many with `reservations` table (one trip can have many reservations)

---

### 4. `reservations` Table
Links clients to trips and routes. Each reservation represents one passenger booking on a specific route.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `reservation_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the reservation |
| `trip_id` | INTEGER | NOT NULL, FOREIGN KEY | References `trips.trip_id` |
| `client_id` | TEXT | NOT NULL, FOREIGN KEY | References `clients.client_id` |
| `route_id` | TEXT | NOT NULL, FOREIGN KEY | References `routes.route_id` |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when reservation was created |

**Keys:**
- **Primary Key:** `reservation_id`
- **Foreign Keys:**
  - `trip_id` → `trips.trip_id` (ON DELETE CASCADE)
  - `client_id` → `clients.client_id` (ON DELETE CASCADE)
  - `route_id` → `routes.route_id` (ON DELETE CASCADE)
- **Unique Constraint:** `(trip_id, client_id, route_id)` - Ensures a client cannot have duplicate reservations for the same route in the same trip

**Indexes:**
- Implicit indexes on foreign key columns

**Relationships:**
- Many-to-One with `trips` table
- Many-to-One with `clients` table
- Many-to-One with `routes` table
- One-to-One with `tickets` table

---

### 5. `tickets` Table
Stores ticket information for each reservation.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `ticket_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique numerical ticket identifier |
| `reservation_id` | INTEGER | NOT NULL, UNIQUE, FOREIGN KEY | References `reservations.reservation_id` |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when ticket was issued |

**Keys:**
- **Primary Key:** `ticket_id`
- **Foreign Key:** `reservation_id` → `reservations.reservation_id` (ON DELETE CASCADE)
- **Unique Constraint:** `reservation_id` - Each reservation has exactly one ticket

**Indexes:**
- Implicit index on `reservation_id` (unique constraint)

**Relationships:**
- One-to-One with `reservations` table

---

## Entity-Relationship Overview

```
routes (1) ──< (many) reservations (many) ──< (1) trips
                     │
                     │ (many)
                     │
                     ▼
              (1) clients
                     │
                     │ (1)
                     │
                     ▼
              (1) tickets
```

## Data Flow

1. **Route Loading:** Routes are loaded from CSV file and stored in `routes` table
2. **Trip Booking:** 
   - Client info stored/updated in `clients` table
   - New `trip` record created with numerical ID
   - `reservation` records created linking client, trip, and route
   - `ticket` records created for each reservation
3. **Trip Viewing:** 
   - Queries join `trips`, `reservations`, `clients`, and `routes` tables
   - Filters by client_id and last_name to find all trips for a client
   - Separates current/future trips from past trips based on departure time

## Notes

- All timestamps use SQLite's TIMESTAMP type (stored as TEXT in ISO8601 format)
- Cascade deletes ensure referential integrity (deleting a trip removes all associated reservations and tickets)
- The `trip_id` is auto-incrementing, ensuring unique numerical IDs as required
- The `ticket_id` starts at 100000 and auto-increments

