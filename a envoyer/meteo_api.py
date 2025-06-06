from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def fetch_latest_weather_data():
    try:
        conn = sqlite3.connect('/home/btsciel2a/Documents/projet-ethan/E3_Ethan/BDD_meteo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DateHeure, VitesseVent, Temperature, DirectionVent, DirectionVent1 FROM meteo ORDER BY DateHeure DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "DateHeure": row[0],
                "VitesseVent": row[1],
                "Temperature": row[2],
                "DirectionVent": row[3],
                "DirectionVent1": row[4]
            }
        else:
            return {"error": "Aucune donnée disponible"}
    except Exception as e:
        return {"error": f"Erreur lors de la récupération des données météorologiques: {e}"}

@app.route('/weather', methods=['GET'])
def get_weather():
    data = fetch_latest_weather_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
