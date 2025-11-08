import string
import random
from datetime import datetime, timedelta
from .Reservation import Reservation

class Trip:
    
    def __init__(self, trip_id=None, reservations=None, booking_date=None):
        """
        Initialize a Trip.
        
        Args:
            trip_id: Numerical trip ID (should be provided from database)
            reservations: List of Reservation objects
            booking_date: datetime object for booking date
        """
        self.trip_id = trip_id  # Numerical ID (will be set by database)
        self.reservations = reservations or []
        self.booking_date = booking_date if booking_date else datetime.now()
    
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
        """
        Checks if this trip is for today or a future date.
        Compares the connection's departure time with today's date.
        """
        connection = self.get_connection()
        if not connection:
            return False
        
        # Get today's date at midnight
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Parse departure time to get a datetime for comparison
        # For simplicity, we'll use the booking date's day and parse the time
        try:
            import re
            
            # Extract time from departure_time string
            time_str = connection.departure_time
            extra_days = 0
            match = re.search(r"\(\+(\d+)d\)", time_str)
            if match:
                extra_days = int(match.group(1))
                time_str = re.sub(r"\s*\(\+\d+d\)", "", time_str).strip()
            
            # Parse time
            time_part = datetime.strptime(time_str, "%H:%M").time()
            
            # Use booking date as reference for the departure date
            # Assume trip is on the booking date (or next day if booking is late)
            departure_date = self.booking_date.replace(
                hour=time_part.hour,
                minute=time_part.minute,
                second=0,
                microsecond=0
            )
            
            # Add extra days if specified
            if extra_days > 0:
                departure_date += timedelta(days=extra_days)
            
            # If departure time has passed today, it's in the past
            # Otherwise it's current or future
            return departure_date >= today
            
        except Exception:
            # If parsing fails, assume it's current/future
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