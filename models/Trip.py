import string
import random
from datetime import datetime
from .Reservation import Reservation

class Trip:
    
    def __init__(self, reservations=None):
        self.trip_id = self._generate_trip_id()
        self.reservations = reservations or []
        self.booking_date = datetime.now()
        
    def _generate_trip_id(self):
        "Generates a unique alphanumeric trip ID (e.g., TR8K3M9L)"
        letters = string.ascii_uppercase
        digits = string.digits
        # Generate 8-character ID starting with TR
        id_chars = 'TR' + ''.join(random.choices(letters + digits, k=6))
        return id_chars
    
    def add_reservation(self, reservation):
        "Adds a reservation to this trip"
        self.reservations.append(reservation)
    
    def get_connection(self):
        "Returns the connection for this trip (assumes all reservations are for the same connection)"
        if self.reservations:
            return self.reservations[0].connection
        return None
    
    def get_total_passengers(self):
        "Returns the number of passengers on this trip"
        return len(self.reservations)
    
    def get_passenger_names(self):
        "Returns a list of all passenger names on this trip"
        return [reservation.client.get_full_name() for reservation in self.reservations]
    
    def is_current_or_future(self):
        "Checks if this trip is for today or a future date"
        connection = self.get_connection()
        if not connection:
            return False
        
        # For simplicity, we'll consider all trips as current/future for now
        # In a real system, you'd parse the departure date and compare with today
        return True
    
    def get_trip_summary(self):
        "Returns a summary of the trip information"
        connection = self.get_connection()
        if not connection:
            return {}
        
        return {
            'trip_id': self.trip_id,
            'booking_date': self.booking_date.strftime('%Y-%m-%d %H:%M'),
            'route': f"{connection.departure_city} → {connection.arrival_city}",
            'departure_time': connection.departure_time,
            'arrival_time': connection.arrival_time,
            'train_type': connection.train_type,
            'duration': connection.calculate_duration(),
            'passengers': self.get_passenger_names(),
            'passenger_count': self.get_total_passengers(),
            'reservations': self.reservations
        }
    
    def __str__(self):
        connection = self.get_connection()
        if connection:
            route = f"{connection.departure_city} → {connection.arrival_city}"
        else:
            route = "No connection"
        return f"Trip {self.trip_id}: {route} ({self.get_total_passengers()} passengers)"