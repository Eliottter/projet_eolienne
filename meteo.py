import requests
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion  # Ajout demandé
import time
import sqlite3

# Configuration
BROKER_ADDRESS = "localhost"  # Adresse du serveur MQTT
TOPIC = "meteo_local"
MQTT_PORT = 8883  # Port TLS sécurisé
MQTT_USER = "user"
MQTT_PASSWORD = "Azerty.1"
VILLE = "Brest, France"
WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key=9b4f6d96f5cd4a709db145328252201&q={VILLE}"
API_KEY = "9b4f6d96f5cd4a709db145328252201"
DATABASE_PATH = "./BDD_meteo.db"

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, *extra_args):
    print("Connecté au broker avec le code de résultat " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message reçu : {msg.payload.decode()}")

# Fonction pour récupérer les données météo
def get_donnee_meteo():
    try:
        response = requests.get(WEATHER_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Échec de la récupération des données météorologiques. Code d'erreur: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données météorologiques: {e}")
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
        print("Données insérées dans la base de données avec succès.")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion dans la base de données: {e}")

# Publication sur MQTT
def publish_to_mqtt(client, data):
    try:
        message = f"Vitesse du vent: {data['wind_kph']} km/h, Température: {data['temp_c']} °C, Direction du vent (degrés): {data['wind_degree']}°, Direction du vent (cardinal): {data['wind_dir']}"
        client.publish(TOPIC, message)
        print("Données publiées sur le topic MQTT:", message)
    except Exception as e:
        print(f"Erreur lors de la publication sur MQTT: {e}")

def main():
    setup_database()

    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    # TLS activé
    client.tls_set(ca_certs="/etc/mosquitto/certs/server.crt")
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, MQTT_PORT, 60)
    client.loop_start()

    while True:
        donnee_meteo = get_donnee_meteo()
        if donnee_meteo:
            print("Données météo récupérées : ", donnee_meteo)

            insert_into_db(donnee_meteo["current"])
            publish_to_mqtt(client, donnee_meteo["current"])

        time.sleep(900)  # Attendre 15 minutes

if __name__ == "__main__":
    main()
