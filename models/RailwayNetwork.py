import pandas as pd
import re
from datetime import datetime, timedelta
from .TrainConnection import TrainConnection

class RailwayNetwork:
    MIN_TRANSFER = timedelta(minutes=15)
    # Layover policy: After hours = 10 PM to 6 AM
    AFTER_HOURS_START = 22  # 10 PM
    AFTER_HOURS_END = 6     # 6 AM
    MAX_LAYOVER_DAYTIME = timedelta(hours=2)  # 1-2 hours OK during day
    MAX_LAYOVER_AFTER_HOURS = timedelta(minutes=30)  # Max 30 min after hours
    
    def __init__(self):
        self.connections = []




    def _get_datetime(self, time_str, reference_datetime=None):
        extra_days = 0
        match = re.search(r"\(\+(\d+)d\)", time_str)
        if match:
            extra_days = int(match.group(1))
            time_str = re.sub(r"\s*\(\+\d+d\)", "", time_str).strip()

        dt = datetime.strptime(time_str, "%H:%M")

        if reference_datetime:
            dt = dt.replace(year=reference_datetime.year,
                            month=reference_datetime.month,
                            day=reference_datetime.day)
            dt += timedelta(days=extra_days)
            if extra_days == 0 and dt < reference_datetime:
                dt += timedelta(days=1)
        else:
            dt = dt.replace(year=1900, month=1, day=1)

        return dt
    
    def _is_after_hours(self, dt):
        """Check if a datetime is during after hours (10 PM - 6 AM)"""
        hour = dt.hour
        return hour >= self.AFTER_HOURS_START or hour < self.AFTER_HOURS_END
    
    def _is_layover_acceptable(self, arrival_time, departure_time):
        """
        Check if layover duration is acceptable based on policy.
        
        Policy:
        - During day (6 AM - 10 PM): Layover of 1-2 hours is OK
        - After hours (10 PM - 6 AM): Max layover is 30 minutes
        
        Args:
            arrival_time: datetime when first train arrives
            departure_time: datetime when second train departs
            
        Returns:
            True if layover is acceptable, False otherwise
        """
        layover_duration = departure_time - arrival_time
        
        # Must meet minimum transfer time
        if layover_duration < self.MIN_TRANSFER:
            return False
        
        # Check if arrival is during after hours
        if self._is_after_hours(arrival_time):
            # After hours: max 30 minutes
            return layover_duration <= self.MAX_LAYOVER_AFTER_HOURS
        else:
            # Daytime: up to 2 hours OK
            return layover_duration <= self.MAX_LAYOVER_DAYTIME




    def load_from_csv(self, filepath, db_manager=None):
        """
        Load routes from CSV file and persist to database.
        If routes already exist in database, load from database instead.
        
        Args:
            filepath: Path to CSV file
            db_manager: DatabaseManager instance for persistence
        """
        # If database manager provided, check if routes already exist
        if db_manager:
            db_routes = db_manager.load_all_routes()
            if db_routes:
                # Load from database
                self.connections = []
                for route_data in db_routes:
                    connection = TrainConnection(
                        route_id=route_data['route_id'],
                        departure_city=route_data['departure_city'],
                        arrival_city=route_data['arrival_city'],
                        departure_time=route_data['departure_time'],
                        arrival_time=route_data['arrival_time'],
                        train_type=route_data['train_type'],
                        days_of_operation=route_data['days_of_operation'],
                        first_class_rate=route_data['first_class_rate'],
                        second_class_rate=route_data['second_class_rate']
                    )
                    self.connections.append(connection)
                return
        
        # Load from CSV and persist to database
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return
        
        df = df.dropna()  # removes rows with missing values

        # Create TrainConnection objects and add to connections list
        for _, row in df.iterrows():
            try:
                route_id = row['Route ID']
                connection = TrainConnection(
                    route_id=route_id,
                    departure_city=row['Departure City'],
                    arrival_city=row['Arrival City'],
                    departure_time=row['Departure Time'],
                    arrival_time=row['Arrival Time'],
                    train_type=row['Train Type'],
                    days_of_operation=row['Days of Operation'],
                    first_class_rate=row['First Class ticket rate (in euro)'],
                    second_class_rate=row['Second Class ticket rate (in euro)']
                )
                self.connections.append(connection)
                
                # Persist to database if manager provided
                if db_manager:
                    route_data = {
                        'route_id': route_id,
                        'departure_city': row['Departure City'],
                        'arrival_city': row['Arrival City'],
                        'departure_time': row['Departure Time'],
                        'arrival_time': row['Arrival Time'],
                        'train_type': row['Train Type'],
                        'days_of_operation': row['Days of Operation'],
                        'first_class_rate': float(row['First Class ticket rate (in euro)']),
                        'second_class_rate': float(row['Second Class ticket rate (in euro)'])
                    }
                    db_manager.insert_route(route_data)
                    
            except Exception as e:
                print(f"Skipping row due to error: {e}")
        




    def filter_connections(self, connections, **kwargs):
        """Filter connections by kwargs except route_id, departure_city, arrival_city."""
        filtered = connections
        for key, value in kwargs.items():
            if key not in ['route_id', 'departure_city', 'arrival_city']:
                filtered = [c for c in filtered if str(getattr(c, key)).lower() == str(value).lower()]
        return filtered






    #1. search for a connection using any parameter except the route ID
    #2. system should display all matches by presenting all parameters
    #3. plus trip duration which needs to be calculated
    #4. in case no direct connection , show indirect (1-2 stop only)
    def search(self, **kwargs):
        departure_city = kwargs.get('departure_city')
        arrival_city = kwargs.get('arrival_city')

        if not departure_city or not arrival_city:
            raise ValueError("Both departure_city and arrival_city must be provided.")
        
        MIN_TRANSFER = timedelta(minutes=15)  # minimum time to change trains


        #this is for the direct connections
        direct = [c for c in self.connections
              if c.departure_city.lower() == departure_city.lower() and
                 c.arrival_city.lower() == arrival_city.lower()]
        direct = self.filter_connections(direct, **kwargs)

        #this is for the indirect connections(1 stop)
        one_stop =[]
        for c1 in self.connections:
            if c1.departure_city.lower()!=departure_city.lower():
                continue
            dt_c1_departure = self._get_datetime(c1.departure_time)
            dt_c1_arrival = self._get_datetime(c1.arrival_time, dt_c1_departure)

            for c2 in self.connections:
                if c2.arrival_city.lower()!=arrival_city.lower():
                    continue
                
                if c1.arrival_city.lower() == c2.departure_city.lower():
                    # Check layover policy: ensure acceptable layover duration
                    dt_c2_departure = self._get_datetime(c2.departure_time, dt_c1_arrival)
                    dt_c2_arrival = self._get_datetime(c2.arrival_time, dt_c2_departure)
                    # Apply layover policy check
                    if self._is_layover_acceptable(dt_c1_arrival, dt_c2_departure):
                        total_duration = dt_c2_arrival - dt_c1_departure
                        one_stop.append({
                            'stops': 1,
                            'connections': [c1, c2],
                            'total_duration': total_duration
                        })
        

        #2 stop connections
        two_stop = []
        for c1 in self.connections:
            if c1.departure_city.lower() != departure_city.lower():
                continue
            dt_c1_departure = self._get_datetime(c1.departure_time)
            dt_c1_arrival = self._get_datetime(c1.arrival_time, dt_c1_departure)

            for c2 in self.connections:
                if c2.departure_city.lower() != c1.arrival_city.lower():
                    continue
                dt_c2_departure = self._get_datetime(c2.departure_time, dt_c1_arrival)
                dt_c2_arrival = self._get_datetime(c2.arrival_time, dt_c2_departure)

                # Check first layover (c1 to c2)
                if not self._is_layover_acceptable(dt_c1_arrival, dt_c2_departure):
                    continue  # First layover doesn't meet policy

                for c3 in self.connections:
                    if c3.departure_city.lower() != c2.arrival_city.lower():
                        continue
                    if c3.arrival_city.lower() != arrival_city.lower():
                        continue
                    dt_c3_departure = self._get_datetime(c3.departure_time, dt_c2_arrival)
                    dt_c3_arrival = self._get_datetime(c3.arrival_time, dt_c3_departure)
                    
                    # Check second layover (c2 to c3)
                    if self._is_layover_acceptable(dt_c2_arrival, dt_c3_departure):
                        total_duration = dt_c3_arrival - dt_c1_departure
                        two_stop.append({
                            'stops': 2,
                            'connections': [c1, c2, c3],
                            'total_duration': total_duration
                        })
        return {
            'direct': direct,
            'one_stop': one_stop,
            'two_stop': two_stop
        }

    def sort_results(self, results, key='duration'):
        """Sort results by duration or price"""
        if key == 'duration':
            # Sort direct connections by duration
            results['direct'].sort(key=lambda x: self._get_duration_minutes(x))
            # Sort indirect connections by total duration
            results['one_stop'].sort(key=lambda x: x['total_duration'])
            results['two_stop'].sort(key=lambda x: x['total_duration'])
        elif key == 'price_first':
            # Sort by first class price
            results['direct'].sort(key=lambda x: x.first_class_rate)
        elif key == 'price_second':
            # Sort by second class price
            results['direct'].sort(key=lambda x: x.second_class_rate)
        return results
    
    def _get_duration_minutes(self, connection):
        """Helper method to get duration in minutes for sorting"""
        duration_str = connection.calculate_duration()
        hours, minutes = map(int, duration_str.split(':'))
        return hours * 60 + minutes