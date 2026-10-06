import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import uuid

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="Transport Management System", layout="wide")

# -------------------------------
# Initialize Session State
# -------------------------------
if 'drivers' not in st.session_state:
    st.session_state.drivers = [
        {"id": "D1", "name": "John Smith", "phone": "555-0101", "reg_date": "2023-01-15", "area": "Downtown"},
        {"id": "D2", "name": "Emily Davis", "phone": "555-0102", "reg_date": "2023-02-20", "area": "Airport"}
    ]

if 'vehicles' not in st.session_state:
    st.session_state.vehicles = [
        {"id": "V1", "plate": "ABC-1234", "type": "Bus", "status": "Active", "driver_id": "D1"},
        {"id": "V2", "plate": "XYZ-5678", "type": "Van", "status": "Maintenance", "driver_id": None}
    ]

if 'cities' not in st.session_state:
    st.session_state.cities = [
        {"id": "C1", "name": "Los Angeles", "state": "California"},
        {"id": "C2", "name": "San Francisco", "state": "California"}
    ]

if 'areas' not in st.session_state:
    st.session_state.areas = [
        {"id": "A1", "name": "Downtown", "city_id": "C1"},
        {"id": "A2", "name": "Airport", "city_id": "C1"}
    ]

if 'routes' not in st.session_state:
    st.session_state.routes = [
        {"id": "R1", "from_city": "Los Angeles", "to_city": "San Francisco", "distance_km": 380}
    ]

if 'trips' not in st.session_state:
    st.session_state.trips = [
        {
            "id": "T1", "vehicle_id": "V1", "route_id": "R1", "start_city": "Los Angeles",
            "end_city": "San Francisco", "departure": "2025-03-20 08:00", "arrival": "2025-03-20 12:30",
            "distance": 380, "price": 45.00, "status": "Scheduled", "booked_seats": 0, "total_seats": 40
        }
    ]

if 'passengers' not in st.session_state:
    st.session_state.passengers = [
        {"id": "P1", "name": "Alice Johnson", "phone": "555-0201", "email": "alice@example.com"}
    ]

if 'bookings' not in st.session_state:
    st.session_state.bookings = [
        {"id": "B1", "trip_id": "T1", "passenger_id": "P1", "seat_number": 12, "payment_status": "Paid", "booking_date": "2025-03-10"}
    ]

if 'driver_queue' not in st.session_state:
    st.session_state.driver_queue = [
        {"id": "Q1", "driver_id": "D1", "position": 1, "date": "2025-03-15", "status": "Ready"},
        {"id": "Q2", "driver_id": "D2", "position": 2, "date": "2025-03-16", "status": "Waiting"}
    ]

if 'schedule' not in st.session_state:
    st.session_state.schedule = [
        {"id": "S1", "trip_id": "T1", "date": "2025-03-20", "departure_time": "08:00", "arrival_time": "12:30"}
    ]

if 'reviews' not in st.session_state:
    st.session_state.reviews = [
        {"id": "R1", "trip_id": "T1", "rating": 5, "comment": "Excellent service!", "passenger_name": "Alice Johnson"}
    ]

# Helper functions
def generate_id(prefix):
    return f"{prefix}{len(st.session_state.get(prefix.lower() + 's', [])) + 1}{random.randint(10, 99)}"

def get_driver_name(driver_id):
    for d in st.session_state.drivers:
        if d['id'] == driver_id:
            return d['name']
    return "Unassigned"

def get_vehicle_plate(vehicle_id):
    for v in st.session_state.vehicles:
        if v['id'] == vehicle_id:
            return v['plate']
    return "Unknown"

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("🚍 Transport Manager")
menu = st.sidebar.radio("Navigate", [
    "Dashboard", "City & Area", "Driver Management", "Vehicle Management",
    "Route Management", "Trip Management", "Passenger & Booking", "Driver Queue",
    "Schedule", "Payments", "Reviews"
])

