import requests
import paho.mqtt.client as mqtt
import time
import sqlite3

# Configuration
BROKER_ADDRESS = "10.160.120.89"  # Adresse de ton serveur MQTT
TOPIC = "meteo_local"  # Nouveau topic
MQTT_PORT = 1883  # Port MQTT par défaut
MQTT_USER = "user"  # Ton utilisateur MQTT
MQTT_PASSWORD = "ton_mot_de_passe"  # Ton mot de passe MQTT
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
API_KEY = "9b4f6d96f5cd4a709db145328252201"  # API Key de WeatherAPI
WEB_SERVER_URL = "http://10.160.120.89"  # Adresse de ton serveur web

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, *extra_args):
    print("Connecté au broker avec le code de résultat " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message reçu : {msg.payload.decode()}")
    send_to_web_server(msg.payload.decode())

# Fonction pour récupérer les données météorologiques
def get_donnee_meteo():
    try:
        response = requests.get(WEATHER_API_URL, params={"key": API_KEY, "q": "Portland"})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Échec de la récupération des données météorologiques. Code d'erreur: {response.status_code}")
            print("Réponse de l'API:", response.text)
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données météorologiques: {e}")
        return None

# Fonction pour envoyer les données au serveur web
def send_to_web_server(data):
    try:
        response = requests.post(WEB_SERVER_URL, json={"weather_data": data})
        if response.status_code == 200:
            print("Données envoyées au serveur web avec succès")
        else:
            print(f"Échec de l'envoi des données au serveur web. Code d'erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur lors de l'envoi des données au serveur web: {e}")


# Configuration de la base de données
def setup_database():
    conn = sqlite3.connect('/var/www/html/BDD_meteo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS meteo
                 (DateHeure TIMESTAMP, VitesseVent REAL, Temperature REAL, DirectionVent FLOAT, DirectionVent1 FLOAT)''')
    conn.commit()
    conn.close()

def insert_donnee_meteo(vitesseVent, temperature, DirectionVent, DirectionVent1):
    conn = sqlite3.connect('/var/www/html/BDD_meteo.db')
    c = conn.cursor()
    c.execute("INSERT INTO meteo (DateHeure, VitesseVent, Temperature, DirectionVent, DirectionVent1) VALUES (datetime('now'), ?, ?, ?, ?)",
          (vitesseVent, temperature, DirectionVent, DirectionVent1))
    conn.commit()
    conn.close()

# Initialisation de la base de données
setup_database()

# Fonction principale
def main():
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)  # Ajout de l'authentification
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, MQTT_PORT, 60)
    client.loop_start()

    while True:
        donnee_meteo = get_donnee_meteo()
        if donnee_meteo:
            print("Données météo récupérées : ", donnee_meteo)
            vitesseVent = donnee_meteo["current"]["wind_kph"]
            temperature = donnee_meteo["current"]["temp_c"]
            DirectionVent = donnee_meteo["current"]["wind_degree"] 
            DirectionVent1 = donnee_meteo["current"]["wind_dir"] 
            insert_donnee_meteo(vitesseVent, temperature, DirectionVent, DirectionVent1)
            client.publish(TOPIC, str(donnee_meteo))
        time.sleep(600)

if __name__ == "__main__":
    main()