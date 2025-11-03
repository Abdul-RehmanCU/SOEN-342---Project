import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    """
    Manages SQLite database operations for the Railway Network System.
    Handles persistence for routes, clients, trips, reservations, and tickets.
    """
    
    def __init__(self, db_path='railway_system.db'):
        self.db_path = db_path
        self._initialize_database()
    
    def _get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _initialize_database(self):
        """Create all necessary tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Routes table - stores all train connections/routes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                route_id TEXT PRIMARY KEY,
                departure_city TEXT NOT NULL,
                arrival_city TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                train_type TEXT NOT NULL,
                days_of_operation TEXT NOT NULL,
                first_class_rate REAL NOT NULL,
                second_class_rate REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clients table - stores client information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trips table - stores trip bookings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reservations table - links clients to trips and routes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                client_id TEXT NOT NULL,
                route_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
                FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE,
                UNIQUE(trip_id, client_id, route_id)
            )
        ''')
        
        # Tickets table - stores ticket information for each reservation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservation_id INTEGER NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== ROUTE OPERATIONS ==========
    
    def insert_route(self, route_data: Dict):
        """Insert a route into the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO routes 
            (route_id, departure_city, arrival_city, departure_time, arrival_time,
             train_type, days_of_operation, first_class_rate, second_class_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            route_data['route_id'],
            route_data['departure_city'],
            route_data['arrival_city'],
            route_data['departure_time'],
            route_data['arrival_time'],
            route_data['train_type'],
            route_data['days_of_operation'],
            route_data['first_class_rate'],
            route_data['second_class_rate']
        ))
        
        conn.commit()
        conn.close()
    
    def load_all_routes(self) -> List[Dict]:
        """Load all routes from the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM routes ORDER BY route_id')
        rows = cursor.fetchall()
        
        routes = [dict(row) for row in rows]
        conn.close()
        return routes
    
    def get_route_by_id(self, route_id: str) -> Optional[Dict]:
        """Get a route by its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM routes WHERE route_id = ?', (route_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def route_exists(self, route_id: str) -> bool:
        """Check if a route exists"""
        return self.get_route_by_id(route_id) is not None
    
    # ========== CLIENT OPERATIONS ==========
    
    def insert_or_update_client(self, client_data: Dict):
        """Insert or update a client in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clients (client_id, first_name, last_name, age)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(client_id) DO UPDATE SET
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                age = excluded.age,
                updated_at = CURRENT_TIMESTAMP
        ''', (
            client_data['client_id'],
            client_data['first_name'],
            client_data['last_name'],
            client_data['age']
        ))
        
        conn.commit()
        conn.close()
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get a client by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clients WHERE client_id = ?', (client_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    # ========== TRIP OPERATIONS ==========
    
    def create_trip(self, booking_date: datetime) -> int:
        """Create a new trip and return its numerical ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Convert datetime to ISO format string for SQLite
        booking_date_str = booking_date.isoformat() if isinstance(booking_date, datetime) else booking_date
        
        cursor.execute('''
            INSERT INTO trips (booking_date)
            VALUES (?)
        ''', (booking_date_str,))
        
        trip_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trip_id
    
    def get_trip(self, trip_id: int) -> Optional[Dict]:
        """Get a trip by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trips WHERE trip_id = ?', (trip_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def get_all_trips(self) -> List[Dict]:
        """Get all trips"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trips ORDER BY booking_date DESC')
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    # ========== RESERVATION OPERATIONS ==========
    
    def create_reservation(self, trip_id: int, client_id: str, route_id: str) -> int:
        """Create a reservation and return its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reservations (trip_id, client_id, route_id)
            VALUES (?, ?, ?)
        ''', (trip_id, client_id, route_id))
        
        reservation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reservation_id
    
    def get_reservations_for_trip(self, trip_id: int) -> List[Dict]:
        """Get all reservations for a trip"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.*, c.first_name, c.last_name, c.age, 
                   rt.departure_city, rt.arrival_city, rt.departure_time, 
                   rt.arrival_time, rt.train_type, rt.days_of_operation,
                   rt.first_class_rate, rt.second_class_rate
            FROM reservations r
            JOIN clients c ON r.client_id = c.client_id
            JOIN routes rt ON r.route_id = rt.route_id
            WHERE r.trip_id = ?
        ''', (trip_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_reservations_for_client(self, client_id: str, last_name: str) -> List[Dict]:
        """Get all trips for a client matching last name and client ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT t.trip_id, t.booking_date, r.route_id,
                   rt.departure_city, rt.arrival_city, rt.departure_time, 
                   rt.arrival_time, rt.train_type, rt.days_of_operation,
                   rt.first_class_rate, rt.second_class_rate
            FROM trips t
            JOIN reservations res ON t.trip_id = res.trip_id
            JOIN clients c ON res.client_id = c.client_id
            JOIN routes rt ON res.route_id = rt.route_id
            JOIN reservations r ON t.trip_id = r.trip_id
            WHERE c.client_id = ? AND LOWER(c.last_name) = LOWER(?)
            ORDER BY t.booking_date DESC
        ''', (client_id, last_name))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ========== TICKET OPERATIONS ==========
    
    def create_ticket(self, reservation_id: int) -> int:
        """Create a ticket for a reservation and return its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (reservation_id)
            VALUES (?)
        ''', (reservation_id,))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    
    def get_ticket_for_reservation(self, reservation_id: int) -> Optional[Dict]:
        """Get ticket for a reservation"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tickets WHERE reservation_id = ?', (reservation_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def get_next_trip_id(self) -> int:
        """Get the next available trip ID (for auto-increment simulation)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(trip_id) FROM trips')
        result = cursor.fetchone()[0]
        conn.close()
        
        return (result + 1) if result else 1
    
    def get_next_ticket_id(self) -> int:
        """Get the next available ticket ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(ticket_id) FROM tickets')
        result = cursor.fetchone()[0]
        conn.close()
        
        return (result + 1) if result else 100000

