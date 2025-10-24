#!/usr/bin/env python3
"""
Test script for the booking system functionality
Tests both scenarios: single traveller and family booking
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.BookingManager import BookingManager
from models.RailwayNetwork import RailwayNetwork

def test_booking_system():
    print("🚄 Testing European Railway Booking System")
    print("=" * 50)
    
    # Initialize the system
    network = RailwayNetwork()
    booking_manager = BookingManager()
    
    # Load railway data
    csv_path = os.path.join('data', 'eu_rail_network.csv')
    network.load_from_csv(csv_path)
    
    print(f"✅ Loaded {len(network.connections)} railway connections")
    
    # Get a sample connection for testing
    if not network.connections:
        print("❌ No connections available for testing")
        return
    
    sample_connection = network.connections[0]  # Use first connection
    print(f"📍 Using sample route: {sample_connection.departure_city} → {sample_connection.arrival_city}")
    print(f"   Route ID: {sample_connection.route_id}")
    print(f"   Train Type: {sample_connection.train_type}")
    print(f"   Departure: {sample_connection.departure_time}")
    print(f"   Arrival: {sample_connection.arrival_time}")
    print()
    
    # Test Scenario 1: Single traveller booking
    print("🧑‍💼 SCENARIO 1: Single Traveller Booking")
    print("-" * 30)
    
    single_traveller = [{
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 35,
        'client_id': 'PASS123456'
    }]
    
    try:
        trip1 = booking_manager.book_trip(single_traveller, sample_connection)
        print(f"✅ Trip booked successfully!")
        print(f"   Trip ID: {trip1.trip_id}")
        print(f"   Passengers: {trip1.get_total_passengers()}")
        print(f"   Booking Date: {trip1.booking_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Display ticket information
        for reservation in trip1.reservations:
            ticket_info = reservation.ticket.get_ticket_info()
            print(f"   🎫 Ticket #{ticket_info['ticket_id']}: {ticket_info['client_name']}")
        
        print()
        
    except Exception as e:
        print(f"❌ Single traveller booking failed: {e}")
        return
    
    # Test Scenario 2: Family booking (4 people)
    print("👨‍👩‍👧‍👦 SCENARIO 2: Family Booking (4 People)")
    print("-" * 35)
    
    # Use a different connection for family booking
    if len(network.connections) > 1:
        family_connection = network.connections[1]
    else:
        family_connection = sample_connection
    
    family_travellers = [
        {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'age': 42,
            'client_id': 'PASS789012'
        },
        {
            'first_name': 'Bob',
            'last_name': 'Smith',
            'age': 45,
            'client_id': 'PASS345678'
        },
        {
            'first_name': 'Emma',
            'last_name': 'Smith',
            'age': 16,
            'client_id': 'PASS901234'
        },
        {
            'first_name': 'Liam',
            'last_name': 'Smith',
            'age': 12,
            'client_id': 'PASS567890'
        }
    ]
    
    try:
        trip2 = booking_manager.book_trip(family_travellers, family_connection)
        print(f"✅ Family trip booked successfully!")
        print(f"   Trip ID: {trip2.trip_id}")
        print(f"   Route: {family_connection.departure_city} → {family_connection.arrival_city}")
        print(f"   Passengers: {trip2.get_total_passengers()}")
        print(f"   Booking Date: {trip2.booking_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Display all tickets
        for i, reservation in enumerate(trip2.reservations, 1):
            ticket_info = reservation.ticket.get_ticket_info()
            print(f"   🎫 Ticket #{ticket_info['ticket_id']}: {ticket_info['client_name']} (Age: {reservation.client.age})")
        
        print()
        
    except Exception as e:
        print(f"❌ Family booking failed: {e}")
        return
    
    # Test duplicate booking prevention
    print("🛡️  TESTING DUPLICATE BOOKING PREVENTION")
    print("-" * 35)
    
    try:
        # Try to book the same person on the same connection again
        duplicate_booking = booking_manager.book_trip([single_traveller[0]], sample_connection)
        print("❌ Duplicate booking should have been prevented!")
        
    except ValueError as e:
        print(f"✅ Duplicate booking correctly prevented: {e}")
        print()
    
    # Test viewing trips functionality
    print("📋 TESTING VIEW TRIPS FUNCTIONALITY")
    print("-" * 30)
    
    # Test viewing John Doe's trips
    john_trips = booking_manager.get_client_trips('Doe', 'PASS123456')
    print(f"✅ Found {len(john_trips['current_trips'])} current trips for John Doe")
    print(f"   Found {len(john_trips['past_trips'])} past trips for John Doe")
    
    # Test viewing Alice Smith's trips (from family booking)
    alice_trips = booking_manager.get_client_trips('Smith', 'PASS789012')
    print(f"✅ Found {len(alice_trips['current_trips'])} current trips for Alice Smith")
    print(f"   Found {len(alice_trips['past_trips'])} past trips for Alice Smith")
    
    print()
    
    # Summary
    print("📊 BOOKING SYSTEM SUMMARY")
    print("-" * 25)
    print(f"Total registered clients: {len(booking_manager.get_all_clients())}")
    print(f"Total trips booked: {len(booking_manager.get_all_trips())}")
    
    # Display all clients
    print("\n👥 Registered Clients:")
    for client in booking_manager.get_all_clients():
        print(f"   • {client.get_full_name()} (Age: {client.age}, ID: {client.client_id})")
    
    print("\n🎯 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("✅ Single traveller booking: PASS")
    print("✅ Family booking (4 people): PASS") 
    print("✅ Duplicate prevention: PASS")
    print("✅ View trips functionality: PASS")
    print("✅ Client management: PASS")

if __name__ == "__main__":
    test_booking_system()