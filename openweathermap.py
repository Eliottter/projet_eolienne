import requests
import paho.mqtt.client as mqtt
import time
import sqlite3

# Configuration
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "weather/data"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
API_KEY = "94df689b87c4a001afc9562d1bfb2888"  # Votre clé API OpenWeatherMap
WEB_SERVER_URL = "http://10.160.120.89"  # Adresse de notre serveur web

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, *extra_args):
    print("Connexion au broker réussie")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message reçu : {msg.payload.decode()}")
    send_to_web_server(msg.payload.decode())

# Fonction pour récupérer les données météorologiques
def get_weather_data(lat, lon):
    try:
        # Faire une requête à l'API OpenWeatherMap avec les coordonnées lat, lon
        url = WEATHER_API_URL.format(lat=lat, lon=lon, API_KEY=API_KEY)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Échec de la récupération des données météorologiques. Code d'erreur: {response.status_code}")
            print("Réponse de l'API:", response.text)  # Afficher la réponse complète de l'API
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données météorologiques: {e}")
        return None

# Fonction pour envoyer les données à un serveur web
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
    conn = sqlite3.connect('meteo_test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather
                 (timestamp TEXT, wind_speed REAL, temperature REAL, is_raining INTEGER)''')
    conn.commit()
    conn.close()

# Fonction pour insérer les données météorologiques dans la base de données
def insert_weather_data(wind_speed, temperature, is_raining):
    conn = sqlite3.connect('meteo_test.db')
    c = conn.cursor()
    c.execute("INSERT INTO weather (timestamp, wind_speed, temperature, is_raining) VALUES (datetime('now'), ?, ?, ?)",
              (wind_speed, temperature, is_raining))
    conn.commit()
    conn.close()

# Initialisation de la base de données
setup_database()

# Fonction principale
def main():
    # Initialisation du client MQTT
    client = mqtt.Client(protocol=mqtt.MQTTv5)  # Utilisation de la dernière version MQTT
    client.on_connect = on_connect
    client.on_message = on_message

    # Connexion au broker MQTT
    client.connect(BROKER_ADDRESS, 1883, 60)

    # Démarrer la boucle MQTT
    client.loop_start()

    # Coordonnées de Brest (latitude et longitude)
    lat = 48.3904
    lon = -4.4861

    while True:
        # Récupération des données météorologiques
        weather_data = get_weather_data(lat, lon)
        if weather_data:
            print("Données météo récupérées : ", weather_data)  # Afficher les données météo récupérées
            # Extraction des données qui nous intéressent
            wind_speed = weather_data["wind"]["speed"]  # Vitesse du vent (en m/s)
            temperature = weather_data["main"]["temp"]  # Température (en °C)
            is_raining = 1 if "rain" in weather_data else 0  # Vérifier s'il pleut
            
            # Insérer les données dans la base de données
            insert_weather_data(wind_speed, temperature, is_raining)
            
            # Publier les données sur le topic MQTT
            client.publish(TOPIC, str(weather_data))
        
        time.sleep(60)

if __name__ == "__main__":
    main()
