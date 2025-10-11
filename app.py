from flask import Flask, render_template, request, redirect, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from models.RailwayNetwork import RailwayNetwork
import os

app = Flask(__name__)

# Initialize railway network
network = RailwayNetwork()
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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
