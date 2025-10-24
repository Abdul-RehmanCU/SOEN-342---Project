from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os

# Set a secret key for sessions and flash messages
SECRET_KEY = os.environ.get('SECRET_KEY', 'key')

from models.RailwayNetwork import RailwayNetwork
from models.BookingManager import BookingManager

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Required for sessions and flash messages

# Initialize railway network and booking manager
network = RailwayNetwork()
booking_manager = BookingManager()
csv_path = os.path.join('data', 'eu_rail_network.csv')
network.load_from_csv(csv_path)

#homepage
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get search parameters from form
        departure = request.form.get('departure_city', '').strip()
        arrival = request.form.get('arrival_city', '').strip()
        train_type = request.form.get('train_type', '').strip()
        days = request.form.get('days_of_operation', '').strip()
        
        # Build search parameters
        search_params = {}
        if departure:
            search_params['departure_city'] = departure
        if arrival:
            search_params['arrival_city'] = arrival
        if train_type:
            search_params['train_type'] = train_type
        if days:
            search_params['days_of_operation'] = days
        
        # Search for connections
        try:
            results = network.search(**search_params)
            
            # Sort results
            sort_by = request.form.get('sort_by', 'duration')
            results = network.sort_results(results, sort_by)
            
            return render_template('results.html', results=results, search_params=search_params, sort_by=sort_by)
        except ValueError as e:
            error_message = str(e)
            return render_template('search.html', error=error_message)
    
    return render_template('search.html')

@app.route("/upload")
def upload():
    return redirect(url_for('search'))

@app.route("/book/<route_id>", methods=['GET', 'POST'])
def book_trip(route_id):
    "Handle trip booking for a specific route"
    # Find the connection by route_id
    connection = None
    for conn in network.connections:
        if conn.route_id == route_id:
            connection = conn
            break
    
    if not connection:
        flash("Connection not found", "error")
        return redirect(url_for('search'))
    
    if request.method == 'POST':
        try:
            # Get traveller data from form
            travellers = []
            traveller_count = int(request.form.get('traveller_count', 1))
            
            for i in range(traveller_count):
                first_name = request.form.get(f'first_name_{i}', '').strip()
                last_name = request.form.get(f'last_name_{i}', '').strip()
                age = request.form.get(f'age_{i}', '').strip()
                client_id = request.form.get(f'client_id_{i}', '').strip()
                
                if not all([first_name, last_name, age, client_id]):
                    raise ValueError(f"All fields are required for traveller {i+1}")
                
                try:
                    age = int(age)
                    if age < 0 or age > 120:
                        raise ValueError(f"Invalid age for traveller {i+1}")
                except ValueError:
                    raise ValueError(f"Age must be a valid number for traveller {i+1}")
                
                travellers.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': age,
                    'client_id': client_id
                })
            
            # Book the trip
            trip = booking_manager.book_trip(travellers, connection)
            
            flash(f"Trip successfully booked! Trip ID: {trip.trip_id}", "success")
            return redirect(url_for('booking_confirmation', trip_id=trip.trip_id))
            
        except ValueError as e:
            flash(str(e), "error")
            return render_template('book.html', connection=connection)
    
    return render_template('book.html', connection=connection)

@app.route("/booking_confirmation/<trip_id>")
def booking_confirmation(trip_id):
    "Show booking confirmation details"
    trip = booking_manager.get_trip_by_id(trip_id)
    if not trip:
        flash("Trip not found", "error")
        return redirect(url_for('search'))
    
    return render_template('booking_confirmation.html', trip=trip)

@app.route("/view_trips", methods=['GET', 'POST'])
def view_trips():
    "Allow clients to view their trips by last name and ID"
    if request.method == 'POST':
        last_name = request.form.get('last_name', '').strip()
        client_id = request.form.get('client_id', '').strip()
        
        if not last_name or not client_id:
            flash("Both last name and ID are required", "error")
            return render_template('view_trips.html')
        
        try:
            trips_data = booking_manager.get_client_trips(last_name, client_id)
            return render_template('view_trips.html', 
                                 trips_data=trips_data, 
                                 last_name=last_name, 
                                 client_id=client_id)
        except Exception as e:
            flash(f"Error retrieving trips: {str(e)}", "error")
            return render_template('view_trips.html')
    
    return render_template('view_trips.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
