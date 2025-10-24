class Client:
    """Represents a client who can make reservations"""
    
    def __init__(self, first_name, last_name, age, client_id):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.client_id = client_id  # Generic ID (passport, state-id, etc.)
    
    def get_full_name(self):
        """Returns the client's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"Client: {self.get_full_name()} (Age: {self.age}, ID: {self.client_id})"
    
    def __eq__(self, other):
        """Two clients are equal if they have the same ID"""
        if isinstance(other, Client):
            return self.client_id == other.client_id
        return False
    
    def __hash__(self):
        """Hash based on client_id for use in sets/dicts"""
        return hash(self.client_id)