# -------------------------------
# Dashboard
# -------------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    total_trips = len(st.session_state.trips)
    total_drivers = len(st.session_state.drivers)
    total_vehicles = len(st.session_state.vehicles)
    total_passengers = len(st.session_state.passengers)
    total_revenue = sum([t['price'] for b in st.session_state.bookings if b['payment_status'] == "Paid" for t in st.session_state.trips if t['id'] == b['trip_id']])
    
    col1.metric("🚌 Total Trips", total_trips)
    col2.metric("👨‍✈️ Drivers", total_drivers)
    col3.metric("🚛 Vehicles", total_vehicles)
    col4.metric("🧑 Passengers", total_passengers)
    col5.metric("💰 Revenue", f"${total_revenue:.2f}")
    
    st.subheader("📋 Recent Trips")
    recent_trips = st.session_state.trips[-5:] if len(st.session_state.trips) > 5 else st.session_state.trips
    if recent_trips:
        df_trips = pd.DataFrame(recent_trips)[['id', 'start_city', 'end_city', 'departure', 'status', 'price']]
        st.dataframe(df_trips, use_container_width=True)
    else:
        st.info("No trips available.")

# -------------------------------
# City & Area Management
# -------------------------------
elif menu == "City & Area":
    st.title("🏙️ City & Area Management")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add City")
        with st.form("add_city_form"):
            city_name = st.text_input("City Name")
            state_region = st.text_input("State/Region")
            submitted = st.form_submit_button("Add City")
            if submitted and city_name and state_region:
                new_id = f"C{len(st.session_state.cities)+1}"
                st.session_state.cities.append({"id": new_id, "name": city_name, "state": state_region})
                st.success(f"City {city_name} added!")
    
    with col2:
        st.subheader("Add Area linked to City")
        with st.form("add_area_form"):
            city_options = {c['id']: f"{c['name']}, {c['state']}" for c in st.session_state.cities}
            selected_city_id = st.selectbox("Select City", options=list(city_options.keys()), format_func=lambda x: city_options[x])
            area_name = st.text_input("Area Name")
            submitted_area = st.form_submit_button("Add Area")
            if submitted_area and area_name:
                new_id = f"A{len(st.session_state.areas)+1}"
                st.session_state.areas.append({"id": new_id, "name": area_name, "city_id": selected_city_id})
                st.success(f"Area {area_name} added!")
    
    st.subheader("Cities List")
    if st.session_state.cities:
        df_cities = pd.DataFrame(st.session_state.cities)
        st.dataframe(df_cities, use_container_width=True)
    else:
        st.info("No cities yet.")
    
    st.subheader("Areas List")
    if st.session_state.areas:
        areas_with_city = []
        for a in st.session_state.areas:
            city = next((c for c in st.session_state.cities if c['id'] == a['city_id']), None)
            city_name = city['name'] if city else "Unknown"
            areas_with_city.append({"Area ID": a['id'], "Area Name": a['name'], "City": city_name})
        df_areas = pd.DataFrame(areas_with_city)
        st.dataframe(df_areas, use_container_width=True)
    else:
        st.info("No areas yet.")

