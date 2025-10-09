import pandas as pd
import re
from datetime import datetime, timedelta
from .TrainConnection import TrainConnection

class RailwayNetwork:
    MIN_TRANSFER = timedelta(minutes=15)
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




    def load_from_csv(self, filepath):
        #load from csv and clear any garbage data with incomplete rows
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return
        
        df =df.dropna() #removes rows with missing vlaues

        # Create TrainConnection objects and add to connections list
        for _, row in df.iterrows():
            try:
                connection = TrainConnection(
                    route_id=row['Route ID'],
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
                    # Only include if second train departs after first train arrives + transfer time
                    dt_c2_departure = self._get_datetime(c2.departure_time, dt_c1_arrival)
                    dt_c2_arrival = self._get_datetime(c2.arrival_time, dt_c2_departure)
                    if dt_c2_departure >= dt_c1_arrival + self.MIN_TRANSFER:
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

                if dt_c2_departure < dt_c1_arrival + self.MIN_TRANSFER:
                    continue  # infeasible transfer

                for c3 in self.connections:
                    if c3.departure_city.lower() != c2.arrival_city.lower():
                        continue
                    if c3.arrival_city.lower() != arrival_city.lower():
                        continue
                    dt_c3_departure = self._get_datetime(c3.departure_time, dt_c2_arrival)
                    dt_c3_arrival = self._get_datetime(c3.arrival_time, dt_c3_departure)

                    if dt_c3_departure >= dt_c2_arrival + self.MIN_TRANSFER:
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