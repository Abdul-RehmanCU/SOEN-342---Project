# European Railway Network Search System

**SOEN 342 - Software Requirements and Deployment - Iteration 1**

**Team Members:**
- Abdul Rehman (40279024)
- Suriya Paramathypathy (40280915)  
- Karim Mawji (40281154)

## 🚄 Project Overview

A comprehensive web-based system for searching European train connections with support for direct and indirect routes (up to 2 stops). The system allows users to search by various parameters, calculate trip durations, and sort results by duration or price.

## ✨ Features

### Core Functionality
- **CSV Data Loading**: Loads 1,200+ European train connections from CSV
- **Advanced Search**: Search by departure city, arrival city, train type, and days of operation
- **Trip Duration Calculation**: Handles overnight trips and multi-day journeys
- **Indirect Connections**: Finds 1-stop and 2-stop connections with transfer times
- **Sorting**: Sort results by trip duration, first class price, or second class price
- **Modern Web Interface**: Beautiful, responsive web interface with search forms and results display

### Search Capabilities
- **Direct Connections**: Single train routes between cities
- **1-Stop Connections**: Routes with one transfer (2 trains)
- **2-Stop Connections**: Routes with two transfers (3 trains)
- **Transfer Time**: 15-minute minimum transfer time included
- **Filtering**: Filter by train type, days of operation, and other parameters

## 🛠️ Technical Stack

- **Backend**: Python 3.12, Flask 3.1.2
- **Data Processing**: Pandas 2.3.3, NumPy 2.2.6
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Architecture**: Object-oriented design with MVC pattern

## 📁 Project Structure

```
SOEN-342---Project/
├── app.py                          # Flask web application
├── requirements.txt                 # Python dependencies
├── test_system.py                  # System test script
├── data/
│   └── eu_rail_network.csv        # Train connection data (1,200+ routes)
├── models/
│   ├── __init__.py
│   ├── RailwayNetwork.py          # Main search engine class
│   └── TrainConnection.py         # Individual connection model
├── templates/
│   ├── index.html                 # Homepage
│   ├── search.html                # Search form
│   └── results.html               # Results display
└── static/
    └── styles.css                 # CSS styling
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SOEN-342---Project
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python3 app.py
   ```

4. **Access the web interface**
   - Open your browser to: `http://localhost:5001`
   - Click "Start Your Journey" to begin searching

### Alternative: Test Core Functionality
```bash
python3 test_system.py
```

## 🔍 Usage Guide

### Basic Search
1. Navigate to the search page
2. Enter departure and arrival cities
3. Optionally select train type and days of operation
4. Choose sorting preference (duration or price)
5. Click "Search Connections"

### Understanding Results
- **Direct Connections**: Single train routes
- **1-Stop Connections**: Routes with one transfer
- **2-Stop Connections**: Routes with two transfers
- **Transfer Time**: Minimum 15 minutes between connections
- **Pricing**: Combined prices for multi-leg journeys

### Search Tips
- Use exact city names as they appear in the database
- Try different train types to see all available options
- Use "Any Day" to see all available schedules
- Sort by duration to find the fastest routes
- Sort by price to find the most economical options

## 📊 Data Structure

The system processes CSV data with the following structure:
- **Route ID**: Unique identifier (not displayed to users)
- **Departure/Arrival Cities**: Start and end points
- **Times**: Departure and arrival times (supports overnight notation)
- **Train Type**: TGV, ICE, EuroCity, InterCity, etc.
- **Days of Operation**: Daily, Mon-Fri, Weekend, etc.
- **Pricing**: First and second class rates in euros

## 🧪 Testing

The system includes comprehensive testing:

```bash
# Run the test suite
python3 test_system.py
```

Tests cover:
- CSV data loading
- Search functionality (direct and indirect)
- Duration calculations
- Sorting algorithms
- Error handling

## 🎯 Assignment Requirements Compliance

✅ **Load CSV records into memory** - Implemented with pandas  
✅ **Search by any parameter except route-id** - Full search functionality  
✅ **Display all parameters + trip duration** - Complete results display  
✅ **Sort by trip duration and price** - Multiple sorting options  
✅ **Find indirect connections (1-stop, 2-stop)** - Advanced routing  
✅ **Add transfer time** - 15-minute minimum transfer time  
✅ **Object-oriented design** - Clean class structure  
✅ **Web interface** - Modern, responsive UI  

## 🔧 Technical Details

### Core Classes
- **`TrainConnection`**: Represents individual train routes
- **`RailwayNetwork`**: Main search engine with advanced algorithms

### Key Algorithms
- **Direct Search**: Simple city-to-city matching
- **Indirect Search**: Graph traversal for 1-stop and 2-stop routes
- **Duration Calculation**: Handles overnight trips and multi-day journeys
- **Sorting**: Efficient sorting by duration and price

### Performance
- Loads 1,200+ connections in <1 second
- Search results returned in <100ms
- Supports complex multi-stop routing
- Memory efficient with pandas data processing

## 🐛 Troubleshooting

### Common Issues
1. **Port 5000 in use**: The app runs on port 5001 by default
2. **Module not found**: Ensure all dependencies are installed
3. **CSV loading errors**: Check file path and data format

### Getting Help
- Check the test output for system status
- Review error messages in the web interface
- Ensure all dependencies are properly installed

## 📈 Future Enhancements

- Real-time data updates
- Advanced filtering options
- User preferences and favorites
- Mobile app integration
- Multi-language support

## 📄 License

This project is developed for educational purposes as part of SOEN 342 at Concordia University.

---

**Ready to explore Europe by rail? Start your journey at `http://localhost:5001`! 🚄**
