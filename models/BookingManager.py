from .Client import Client
from .Reservation import Reservation
from .Trip import Trip

class BookingManager:
    
    def __init__(self):
        self.clients = {}  # client_id -> Client object
        self.trips = []    # List of all trips
        
    def get_or_create_client(self, first_name, last_name, age, client_id):
        "Gets existing client or creates a new one"
        if client_id in self.clients:
            # Update client info if it exists
            client = self.clients[client_id]
            client.first_name = first_name
            client.last_name = last_name
            client.age = age
            return client
        else:
            # Create new client
            client = Client(first_name, last_name, age, client_id)
            self.clients[client_id] = client
            return client
    
    def book_trip(self, travellers, connection):
        """
        Books a trip for one or more travellers on a given connection
        
        Args:
            travellers: List of dicts with keys: 'first_name', 'last_name', 'age', 'client_id'
            connection: TrainConnection object
            
        Returns:
            Trip object with all reservations
        """
        if not travellers:
            raise ValueError("At least one traveller is required")
        
        # Validate that each client can only have one reservation per connection
        for traveller_info in travellers:
            client_id = traveller_info['client_id']
            if self._has_existing_reservation(client_id, connection):
                raise ValueError(f"Client {client_id} already has a reservation for this connection")
        
        # Create or get clients and make reservations
        reservations = []
        for traveller_info in travellers:
            client = self.get_or_create_client(
                traveller_info['first_name'],
                traveller_info['last_name'],
                traveller_info['age'],
                traveller_info['client_id']
            )
            
            reservation = Reservation(client, connection)
            reservations.append(reservation)
        
        # Create trip and add to records
        trip = Trip(reservations)
        self.trips.append(trip)
        
        return trip
    
    def _has_existing_reservation(self, client_id, connection):
        "Checks if a client already has a reservation for a given connection"
        for trip in self.trips:
            for reservation in trip.reservations:
                if (reservation.client.client_id == client_id and 
                    reservation.connection.route_id == connection.route_id):
                    return True
        return False
    
    def get_client_trips(self, last_name, client_id):
        """
        Gets all trips for a client by last name and client ID
        
        Returns:
            dict with 'current_trips' and 'past_trips' lists
        """
        client_trips = []
        
        # Find all trips for this client
        for trip in self.trips:
            for reservation in trip.reservations:
                if (reservation.client.last_name.lower() == last_name.lower() and 
                    reservation.client.client_id == client_id):
                    client_trips.append(trip)
                    break  # Only add the trip once even if multiple reservations
        
        # Separate current/future vs past trips
        current_trips = [trip for trip in client_trips if trip.is_current_or_future()]
        past_trips = [trip for trip in client_trips if not trip.is_current_or_future()]
        
        return {
            'current_trips': current_trips,
            'past_trips': past_trips
        }
    
    def get_all_clients(self):
        "Returns all registered clients"
        return list(self.clients.values())
    
    def get_all_trips(self):
        "Returns all trips"
        return self.trips
    
    def get_trip_by_id(self, trip_id):
        "Finds a trip by its ID"
        for trip in self.trips:
            if trip.trip_id == trip_id:
                return trip
        return None