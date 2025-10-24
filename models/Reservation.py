from .Ticket import Ticket

class Reservation:
    """Represents a reservation linking a client to a connection, documented by a ticket"""
    
    def __init__(self, client, connection):
        self.client = client
        self.connection = connection
        self.ticket = Ticket(self)
        
    def get_reservation_info(self):
        """Returns formatted reservation information"""
        return {
            'client': self.client,
            'connection': self.connection,
            'ticket': self.ticket,
            'ticket_info': self.ticket.get_ticket_info()
        }
    
    def __str__(self):
        return f"Reservation for {self.client.get_full_name()} on {self.connection.departure_city} → {self.connection.arrival_city} (Ticket #{self.ticket.ticket_id})"