# mqtt_publisher.py

import sqlite3
import paho.mqtt.client as mqtt

class MqttPublisher:
    def __init__(self, 
                 db_path="/var/www/html/BDD_meteo.db",  # base météo (non utilisée ici, conservée pour compatibilité éventuelle)
                 broker="localhost",
                 port=8883,  # TLS
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

    def recuperer_donnees_bdd_mesures(self):
        """Lit la dernière ligne dans la base des mesures réelles"""
        try:
            conn = sqlite3.connect("/home/btsciel2a/Documents/projet-ethan/BDD_mesures.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT OrientationBrute, DirectionCardinale, Vitesse_ms
                FROM mesures
                ORDER BY DateHeure DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            return row if row else None
        except Exception as e:
            print(f"Erreur lors de la lecture de la base de données mesures : {e}")
            return None

    def construire_message(self, degres, cardinal, vitesse):
        return f"Orientation {degres:.2f}° ({cardinal}) | Vitesse du vent : {vitesse:.2f} m/s"

    def publier_donnees_mesures(self):
        """Envoie un message MQTT formaté à partir de la base de mesures réelles"""
        row = self.recuperer_donnees_bdd_mesures()
        if row:
            degres, cardinal, vitesse = row
            message = self.construire_message(degres, cardinal, vitesse)

            try:
                client = mqtt.Client()
                client.username_pw_set(self.username, password=self.password)

                # TLS
                client.tls_set(ca_certs=self.cafile)
                client.tls_insecure_set(True)

                client.connect(self.broker, self.port, 5)
                client.publish(self.topic, message)
                print(f"Message MQTT (mesures) envoyé : {message}")
                client.disconnect()
            except Exception as e:
                print(f"Erreur lors de l'envoi MQTT : {e}")
        else:
            print("Aucune donnée de mesure à publier.")


# Exécutable pour test manuel
if __name__ == "__main__":
    publisher = MqttPublisher()
    publisher.publier_donnees_mesures()