# -------------------------------
# Driver Management
# -------------------------------
elif menu == "Driver Management":
    st.title("👨‍✈️ Driver Management")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Driver")
        with st.form("add_driver_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            reg_date = st.date_input("Registration Date", datetime.now())
            # assign to area
            area_options = {a['id']: a['name'] for a in st.session_state.areas}
            area_id = st.selectbox("Assign to Area", options=list(area_options.keys()), format_func=lambda x: area_options[x])
            submitted = st.form_submit_button("Add Driver")
            if submitted and name and phone:
                new_id = f"D{len(st.session_state.drivers)+1}"
                area_name = area_options[area_id]
                st.session_state.drivers.append({
                    "id": new_id, "name": name, "phone": phone,
                    "reg_date": str(reg_date), "area": area_name
                })
                st.success(f"Driver {name} added!")
    
    with col2:
        st.subheader("Driver List")
        if st.session_state.drivers:
            df_drivers = pd.DataFrame(st.session_state.drivers)
            st.dataframe(df_drivers, use_container_width=True)
        else:
            st.info("No drivers yet.")

# -------------------------------
# Vehicle Management
# -------------------------------
elif menu == "Vehicle Management":
    st.title("🚛 Vehicle Management")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add Vehicle")
        with st.form("add_vehicle_form"):
            plate = st.text_input("Plate Number")
            vehicle_type = st.selectbox("Type", ["Bus", "Van", "Truck", "Minibus"])
            status = st.selectbox("Status", ["Active", "Maintenance", "Retired"])
            driver_options = {d['id']: d['name'] for d in st.session_state.drivers}
            driver_id = st.selectbox("Assign to Driver (optional)", options=[None] + list(driver_options.keys()), 
                                     format_func=lambda x: "None" if x is None else driver_options[x])
            submitted = st.form_submit_button("Add Vehicle")
            if submitted and plate:
                new_id = f"V{len(st.session_state.vehicles)+1}"
                st.session_state.vehicles.append({
                    "id": new_id, "plate": plate, "type": vehicle_type,
                    "status": status, "driver_id": driver_id
                })
                st.success(f"Vehicle {plate} added!")
    
    with col2:
        st.subheader("Vehicle List")
        if st.session_state.vehicles:
            vehicles_display = []
            for v in st.session_state.vehicles:
                driver_name = get_driver_name(v['driver_id'])
                vehicles_display.append({
                    "ID": v['id'], "Plate": v['plate'], "Type": v['type'],
                    "Status": v['status'], "Driver": driver_name
                })
            df_vehicles = pd.DataFrame(vehicles_display)
            st.dataframe(df_vehicles, use_container_width=True)
        else:
            st.info("No vehicles yet.")

# -------------------------------
# Route Management
# -------------------------------
elif menu == "Route Management":
    st.title("🗺️ Route Management")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create Route")
        with st.form("add_route_form"):
            city_names = [c['name'] for c in st.session_state.cities]
            from_city = st.selectbox("From City", city_names)
            to_city = st.selectbox("To City", city_names)
            distance = st.number_input("Distance (km)", min_value=1)
            submitted = st.form_submit_button("Add Route")
            if submitted and from_city != to_city:
                new_id = f"R{len(st.session_state.routes)+1}"
                st.session_state.routes.append({
                    "id": new_id, "from_city": from_city, "to_city": to_city, "distance_km": distance
                })
                st.success(f"Route {from_city} → {to_city} added!")
            elif from_city == to_city:
                st.error("From and To cities must be different.")
    
    with col2:
        st.subheader("Routes List")
        if st.session_state.routes:
            df_routes = pd.DataFrame(st.session_state.routes)
            st.dataframe(df_routes, use_container_width=True)
        else:
            st.info("No routes yet.")

# -------------------------------
# Trip Management
# -------------------------------
elif menu == "Trip Management":
    st.title("✈️ Trip Management")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create New Trip")
        with st.form("add_trip_form"):
            vehicle_options = {v['id']: f"{v['plate']} ({v['type']})" for v in st.session_state.vehicles if v['status'] == "Active"}
            vehicle_id = st.selectbox("Vehicle", options=list(vehicle_options.keys()), format_func=lambda x: vehicle_options[x])
            route_options = {r['id']: f"{r['from_city']} → {r['to_city']}" for r in st.session_state.routes}
            route_id = st.selectbox("Route", options=list(route_options.keys()), format_func=lambda x: route_options[x])
            # Get route details
            selected_route = next((r for r in st.session_state.routes if r['id'] == route_id), None)
            if selected_route:
                start_city = selected_route['from_city']
                end_city = selected_route['to_city']
                distance = selected_route['distance_km']
            else:
                start_city = end_city = ""
                distance = 0
            departure_datetime = st.datetime_input("Departure Time", datetime.now())
            arrival_datetime = st.datetime_input("Arrival Time", datetime.now() + timedelta(hours=4))
            price = st.number_input("Ticket Price ($)", min_value=5.0, step=5.0)
            status = st.selectbox("Trip Status", ["Scheduled", "Completed", "Cancelled"])
            total_seats = st.number_input("Total Seats", min_value=10, value=40, step=5)
            submitted = st.form_submit_button("Create Trip")
            if submitted and vehicle_id and route_id:
                new_id = f"T{len(st.session_state.trips)+1}"
                st.session_state.trips.append({
                    "id": new_id, "vehicle_id": vehicle_id, "route_id": route_id,
                    "start_city": start_city, "end_city": end_city,
                    "departure": departure_datetime.strftime("%Y-%m-%d %H:%M"),
                    "arrival": arrival_datetime.strftime("%Y-%m-%d %H:%M"),
                    "distance": distance, "price": price, "status": status,
                    "booked_seats": 0, "total_seats": total_seats
                })
                # Add to schedule
                st.session_state.schedule.append({
                    "id": f"S{len(st.session_state.schedule)+1}", "trip_id": new_id,
                    "date": departure_datetime.strftime("%Y-%m-%d"),
                    "departure_time": departure_datetime.strftime("%H:%M"),
                    "arrival_time": arrival_datetime.strftime("%H:%M")
                })
                st.success(f"Trip {start_city} → {end_city} created!")
    
    with col2:
        st.subheader("Trips List")
        if st.session_state.trips:
            trips_display = []
            for t in st.session_state.trips:
                vehicle_plate = get_vehicle_plate(t['vehicle_id'])
                trips_display.append({
                    "ID": t['id'], "Route": f"{t['start_city']}→{t['end_city']}",
                    "Departure": t['departure'], "Price": f"${t['price']}",
                    "Status": t['status'], "Vehicle": vehicle_plate
                })
            df_trips = pd.DataFrame(trips_display)
            st.dataframe(df_trips, use_container_width=True)
        else:
            st.info("No trips yet.")
    
    # Trip filter
    st.subheader("🔍 Filter Trips")
    status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Completed", "Cancelled"])
    if status_filter != "All":
        filtered = [t for t in st.session_state.trips if t['status'] == status_filter]
        if filtered:
            df_filtered = pd.DataFrame([{"ID": t['id'], "Route": f"{t['start_city']}→{t['end_city']}", "Departure": t['departure'], "Status": t['status']} for t in filtered])
            st.dataframe(df_filtered, use_container_width=True)

# -------------------------------
# Passenger & Booking
# -------------------------------
elif menu == "Passenger & Booking":
    st.title("🧑 Passenger & Booking")
    tab1, tab2 = st.tabs(["Add Passenger", "Book Trip"])
    
    with tab1:
        with st.form("add_passenger_form"):
            p_name = st.text_input("Full Name")
            p_phone = st.text_input("Phone")
            p_email = st.text_input("Email")
            submitted_p = st.form_submit_button("Add Passenger")
            if submitted_p and p_name and p_phone:
                new_id = f"P{len(st.session_state.passengers)+1}"
                st.session_state.passengers.append({
                    "id": new_id, "name": p_name, "phone": p_phone, "email": p_email
                })
                st.success(f"Passenger {p_name} added!")
        
        st.subheader("Passenger List")
        if st.session_state.passengers:
            df_pass = pd.DataFrame(st.session_state.passengers)
            st.dataframe(df_pass, use_container_width=True)
    
    with tab2:
        st.subheader("Book a Trip")
        with st.form("booking_form"):
            passenger_options = {p['id']: p['name'] for p in st.session_state.passengers}
            passenger_id = st.selectbox("Select Passenger", options=list(passenger_options.keys()), format_func=lambda x: passenger_options[x])
            # Only show scheduled trips with available seats
            available_trips = [t for t in st.session_state.trips if t['status'] == "Scheduled" and t['booked_seats'] < t['total_seats']]
            if available_trips:
                trip_options = {t['id']: f"{t['start_city']} → {t['end_city']} | {t['departure']} | ${t['price']}" for t in available_trips}
                trip_id = st.selectbox("Select Trip", options=list(trip_options.keys()), format_func=lambda x: trip_options[x])
                seat_number = st.number_input("Seat Number", min_value=1, max_value=50, step=1)
                payment_status = st.selectbox("Payment Status", ["Pending", "Paid"])
                submitted_book = st.form_submit_button("Book Now")
                if submitted_book:
                    # Check seat availability
                    selected_trip = next((t for t in st.session_state.trips if t['id'] == trip_id), None)
                    if selected_trip and seat_number <= selected_trip['total_seats']:
                        # Check if seat already booked
                        seat_taken = any(b['trip_id'] == trip_id and b['seat_number'] == seat_number for b in st.session_state.bookings)
                        if not seat_taken:
                            new_booking_id = f"B{len(st.session_state.bookings)+1}"
                            st.session_state.bookings.append({
                                "id": new_booking_id, "trip_id": trip_id, "passenger_id": passenger_id,
                                "seat_number": seat_number, "payment_status": payment_status,
                                "booking_date": datetime.now().strftime("%Y-%m-%d")
                            })
                            # Update booked seats count
                            selected_trip['booked_seats'] += 1
                            st.success(f"Booking confirmed for {passenger_options[passenger_id]} on seat {seat_number}!")
                        else:
                            st.error("Seat already taken. Choose another seat.")
                    else:
                        st.error("Invalid seat number.")
            else:
                st.warning("No scheduled trips with available seats.")
        
        st.subheader("Current Bookings")
        if st.session_state.bookings:
            bookings_display = []
            for b in st.session_state.bookings:
                passenger = next((p for p in st.session_state.passengers if p['id'] == b['passenger_id']), None)
                trip = next((t for t in st.session_state.trips if t['id'] == b['trip_id']), None)
                if passenger and trip:
                    bookings_display.append({
                        "Passenger": passenger['name'], "Trip": f"{trip['start_city']}→{trip['end_city']}",
                        "Seat": b['seat_number'], "Payment": b['payment_status'], "Date": b['booking_date']
                    })
            df_bookings = pd.DataFrame(bookings_display)
            st.dataframe(df_bookings, use_container_width=True)

# -------------------------------
# Driver Queue
# -------------------------------
elif menu == "Driver Queue":
    st.title("⏳ Driver Queue")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Add to Queue")
        driver_options = {d['id']: d['name'] for d in st.session_state.drivers}
        if driver_options:
            selected_driver = st.selectbox("Select Driver", list(driver_options.keys()), format_func=lambda x: driver_options[x])
            queue_status = st.selectbox("Status", ["Ready", "Waiting", "On Trip"])
            if st.button("Add to Queue"):
                new_pos = len(st.session_state.driver_queue) + 1
                new_id = f"Q{len(st.session_state.driver_queue)+1}"
                st.session_state.driver_queue.append({
                    "id": new_id, "driver_id": selected_driver, "position": new_pos,
                    "date": datetime.now().strftime("%Y-%m-%d"), "status": queue_status
                })
                st.success(f"Driver {driver_options[selected_driver]} added to queue.")
        else:
            st.info("No drivers available.")
    
    with col2:
        st.subheader("Driver Queue List")
        if st.session_state.driver_queue:
            queue_display = []
            for q in st.session_state.driver_queue:
                driver = next((d for d in st.session_state.drivers if d['id'] == q['driver_id']), None)
                driver_name = driver['name'] if driver else "Unknown"
                queue_display.append({
                    "Position": q['position'], "Driver": driver_name,
                    "Date": q['date'], "Status": q['status']
                })
            df_queue = pd.DataFrame(queue_display).sort_values("Position")
            st.dataframe(df_queue, use_container_width=True)
        else:
            st.info("Queue is empty.")

# -------------------------------
# Schedule
# -------------------------------
elif menu == "Schedule":
    st.title("📅 Trip Schedule")
    if st.session_state.schedule:
        schedule_display = []
        for s in st.session_state.schedule:
            trip = next((t for t in st.session_state.trips if t['id'] == s['trip_id']), None)
            if trip:
                schedule_display.append({
                    "Date": s['date'], "Departure": s['departure_time'], "Arrival": s['arrival_time'],
                    "Route": f"{trip['start_city']} → {trip['end_city']}", "Vehicle": get_vehicle_plate(trip['vehicle_id'])
                })
        df_schedule = pd.DataFrame(schedule_display).sort_values("Date")
        st.dataframe(df_schedule, use_container_width=True)
        
        # Filter by date
        filter_date = st.date_input("Filter by Date", value=None)
        if filter_date:
            filtered = df_schedule[df_schedule['Date'] == filter_date.strftime("%Y-%m-%d")]
            st.subheader(f"Trips on {filter_date}")
            st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No scheduled trips.")

# -------------------------------
# Payments
# -------------------------------
elif menu == "Payments":
    st.title("💰 Payment Management")
    if st.session_state.bookings:
        payments_data = []
        for b in st.session_state.bookings:
            passenger = next((p for p in st.session_state.passengers if p['id'] == b['passenger_id']), None)
            trip = next((t for t in st.session_state.trips if t['id'] == b['trip_id']), None)
            if passenger and trip:
                payments_data.append({
                    "Booking ID": b['id'], "Passenger": passenger['name'],
                    "Trip": f"{trip['start_city']}→{trip['end_city']}",
                    "Amount": f"${trip['price']}", "Status": b['payment_status']
                })
        df_payments = pd.DataFrame(payments_data)
        st.dataframe(df_payments, use_container_width=True)
        
        # Update payment status
        st.subheader("Update Payment Status")
        booking_options = {b['id']: f"Booking {b['id']} - {next((p['name'] for p in st.session_state.passengers if p['id'] == b['passenger_id']), 'Unknown')}" for b in st.session_state.bookings}
        if booking_options:
            selected_booking = st.selectbox("Select Booking", list(booking_options.keys()), format_func=lambda x: booking_options[x])
            new_status = st.selectbox("New Status", ["Pending", "Paid"])
            if st.button("Update Status"):
                for b in st.session_state.bookings:
                    if b['id'] == selected_booking:
                        b['payment_status'] = new_status
                        st.success(f"Payment status updated to {new_status}")
                        break
        else:
            st.info("No bookings to update.")
    else:
        st.info("No payment records yet.")

# -------------------------------
# Reviews
# -------------------------------
elif menu == "Reviews":
    st.title("⭐ Passenger Reviews")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Review")
        with st.form("add_review_form"):
            # Show completed trips for selection
            completed_trips = [t for t in st.session_state.trips if t['status'] == "Completed"]
            if completed_trips:
                trip_options = {t['id']: f"{t['start_city']} → {t['end_city']} ({t['departure']})" for t in completed_trips}
                trip_id = st.selectbox("Select Trip", options=list(trip_options.keys()), format_func=lambda x: trip_options[x])
                passenger_options = {p['id']: p['name'] for p in st.session_state.passengers}
                passenger_id = st.selectbox("Passenger Name", options=list(passenger_options.keys()), format_func=lambda x: passenger_options[x])
                rating = st.slider("Rating (1-5)", 1, 5, 5)
                comment = st.text_area("Comment")
                submitted_review = st.form_submit_button("Submit Review")
                if submitted_review:
                    new_id = f"RV{len(st.session_state.reviews)+1}"
                    st.session_state.reviews.append({
                        "id": new_id, "trip_id": trip_id, "rating": rating,
                        "comment": comment, "passenger_name": passenger_options[passenger_id]
                    })
                    st.success("Review submitted!")
            else:
                st.info("No completed trips available for review.")
    
    with col2:
        st.subheader("All Reviews")
        if st.session_state.reviews:
            reviews_display = []
            for r in st.session_state.reviews:
                trip = next((t for t in st.session_state.trips if t['id'] == r['trip_id']), None)
                route_info = f"{trip['start_city']}→{trip['end_city']}" if trip else "Unknown"
                reviews_display.append({
                    "Trip": route_info, "Passenger": r['passenger_name'],
                    "Rating": "⭐" * r['rating'], "Comment": r['comment']
                })
            df_reviews = pd.DataFrame(reviews_display)
            st.dataframe(df_reviews, use_container_width=True)
        else:
            st.info("No reviews yet.")