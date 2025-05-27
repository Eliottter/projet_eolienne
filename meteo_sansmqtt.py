import requests
import time
import sqlite3

# Configuration
VILLE = "Brest, France"
WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key=9b4f6d96f5cd4a709db145328252201&q={VILLE}"
DATABASE_PATH = "./BDD_meteo.db"

# Fonction pour récupérer les données météo
def get_donnee_meteo():
    try:
        response = requests.get(WEATHER_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Échec récupération météo : Code {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur récupération météo : {e}")
        return None

# Configuration de la base de données
def setup_database():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS meteo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    DateHeure TIMESTAMP,
                    VitesseVent REAL,
                    Temperature REAL,
                    DirectionVentDegres FLOAT,
                    DirectionVentCardinal TEXT
                )''')
    conn.commit()
    conn.close()

# Insertion dans la base
def insert_into_db(data):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meteo (DateHeure, VitesseVent, Temperature, DirectionVentDegres, DirectionVentCardinal)
            VALUES (datetime('now'), ?, ?, ?, ?)
        """, (data["wind_kph"], data["temp_c"], data["wind_degree"], data["wind_dir"]))
        conn.commit()
        conn.close()
        print(f"Vitesse du vent : {data['wind_kph']} km/h, Température : {data['temp_c']} °C, Direction : {data['wind_degree']}° ({data['wind_dir']})")
    except sqlite3.Error as e:
        print(f"❌ Erreur insertion BDD : {e}")

# Programme principal
def main():
    setup_database()

    while True:
        donnee_meteo = get_donnee_meteo()
        if donnee_meteo:
            print("🌤️ Données météo récupérées : ", donnee_meteo["current"])
            insert_into_db(donnee_meteo["current"])

        time.sleep(900)  # Pause de 15 minutes

if __name__ == "__main__":
    main()
