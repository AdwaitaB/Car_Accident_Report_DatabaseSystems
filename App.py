from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Tanuska@2004",
        database="Accidents_Database"
    )

# -------------------------
# SERVE DASHBOARD
# -------------------------
@app.route("/")
def dashboard():
    return send_from_directory('static', 'index.html')

# -------------------------
# GET all accident statistics
# -------------------------
@app.route("/accidents", methods=["GET"])
def get_accidents():
    year = request.args.get("year")
    
    query = "SELECT * FROM NHTSA_NATIONAL_STATS WHERE 1=1"
    params = []
    
    if year:
        query += " AND year = %s"
        params.append(year)
    
    query += " ORDER BY year DESC"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert Decimal objects to strings for JSON serialization
        for row in rows:
            for key, value in row.items():
                if hasattr(value, '__float__'):
                    row[key] = float(value)
        
        return jsonify(rows)
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------
# ADD NATIONAL STATISTIC (from form)
# -------------------------
@app.route("/accidents/form", methods=["POST"])
def add_accident_from_form():
    data = request.json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert new national statistics record
        query = """
            INSERT INTO NHTSA_NATIONAL_STATS 
            (year, total_fatalities, drivers_killed, passengers_killed, 
             motorcyclists_killed, pedalcyclists_killed, pedestrians_killed, 
             nonmotorists_total, other_nonmotorists_killed, unknown_occupants,
             fatal_crashes, vehicle_occupants_total, registered_vehicles, 
             licensed_drivers, resident_population, vehicle_miles_traveled,
             fatality_rate_per_100k_pop, fatality_rate_per_100k_drivers, 
             fatality_rate_per_100k_vehicles, fatality_rate_per_100m_vmt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            int(data.get("year", 0)),
            int(data.get("total_fatalities", 0)),
            int(data.get("drivers_killed", 0)),
            int(data.get("passengers_killed", 0)),
            int(data.get("motorcyclists_killed", 0)),
            int(data.get("pedalcyclists_killed", 0)),
            int(data.get("pedestrians_killed", 0)),
            int(data.get("nonmotorists_total", 0)),
            int(data.get("other_nonmotorists_killed", 0)),
            int(data.get("unknown_occupants", 0)),
            int(data.get("fatal_crashes", 0)),
            int(data.get("vehicle_occupants_total", 0)),
            int(data.get("registered_vehicles", 0)),
            int(data.get("licensed_drivers", 0)),
            int(data.get("resident_population", 0)),
            float(data.get("vehicle_miles_traveled", 0)),
            float(data.get("fatality_rate_per_100k_pop", 0)),
            float(data.get("fatality_rate_per_100k_drivers", 0)),
            float(data.get("fatality_rate_per_100k_vehicles", 0)),
            float(data.get("fatality_rate_per_100m_vmt", 0))
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        new_id = cursor.lastrowid
        
        return jsonify({
            "id": new_id,
            "success": True,
            "message": "National statistic record added successfully"
        }), 201
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------
# GET YEARLY TRENDS
# -------------------------
@app.route("/trends/yearly", methods=["GET"])
def yearly_trends():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT year, total_fatalities as fatalities, fatal_crashes as crashes
            FROM NHTSA_NATIONAL_STATS
            ORDER BY year ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        years = [row['year'] for row in rows]
        counts = [row['crashes'] for row in rows]
        
        return jsonify({
            "years": years,
            "counts": counts
        })
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# -------------------------
# GET STATISTICS SUMMARY
# -------------------------
@app.route("/statistics/factors", methods=["GET"])
def statistics_by_factors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get top years by fatalities
        query = """
            SELECT year, total_fatalities, fatal_crashes, 
                   fatality_rate_per_100k_pop, fatality_rate_per_100m_vmt
            FROM NHTSA_NATIONAL_STATS
            ORDER BY total_fatalities DESC
            LIMIT 10
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert Decimal to float for JSON
        for row in rows:
            for key, value in row.items():
                if hasattr(value, '__float__'):
                    row[key] = float(value)
        
        return jsonify(rows)
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)

