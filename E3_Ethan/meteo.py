import requests
import paho.mqtt.client as mqtt
import time
import sqlite3

# Configuration
BROKER_ADDRESS = "10.160.120.89"  # Adresse de ton serveur MQTT
TOPIC = "meteo_local"  # Nouveau topic
MQTT_PORT = 1883  # Port MQTT par défaut
MQTT_USER = "user"  # Ton utilisateur MQTT
MQTT_PASSWORD = "Azerty.1"  # Ton mot de passe MQTT
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
API_KEY = "9b4f6d96f5cd4a709db145328252201"  # API Key de WeatherAPI
DATABASE_PATH = "./BDD_meteo.db"  # Chemin de ta base de données

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, *extra_args):
    print("Connecté au broker avec le code de résultat " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message reçu : {msg.payload.decode()}")

# Fonction pour récupérer les données météo
def get_donnee_meteo():
    try:
        response = requests.get(WEATHER_API_URL, params={"key": API_KEY, "q": "Brest, France"})
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
    # Création de la table si elle n'existe pas
    c.execute('''CREATE TABLE IF NOT EXISTS meteo
                 (DateHeure TIMESTAMP, VitesseVent REAL, Temperature REAL, DirectionVentDegres FLOAT, DirectionVentCardinal TEXT)''')
    conn.commit()
    conn.close()

# Fonction pour insérer les données dans la base de données
def insert_into_db(data):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Insertion dans la base de données
        cursor.execute("""
            INSERT INTO meteo (DateHeure, VitesseVent, Temperature, DirectionVentDegres, DirectionVentCardinal)
            VALUES (datetime('now'), ?, ?, ?, ?)
        """, (data["wind_kph"], data["temp_c"], data["wind_degree"], data["wind_dir"]))

        conn.commit()
        conn.close()

        print("Données insérées dans la base de données avec succès.")

    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion dans la base de données: {e}")

# Fonction pour publier sur MQTT
def publish_to_mqtt(client, data):
    try:
        message = f"Vitesse du vent: {data['wind_kph']} km/h, Température: {data['temp_c']} °C, Direction du vent (degrés): {data['wind_degree']}°, Direction du vent (cardinal): {data['wind_dir']}"
        client.publish(TOPIC, message) 
        print("Données publiées sur le topic MQTT:", message)
    except Exception as e:
        print(f"Erreur lors de la publication sur MQTT: {e}")

# Fonction principale
def main():
    # Configuration de la base de données avant de commencer à insérer des données
    setup_database()
    
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)  # Ajout de l'authentification
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, MQTT_PORT, 60)
    client.loop_start()

    while True:
        donnee_meteo = get_donnee_meteo()
        if donnee_meteo:
            print("Données météo récupérées : ", donnee_meteo)

            # Insérer dans la base de données
            insert_into_db(donnee_meteo["current"])

            # Publier sur MQTT
            publish_to_mqtt(client, donnee_meteo["current"])

        time.sleep(900)  # Attendre 15 minutes avant la prochaine récupération

if __name__ == "__main__":
    main()