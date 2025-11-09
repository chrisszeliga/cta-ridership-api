from flask_restx import abort
import sqlite3

DATABASE = "file:CTA2_L_daily_ridership.db?mode=ro" # read only


################################################################################# 
#
# get_stats
#
# Retrieves general CTA ridership statistics from the database
# Returns a dictionary containing total stations, total stops, total ridership, and date range
#
def get_stats():
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    # Retrieve the total rows in stations (total number of stations)
    cursor.execute("SELECT count(*) FROM Stations;")
    total_stations = cursor.fetchone()[0]

    # Retrieve the total rows in Stops (total number of stops)
    cursor.execute("SELECT count(*) FROM Stops;")
    total_stops = cursor.fetchone()[0]

    # Retrieve the total rows in Ridership (total number of ride enteries)
    cursor.execute("SELECT count(*) FROM Ridership;")
    total_entries = cursor.fetchone()[0]

    # Retrieve the row of the minimum formatted date and row of the maximum formatted date
    cursor.execute("""
        SELECT MIN(strftime('%Y-%m-%d', Ride_Date)), 
               MAX(strftime('%Y-%m-%d', Ride_Date)) 
        FROM Ridership;
    """)
    min_date, max_date = cursor.fetchone()

    # Retrieve the sum of Num_Riders in all rows (total ridership)
    cursor.execute("SELECT SUM(Num_Riders) FROM Ridership;")
    total_ridership = cursor.fetchone()[0]
    db.close()

    return {
        "total_stations": total_stations,
        "total_stops": total_stops,
        "total_entries": total_entries,
        "date_range": {
            "min": min_date,
            "max": max_date
        },
        "total_ridership": total_ridership
    }

################################################################################# 
#
# get_stations
#
# Retrieves all station ids and names that match the requested station name
#
def get_stations(station_name):
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    station_name_wildcard = f"%{station_name}%"

    sql = """
            SELECT Station_ID, Station_Name FROM Stations
            WHERE Station_Name LIKE ?
            ORDER BY Station_Name ASC;
          """
    cursor.execute(sql, [station_name_wildcard])
    result = cursor.fetchall()
    db.close()

    if not result:
        abort(404, f"'{station_name}' not found")

    # Convert each row to a dictionary
    stations = [{"station_id": row[0], "station_name": row[1]} for row in result]

    return {"stations": stations}


################################################################################# 
#
# get_ridership_breakdown
#
# Retrieves total ridership and percentage of riders on a weekday,
# Saturday and Sunday/holiday for the inputted station
#
def get_ridership_breakdown(station_name):
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    sql = """
            SELECT (
              SELECT SUM(Num_Riders) FROM Ridership
              WHERE Type_of_Day = 'W'
                AND Ridership.Station_ID = Stations.Station_ID
            ) AS weekday_riders, (
              SELECT SUM(Num_Riders) FROM Ridership
              WHERE Type_of_Day = 'A' 
                AND Ridership.Station_ID = Stations.Station_ID
            ) AS saturday_riders, (
              SELECT SUM(Num_Riders) FROM Ridership
              WHERE Type_of_Day = 'U' 
                AND Ridership.Station_ID = Stations.Station_ID
            ) AS sunday_riders, 
            SUM(Num_Riders) as total_riders
            FROM Ridership JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
            WHERE Station_Name = ?;
          """
    cursor.execute(sql, [station_name])
    rider_data = cursor.fetchone()
    db.close()

    # If no data found, abort with 404
    if not rider_data or rider_data[0] is None:
        abort(404, f"No ridership data found for station '{station_name}'")

    weekday_riders = rider_data[0]
    weekday_pct = f"{(rider_data[0] / rider_data[3]) * 100:.2f}%"
    saturday_riders = rider_data[1]
    saturday_pct = f"{(rider_data[1] / rider_data[3]) * 100:.2f}%"
    sunday_riders = rider_data[2]
    sunday_pct = f"{(rider_data[2] / rider_data[3]) * 100:.2f}%"
    total_riders = rider_data[3]

    return {
        "station": station_name,
        "weekday_riders": weekday_riders,
        "weekday_pct": weekday_pct,
        "saturday_riders": saturday_riders,
        "saturday_pct": saturday_pct,
        "sunday_riders": sunday_riders,
        "sunday_pct": sunday_pct,
        "total_riders": total_riders
    }


################################################################################# 
#
# get_weekday_ridership
#
# Retrieves the total ridership and percentage of riders on weekdays for each station
#
def get_weekday_ridership():
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    # Total riders on weekdays
    cursor.execute("""
        SELECT SUM(Num_Riders) FROM Ridership
        WHERE Type_of_Day = 'W';
    """)
    total_riders = cursor.fetchone()[0]

    # Ridership per station on weekdays
    cursor.execute("""
        SELECT Station_Name, SUM(Num_Riders)
        FROM Ridership JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
        WHERE Type_of_Day = 'W'
        GROUP BY Station_Name
        ORDER BY SUM(Num_Riders) DESC;
    """)
    rider_data = cursor.fetchall()
    db.close()

    # Convert to list of dicts with percentages
    result = []
    for row in rider_data:
        station_name = row[0]
        station_riders = row[1]
        pct = (station_riders / total_riders) * 100 if total_riders else 0
        result.append({
            "station_name": station_name,
            "weekday_riders": station_riders,
            "percentage": f"{pct:.2f}%"
        })

    return {"total_weekday_riders": total_riders, "stations": result}


