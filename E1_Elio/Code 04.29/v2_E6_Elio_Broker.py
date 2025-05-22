# mqtt_publisher.py

import sqlite3
import paho.mqtt.client as mqtt

class MqttPublisher:
    def __init__(self, 
                 db_path="/var/www/html/BDD_meteo.db",
                 broker="localhost",
                 port=8883,  # Port TLS
                 topic="capteur_present",
                 username="user",
                 password="Azerty.1",
                 cafile="/etc/mosquitto/certs/server.crt"):
        self.db_path = db_path
        self.broker = broker
        self.port = port
        self.topic = topic
        self.username = username
        self.password = password
        self.cafile = cafile

    def recuperer_donnees_bdd(self):
        """Lit la dernière ligne dans la base météo et retourne les valeurs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DirectionVentDegres, DirectionVentCardinal, VitesseVent
                FROM meteo
                ORDER BY DateHeure DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            return row if row else None
        except Exception as e:
            print(f"Erreur lors de la lecture de la base de données : {e}")
            return None

    def construire_message(self, degres, cardinal, vitesse):
        return f"Orientation {degres:.2f}° ({cardinal}) | Vitesse du vent : {vitesse:.2f} m/s"

    def publier(self, message):
            try:
                client = mqtt.Client()
                client.username_pw_set(self.username, password=self.password)
                client.connect(self.broker, self.port, 5)
                client.publish(self.topic, message)
                print(f"Message MQTT envoyé : {message}")
                client.disconnect()
            except Exception as e:
                print(f"Erreur lors de l'envoi MQTT : {e}")

if __name__ == "__main__":
    publisher = MqttPublisher()
    publisher.publier()
