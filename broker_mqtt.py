import paho.mqtt.client as mqtt

# Configuration du broker
BROKER_ADDRESS = "localhost"
PORT = 1883

# Création de la liste des topics
TOPICS = ["/meteo", "/temp_incli", "/user2"]

# Callback lors de la connexion au broker
def on_connect(client, userdata, flags, rc, *extra_args):
    if rc == 0:
        print("Broker MQTT connecté avec succès")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"Abonné au topic : {topic}")
    else:
        print(f"Échec de la connexion au broker, code d'erreur : {rc}")

# Callback lors de la réception d'un message
def on_message(client, userdata, msg):
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")

# Initialisation du broker MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker
client.connect(BROKER_ADDRESS, PORT, 60)

# Boucle d'attente des messages
client.loop_forever()