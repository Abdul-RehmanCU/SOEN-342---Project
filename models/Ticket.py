class Ticket:
    """Represents a ticket that documents a reservation with a unique numerical ID"""
    
    _next_ticket_id = 100000  # Start ticket IDs at 100000
    
    def __init__(self, reservation):
        self.ticket_id = Ticket._next_ticket_id
        Ticket._next_ticket_id += 1
        self.reservation = reservation
        
    def get_ticket_info(self):
        """Returns formatted ticket information"""
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