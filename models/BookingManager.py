from .Client import Client
from .Reservation import Reservation
from .Trip import Trip
from .Ticket import Ticket
from .TrainConnection import TrainConnection
from datetime import datetime
from .DatabaseManager import DatabaseManager

class BookingManager:
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize BookingManager with database persistence.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db_manager = db_manager or DatabaseManager()
        # In-memory cache for active objects (for current session)
        self.clients = {}  # client_id -> Client object
        self.trips = {}    # trip_id -> Trip object
    
    def get_or_create_client(self, first_name, last_name, age, client_id):
        """Gets existing client or creates a new one (in memory and database)"""
        if client_id in self.clients:
            # Update client info if it exists
            client = self.clients[client_id]
            client.first_name = first_name
            client.last_name = last_name
            client.age = age
        else:
            # Create new client
            client = Client(first_name, last_name, age, client_id)
            self.clients[client_id] = client
        
        # Persist to database
        client_data = {
            'client_id': client_id,
            'first_name': first_name,
            'last_name': last_name,
            'age': age
        }
        self.db_manager.insert_or_update_client(client_data)
        
        return client
    
    def book_trip(self, travellers, connection):
        """
        Books a trip for one or more travellers on a given connection.
        Persists everything to database and returns Trip with numerical ID.
        
        Args:
            travellers: List of dicts with keys: 'first_name', 'last_name', 'age', 'client_id'
            connection: TrainConnection object
            
        Returns:
            Trip object with all reservations (with numerical trip_id from database)
        """
        if not travellers:
            raise ValueError("At least one traveller is required")
        
        # Validate that each client can only have one reservation per connection
        for traveller_info in travellers:
            client_id = traveller_info['client_id']
            if self._has_existing_reservation(client_id, connection):
                raise ValueError(f"Client {client_id} already has a reservation for this connection")
        
        # Create trip in database first to get numerical ID
        booking_date = datetime.now()
        trip_id = self.db_manager.create_trip(booking_date)
        
        # Create or get clients and make reservations
        reservations = []
        for traveller_info in travellers:
            client = self.get_or_create_client(
                traveller_info['first_name'],
                traveller_info['last_name'],
                traveller_info['age'],
                traveller_info['client_id']
            )
            
            # Create reservation in database
            reservation_id = self.db_manager.create_reservation(
                trip_id, client.client_id, connection.route_id
            )
            
            # Create ticket in database first
            ticket_id = self.db_manager.create_ticket(reservation_id)
            
            # Create reservation object (for in-memory use)
            reservation = Reservation(client, connection, reservation_id)
            
            # Create ticket object and link it
            ticket = Ticket(reservation, ticket_id)
            reservation.ticket = ticket
            
            reservations.append(reservation)
        
        # Create trip object with numerical ID from database
        trip = Trip(trip_id=trip_id, reservations=reservations, booking_date=booking_date)
        self.trips[trip_id] = trip
        
        return trip
    
    def _has_existing_reservation(self, client_id, connection):
        """Checks if a client already has a reservation for a given connection"""
        # Check in-memory trips first
        for trip in self.trips.values():
            for reservation in trip.reservations:
                if (reservation.client.client_id == client_id and 
                    reservation.connection.route_id == connection.route_id):
                    return True
        
        # Also check database
        client_trips = self.db_manager.get_reservations_for_client(client_id, "")
        for trip_data in client_trips:
            if trip_data['route_id'] == connection.route_id:
                return True
        
        return False
    
    def get_client_trips(self, last_name, client_id):
        """
        Gets all trips for a client by last name and client ID from database.
        
        Returns:
            dict with 'current_trips' and 'past_trips' lists
        """
        # Get trips from database
        db_trips_data = self.db_manager.get_reservations_for_client(client_id, last_name)
        
        # Group by trip_id and build Trip objects
        trips_dict = {}
        for trip_data in db_trips_data:
            trip_id = trip_data['trip_id']
            
            if trip_id not in trips_dict:
                # Parse booking date
                booking_date_str = trip_data['booking_date']
                if isinstance(booking_date_str, str):
                    booking_date = datetime.fromisoformat(booking_date_str.replace('Z', '+00:00'))
                else:
                    booking_date = booking_date_str
                
                trips_dict[trip_id] = {
                    'trip_id': trip_id,
                    'booking_date': booking_date,
                    'reservations': []
                }
            
            # Get client data
            client = self._get_or_load_client(
                trip_data.get('first_name', ''),
                trip_data.get('last_name', last_name),
                trip_data.get('age', 0),
                client_id
            )
            
            # Create connection object
            connection = TrainConnection(
                route_id=trip_data['route_id'],
                departure_city=trip_data['departure_city'],
                arrival_city=trip_data['arrival_city'],
                departure_time=trip_data['departure_time'],
                arrival_time=trip_data['arrival_time'],
                train_type=trip_data['train_type'],
                days_of_operation=trip_data['days_of_operation'],
                first_class_rate=trip_data['first_class_rate'],
                second_class_rate=trip_data['second_class_rate']
            )
            
            # Create reservation
            reservation = Reservation(client, connection)
            trips_dict[trip_id]['reservations'].append(reservation)
        
        # Build Trip objects
        trip_objects = []
        for trip_data in trips_dict.values():
            trip = Trip(
                trip_id=trip_data['trip_id'],
                reservations=trip_data['reservations'],
                booking_date=trip_data['booking_date']
            )
            trip_objects.append(trip)
        
        # Separate current/future vs past trips
        current_trips = [trip for trip in trip_objects if trip.is_current_or_future()]
        past_trips = [trip for trip in trip_objects if not trip.is_current_or_future()]
        
        return {
            'current_trips': current_trips,
            'past_trips': past_trips
        }
    
    def _get_or_load_client(self, first_name, last_name, age, client_id):
        """Get client from cache or load from database"""
        if client_id in self.clients:
            return self.clients[client_id]
        
        # Load from database
        db_client = self.db_manager.get_client(client_id)
        if db_client:
            client = Client(
                db_client['first_name'],
                db_client['last_name'],
                db_client['age'],
                db_client['client_id']
            )
            self.clients[client_id] = client
            return client
        
        # Create new if not found
        client = Client(first_name, last_name, age, client_id)
        self.clients[client_id] = client
        return client
    
    def get_all_clients(self):
        """Returns all registered clients (from database)"""
        # This would require a method in DatabaseManager to get all clients
        # For now, return in-memory clients
        return list(self.clients.values())
    
    def get_all_trips(self):
        """Returns all trips (from database)"""
        # This would require loading all trips from database
        # For now, return in-memory trips
        return list(self.trips.values())
    
    def get_trip_by_id(self, trip_id):
        """
        Finds a trip by its ID.
        First checks in-memory cache, then loads from database if needed.
        """
        # Check in-memory cache
        if trip_id in self.trips:
            return self.trips[trip_id]
        
        # Load from database
        trip_data = self.db_manager.get_trip(trip_id)
        if not trip_data:
            return None
        
        # Get reservations for this trip
        reservations_data = self.db_manager.get_reservations_for_trip(trip_id)
        
        # Build trip object
        reservations = []
        for res_data in reservations_data:
            client = self._get_or_load_client(
                res_data['first_name'],
                res_data['last_name'],
                res_data['age'],
                res_data['client_id']
            )
            
            connection = TrainConnection(
                route_id=res_data['route_id'],
                departure_city=res_data['departure_city'],
                arrival_city=res_data['arrival_city'],
                departure_time=res_data['departure_time'],
                arrival_time=res_data['arrival_time'],
                train_type=res_data['train_type'],
                days_of_operation=res_data['days_of_operation'],
                first_class_rate=res_data['first_class_rate'],
                second_class_rate=res_data['second_class_rate']
            )
            
            reservation = Reservation(client, connection)
            reservation.reservation_id = res_data['reservation_id']
            
            # Load ticket
            ticket_data = self.db_manager.get_ticket_for_reservation(res_data['reservation_id'])
            if ticket_data:
                ticket = Ticket(reservation)
                ticket.ticket_id = ticket_data['ticket_id']
                reservation.ticket = ticket
            
            reservations.append(reservation)
        
        # Parse booking date
        booking_date_str = trip_data['booking_date']
        if isinstance(booking_date_str, str):
            booking_date = datetime.fromisoformat(booking_date_str.replace('Z', '+00:00'))
        else:
            booking_date = booking_date_str
        
        trip = Trip(
            trip_id=trip_id,
            reservations=reservations,
            booking_date=booking_date
        )
        
        # Cache it
        self.trips[trip_id] = trip
        return trip
