import paho.mqtt.client as mqtt
import sqlite3
import time

# Configuration
BROKER_ADDRESS = "10.160.120.89"  # Adresse du serveur MQTT
TOPIC = "capteur_present"  # Nouveau topic
MQTT_PORT = 1883  # Port MQTT par défaut
MQTT_USER = "user"  # Ton utilisateur MQTT
MQTT_PASSWORD = "Azerty.1"  # Ton mot de passe MQTT
DATABASE_PATH = "/var/www/html/BDD_capteur_present.db"  # Chemin de la base de données


# MQTT Callbacks
def on_connect(client, userdata, flags, rc, *extra_args):
    print("Connecté au broker avec le code de résultat " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message reçu : {msg.payload.decode()}")


# Configuration de la base de données
def setup_database():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    # Création de la table si elle n'existe pas
    c.execute('''CREATE TABLE IF NOT EXISTS capteur_present (
                 DateHeure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 Orientation TEXT,
                 VitesseVent REAL)''')
    conn.commit()
    conn.close()


# Fonction pour insérer les données dans la base de données
def insert_into_db(orientation, vitesse_vent):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Insertion dans la base de données
        cursor.execute("""
            INSERT INTO capteur_present (DateHeure, Orientation, VitesseVent)
            VALUES (datetime('now'), ?, ?)
        """, (orientation, vitesse_vent))

        conn.commit()
        conn.close()

        print("Données insérées dans la base de données avec succès.")

    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion dans la base de données: {e}")


# Fonction pour publier sur MQTT
def publish_to_mqtt(client, orientation, vitesse_vent):
    try:
        message = f"Orientation: {orientation}, Vitesse Vent: {vitesse_vent} km/h"
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
        # Récupération des données du capteur (exemple, à remplacer par tes vraies données)
        orientation = "Nord"  # Exemple de direction du vent
        vitesse_vent = 12.5  # Exemple de vitesse du vent en km/h

        # Insérer dans la base de données
        insert_into_db(orientation, vitesse_vent)

        # Publier sur MQTT
        publish_to_mqtt(client, orientation, vitesse_vent)

        time.sleep(900)  # Attendre 15 minutes avant la prochaine récupération

if __name__ == "__main__":
    main()
