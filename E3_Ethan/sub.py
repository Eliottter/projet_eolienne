import paho.mqtt.client as mqtt

# Configuration
BROKER_ADDRESS = "10.160.120.89"  # Adresse du serveur MQTT
TOPIC = "meteo_local"  # Topic auquel nous nous abonnons
MQTT_PORT = 1883  # Port par défaut du broker MQTT
MQTT_USER = "user"  # Utilisateur MQTT
MQTT_PASSWORD = "Azerty.1"  # Mot de passe MQTT

# Callback qui s'exécute lors de la connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker avec le code de résultat {rc}")
    client.subscribe(TOPIC)  # S'abonne au topic 'meteo_local'

# Callback qui s'exécute lors de la réception d'un message sur un topic
def on_message(client, userdata, msg):
    print(f"Message reçu sur le topic {msg.topic}: {msg.payload.decode()}")  # Affiche le message reçu

# Initialisation du client MQTT
client = mqtt.Client()

# Configuration de l'utilisateur et mot de passe pour l'authentification
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Assignation des callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker MQTT
client.connect(BROKER_ADDRESS, MQTT_PORT, 60)

# Démarre la boucle de réception des messages
client.loop_forever()  # Cette fonction va écouter en permanence et gérer les messages entrants