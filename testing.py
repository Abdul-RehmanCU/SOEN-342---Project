from datetime import datetime, timedelta
import re

def calculate_duration(departure_time_str, arrival_time_str):
    """Calculates the difference in times and returns as HH:MM format"""
    
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

# Test cases
print(calculate_duration("23:30", "15:15 (+1d)"))  # Should output: 49:45
print(calculate_duration("08:00", "10:30"))         # Should output: 2:30
print(calculate_duration("23:00", "01:00"))         # Should output: 26:00 (overnight)