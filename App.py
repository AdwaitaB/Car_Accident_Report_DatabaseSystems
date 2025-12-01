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
    # support several filtering query parameters from the UI
    year = request.args.get("year")
    min_fatalities = request.args.get("min_fatalities")
    max_fatalities = request.args.get("max_fatalities")
    min_crashes = request.args.get("min_crashes")
    max_crashes = request.args.get("max_crashes")
    min_fatality_rate = request.args.get("min_fatality_rate")
    max_fatality_rate = request.args.get("max_fatality_rate")

    query = "SELECT * FROM NHTSA_NATIONAL_STATS WHERE 1=1"
    params = []

    if year:
        query += " AND year = %s"
        params.append(year)

    if min_fatalities:
        query += " AND total_fatalities >= %s"
        params.append(min_fatalities)

    if max_fatalities:
        query += " AND total_fatalities <= %s"
        params.append(max_fatalities)

    if min_crashes:
        query += " AND fatal_crashes >= %s"
        params.append(min_crashes)

    if max_crashes:
        query += " AND fatal_crashes <= %s"
        params.append(max_crashes)

    if min_fatality_rate:
        query += " AND (fatality_rate_per_100k_pop + 0) >= %s"
        params.append(min_fatality_rate)

    if max_fatality_rate:
        query += " AND (fatality_rate_per_100k_pop + 0) <= %s"
        params.append(max_fatality_rate)

    query += " ORDER BY year DESC"

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert Decimal objects to native types for JSON serialization
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
# FORECASTING (simple linear trend)
# -------------------------
@app.route("/forecast", methods=["GET"])
def forecast_accidents():
    # simple linear regression on historical year -> total_fatalities
    years_ahead = int(request.args.get('years', 5))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT year, total_fatalities FROM NHTSA_NATIONAL_STATS ORDER BY year ASC")
        rows = cursor.fetchall()

        if not rows or len(rows) < 2:
            return jsonify({"error": "Not enough historical data to forecast"}), 400

        xs = [float(r['year']) for r in rows]
        ys = [float(r['total_fatalities']) for r in rows]

        n = len(xs)
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n

        num = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
        den = sum((xs[i] - x_mean) ** 2 for i in range(n))
        if den == 0:
            slope = 0.0
        else:
            slope = num / den
        intercept = y_mean - slope * x_mean

        last_year = int(xs[-1])
        forecast = []
        for i in range(1, years_ahead + 1):
            y_pred = intercept + slope * (last_year + i)
            forecast.append({"year": last_year + i, "predicted_fatalities": round(y_pred, 2)})

        return jsonify({"history_points": len(rows), "slope": slope, "intercept": intercept, "forecast": forecast})

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# -------------------------
# SIMULATION / WHAT-IF
# -------------------------
@app.route("/simulate", methods=["POST"])
def simulate_policy():
    # Accepts percentage adjustments and returns projected fatalities using latest year baseline
    data = request.json or {}
    # percent changes (can be negative). Example: {"fatality_rate_pct": -5, "population_pct": 1.2}
    fatality_rate_pct = float(data.get('fatality_rate_pct', 0))
    population_pct = float(data.get('population_pct', 0))
    # optional multipliers for VMT/drivers could be used in more complex models
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM NHTSA_NATIONAL_STATS ORDER BY year DESC LIMIT 1")
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "No baseline data available"}), 400

        baseline = {
            'year': int(row.get('year')),
            'total_fatalities': float(row.get('total_fatalities') or 0),
            'fatality_rate_per_100k_pop': float(row.get('fatality_rate_per_100k_pop') or 0),
            'resident_population': float(row.get('resident_population') or 0)
        }

        # apply percentage changes
        new_pop = baseline['resident_population'] * (1 + population_pct/100)
        new_rate = baseline['fatality_rate_per_100k_pop'] * (1 + fatality_rate_pct/100)

        # projected fatalities = rate_per_100k * (population / 100k)
        projected_fatalities = new_rate * (new_pop / 100000.0)

        return jsonify({
            "baseline": baseline,
            "scenario": {"fatality_rate_pct": fatality_rate_pct, "population_pct": population_pct},
            "projected_fatalities": round(projected_fatalities, 2),
            "delta": round(projected_fatalities - baseline['total_fatalities'], 2),
            "percent_change": round(((projected_fatalities / baseline['total_fatalities'] - 1) * 100) if baseline['total_fatalities'] else 0, 2)
        })

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

        # Basic validation: year is required
        year_val = int(data.get("year", 0))
        if year_val <= 0:
            return jsonify({"error": "Invalid or missing 'year' field"}), 400

        # If a record for this year already exists, return 409 Conflict
        cursor.execute("SELECT stat_id FROM NHTSA_NATIONAL_STATS WHERE year = %s", (year_val,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": f"Record for year {year_val} already exists", "stat_id": existing[0]}), 409

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
            year_val,
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
# DELETE A NATIONAL STATISTIC
# -------------------------
@app.route("/accidents/<int:stat_id>", methods=["DELETE"])
def delete_accident(stat_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify record exists
        cursor.execute("SELECT stat_id FROM NHTSA_NATIONAL_STATS WHERE stat_id = %s", (stat_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": f"Record with id {stat_id} not found"}), 404

        # Delete the record
        cursor.execute("DELETE FROM NHTSA_NATIONAL_STATS WHERE stat_id = %s", (stat_id,))
        conn.commit()

        return jsonify({"success": True, "deleted_id": stat_id}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# -------------------------
# GET single national statistic
# -------------------------
@app.route("/accidents/<int:stat_id>", methods=["GET"])
def get_accident(stat_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM NHTSA_NATIONAL_STATS WHERE stat_id = %s", (stat_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": f"Record with id {stat_id} not found"}), 404

        # Convert Decimal objects to floats where applicable
        for key, value in row.items():
            if hasattr(value, '__float__'):
                row[key] = float(value)

        return jsonify(row)

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# -------------------------
# UPDATE national statistic
# -------------------------
@app.route("/accidents/<int:stat_id>", methods=["PUT"])
def update_accident(stat_id):
    data = request.json or {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check the record exists
        cursor.execute("SELECT stat_id, year FROM NHTSA_NATIONAL_STATS WHERE stat_id = %s", (stat_id,))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"error": f"Record with id {stat_id} not found"}), 404

        # If year is being changed, ensure no other record uses the same year
        if 'year' in data:
            try:
                year_val = int(data.get('year', 0))
            except Exception:
                return jsonify({"error": "Invalid 'year' value"}), 400

            cursor.execute("SELECT stat_id FROM NHTSA_NATIONAL_STATS WHERE year = %s AND stat_id <> %s", (year_val, stat_id))
            conflict = cursor.fetchone()
            if conflict:
                return jsonify({"error": f"Another record already uses year {year_val}"}), 409

        # Prepare update fields - only update allowed columns
        allowed = [
            'year','total_fatalities','drivers_killed','passengers_killed',
            'motorcyclists_killed','pedalcyclists_killed','pedestrians_killed',
            'nonmotorists_total','other_nonmotorists_killed','unknown_occupants',
            'fatal_crashes','vehicle_occupants_total','registered_vehicles',
            'licensed_drivers','resident_population','vehicle_miles_traveled',
            'fatality_rate_per_100k_pop','fatality_rate_per_100k_drivers',
            'fatality_rate_per_100k_vehicles','fatality_rate_per_100m_vmt'
        ]

        set_clauses = []
        params = []
        for col in allowed:
            if col in data:
                set_clauses.append(f"{col} = %s")
                # coerce types where sensible
                if col in ('year','total_fatalities','drivers_killed','passengers_killed','motorcyclists_killed','pedalcyclists_killed','pedestrians_killed','nonmotorists_total','other_nonmotorists_killed','unknown_occupants','fatal_crashes','vehicle_occupants_total','registered_vehicles','licensed_drivers','resident_population'):
                    try:
                        params.append(int(data.get(col) or 0))
                    except Exception:
                        params.append(0)
                else:
                    try:
                        params.append(float(data.get(col) or 0))
                    except Exception:
                        params.append(0.0)

        if not set_clauses:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.append(stat_id)
        update_query = f"UPDATE NHTSA_NATIONAL_STATS SET {', '.join(set_clauses)} WHERE stat_id = %s"
        cursor.execute(update_query, tuple(params))
        conn.commit()

        return jsonify({"success": True, "updated_id": stat_id}), 200

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

