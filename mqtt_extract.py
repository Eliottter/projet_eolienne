import paho.mqtt.client as mqtt

# Configuration MQTT
BROKER_ADDRESS = "10.160.120.89"
MQTT_PORT = 1883
MQTT_USER = "user"
MQTT_PASSWORD = "Azerty.1"
TOPIC = "meteo_local"

# Callback lors de la connexion
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT !")
        client.subscribe(TOPIC)
    else:
        print("Échec de la connexion, code de retour :", rc)

# Callback lors de la réception d’un message
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print("Message brut :", message)

    try:
        # Exemple de parsing basique (à adapter selon le format exact de tes messages)
        parts = message.split(',')
        for part in parts:
            print(part.strip())
    except Exception as e:
        print("Erreur lors du parsing :", e)


# Fonction principale
def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    # Connexion au broker
    client.connect(BROKER_ADDRESS, MQTT_PORT, 60)

    # Boucle infinie pour écouter les messages
    client.loop_forever()

if __name__ == "__main__":
    main()
