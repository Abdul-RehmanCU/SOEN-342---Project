from datetime import datetime, timedelta
import re
class TrainConnection:
    def __init__(self, route_id, departure_city, arrival_city, departure_time, arrival_time, train_type, days_of_operation, first_class_rate, second_class_rate):
        self.route_id = route_id #private parameter (not made public)
        self.departure_city = departure_city
        self.arrival_city = arrival_city
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.train_type = train_type
        self.days_of_operation = days_of_operation
        self.first_class_rate = float(first_class_rate)
        self.second_class_rate = float(second_class_rate)

        

    def calculate_duration(self, departure_time_str=None, arrival_time_str=None):
        "Calculates the difference in times and returns as HH:MM format"
        
        # Use instance attributes if no parameters provided
        if departure_time_str is None:
            departure_time_str = self.departure_time
        if arrival_time_str is None:
            arrival_time_str = self.arrival_time
            
        extra_days = 0

        # Search for any extra days in the string
        match = re.search(r"\(\+(\d+)d\)", arrival_time_str)
        if match:
            extra_days = int(match.group(1))
            arrival_time_str = re.sub(r"\s*\(\+\d+d\)", "", arrival_time_str).strip()

        # Parse time strings
        fmt = "%H:%M"
        departure = datetime.strptime(departure_time_str, fmt)
        arrival = datetime.strptime(arrival_time_str, fmt)  

        # Add extra days
        arrival += timedelta(days=extra_days)

        # Handle implicit overnight if no (+Nd) and arrival < departure
        if extra_days == 0 and arrival < departure:
            arrival += timedelta(days=1)

        # Calculate duration
        duration = arrival - departure
        
        # Convert to total hours and minutes
        total_minutes = int(duration.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        # Return in HH:MM format
        return f"{hours}:{minutes:02d}"