################################################################################# 
#
# get_stops_stats
#
# Retrieves the number of stops, and percentage of stops, 
# for each combination of line color and direction. 
#
def get_stops_stats():
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    # Get total number of stops
    cursor.execute("SELECT COUNT(*) FROM Stops")
    total_stops = cursor.fetchone()[0]

    # Query for stops grouped by line color and direction
    sql = """
        SELECT Color, Direction, COUNT(*)
        FROM Stops
        JOIN StopDetails ON StopDetails.Stop_ID = Stops.Stop_ID
        JOIN Lines ON Lines.Line_ID = StopDetails.Line_ID
        GROUP BY Color, Direction
        ORDER BY Color ASC;
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()

    # Convert results into list of dictionaries
    stops_data = []
    for row in results:
        stops_data.append({
            "color": row[0],
            "direction": row[1],
            "num_stops": row[2],
            "percent_of_total": round((row[2] / total_stops) * 100, 2)
        })

    return {"stops": stops_data}


################################################################################# 
#
# get_stops_by_line_and_direction
#
# Retrieves all stops for an inputted line color and direction
#
def get_stops_by_line_and_direction(line_color, direction):
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    # Capitalize the line color (handles things like 'pink-red' -> 'Pink-Red')
    line_color = line_color.title()
    direction = direction.upper()

    # First check if the line color exists at all
    cursor.execute("""
        SELECT Stop_ID FROM StopDetails 
        JOIN Lines ON Lines.Line_ID = StopDetails.Line_ID
        WHERE Color = ?;
    """, [line_color])
    line_color_result = cursor.fetchall()

    if not line_color_result:
        db.close()
        abort(404, f"Line color '{line_color}' not found")

    # Retrieve stops with the specified color and direction
    cursor.execute("""
        SELECT Stop_Name, Direction, ADA FROM Stops
        JOIN StopDetails ON StopDetails.Stop_ID = Stops.Stop_ID
        JOIN Lines ON Lines.Line_ID = StopDetails.Line_ID
        WHERE Color = ? AND Direction = ?
        ORDER BY Stop_Name ASC;
    """, [line_color, direction])
    stops = cursor.fetchall()
    db.close()

    if not stops:
        abort(404, f"Line '{line_color}' does not run in direction '{direction}'")

    # Format each stop into a dictionary
    stops_list = [
        {
            "stop_name": row[0],
            "direction": row[1],
            "ada": bool(row[2])
        }
        for row in stops
    ]

    return {"line_color": line_color, "direction": direction, "stops": stops_list}


################################################################################# 
#
# get_yearly_ridership
#
# Retrieves ridership of each year for the inputted station
#
def get_yearly_ridership(station_name):
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    sql = """
        SELECT strftime('%Y', Ride_Date) AS year, SUM(Num_Riders) FROM Ridership 
        JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
        WHERE Station_Name = ?
        GROUP BY year
        ORDER BY year ASC;
    """

    cursor.execute(sql, [station_name])
    yearly_data = cursor.fetchall()
    db.close()

    # If no data found, abort with 404
    if not yearly_data:
        abort(404, f"No ridership data found for station '{station_name}'")

    result = [
        {"year": row[0], "total_riders": row[1]}
        for row in yearly_data
    ]
    return {
        "station": station_name,
        "yearly_ridership": result
    }


################################################################################# 
#
# get_monthly_ridership
#
# Retrieves the total ridership of each month for the inputted station and year
#
def get_monthly_ridership(station_name, year):

    if year < 2001 or year > 2021:
        return {"error": "Year must be between 2001 and 2021"}, 400
    year = str(year)

    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    sql = """
        SELECT strftime('%m', Ride_Date) AS Month, SUM(Num_Riders) FROM Ridership 
        JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
        WHERE Station_Name = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Month
        ORDER BY Month ASC;
    """
    cursor.execute(sql, [station_name, year])
    monthly_data = cursor.fetchall()
    db.close()
    
    # If no data found, abort with 404
    if not monthly_data:
        abort(404, f"No ridership data found for station '{station_name}' year '{year}'")

    result = [
        {"month": row[0], "total_riders": f"{row[1]:,}"}
        for row in monthly_data
    ]
    return {
        "station": station_name,
        "year": year,
        "monthly_ridership": result
    }


#################################################################################
#
# get_stations_nearby
#
# Retrieves all stations in a mile square radius for the inputted latitude and longitude
#
def get_stations_nearby(lat: float, lon: float):
    # Validate Latitude and Longitude
    if not (40 <= lat <= 43):
        return {"error": "Latitude must be between 40 and 43"}, 400
    
    if not (-88 <= lon <= -87):
        return {"error": "Longitude must be between -88 and -87"}, 400
    
    db = sqlite3.connect(DATABASE, uri=True)
    cursor = db.cursor()

    # Latitude: Each degree = 69 miles
    # longitude: Each degree = 51 miles
    # Calculate square mile radius bounds
    max_lat = round(lat + (1 / 69), 3)
    min_lat = round(lat - (1 / 69), 3)
    max_lon = round(lon + (1 / 51), 3)
    min_lon = round(lon - (1 / 51), 3)

    sql = """
        SELECT DISTINCT Station_Name, Latitude, Longitude
        FROM Stations
        JOIN Stops ON Stops.Station_ID = Stations.Station_ID
        WHERE Latitude BETWEEN ? AND ?
        AND Longitude BETWEEN ? AND ?
        ORDER BY Station_Name;
    """

    cursor.execute(sql, [min_lat, max_lat, min_lon, max_lon])
    stations = cursor.fetchall()
    db.close()

    if not stations:
        return {"stations": []}

    result = [
        {"station_name": row[0], "latitude": row[1], "longitude": row[2]}
        for row in stations
    ]
    return {"stations": result}

