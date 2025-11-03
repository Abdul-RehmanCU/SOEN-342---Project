class Ticket:

    def __init__(self, reservation, ticket_id=None):
        """
        Initialize a Ticket.
        
        Args:
            reservation: Reservation object this ticket belongs to
            ticket_id: Numerical ticket ID (from database if provided)
        """
        self.ticket_id = ticket_id  # Will be set by database
        self.reservation = reservation
        
    def get_ticket_info(self):
        "Returns formatted ticket information"
        return {
            'ticket_id': self.ticket_id,
            'client_name': self.reservation.client.get_full_name(),
            'client_id': self.reservation.client.client_id,
            'route': f"{self.reservation.connection.departure_city} → {self.reservation.connection.arrival_city}",
            'departure_time': self.reservation.connection.departure_time,
            'arrival_time': self.reservation.connection.arrival_time,
            'train_type': self.reservation.connection.train_type,
            'duration': self.reservation.connection.calculate_duration(),
            'price_first': self.reservation.connection.first_class_rate,
            'price_second': self.reservation.connection.second_class_rate
        }
    
    def __str__(self):
        info = self.get_ticket_info()
        return f"Ticket #{info['ticket_id']}: {info['client_name']} - {info['route']}"