import sqlite3
import paho.mqtt.client as mqtt
import re
from datetime import datetime

# Connexion à la base SQLite
conn = sqlite3.connect("./capteur_present.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS capteur_present (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    orientation_deg REAL,
    orientation_card TEXT,
    vitesse_vent REAL
)
''')
conn.commit()

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("Message reçu :", repr(payload))

    orientation_match = re.search(r"orientation\s+([\d.]+)°\s+\(([^ ]+)", payload, re.IGNORECASE)
    vitesse_match = re.search(r"Vitesse du vent\s*:\s*([\d.]+)", payload, re.IGNORECASE)

    if orientation_match and vitesse_match:
        orientation_deg = float(orientation_match.group(1))
        orientation_card = orientation_match.group(2).strip()
        vitesse_vent = float(vitesse_match.group(1))

        conn = sqlite3.connect("./capteur_present.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO capteur_present (date, orientation_deg, orientation_card, vitesse_vent)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M"), orientation_deg, orientation_card, vitesse_vent))
        conn.commit()
        conn.close()

        print("Données insérées :", orientation_deg, orientation_card, vitesse_vent)
    else:
        print("Format du message incorrect.")

# Configuration du client MQTT avec TLS
client = mqtt.Client()
client.username_pw_set("user", password="Azerty.1")
client.tls_set(ca_certs="/etc/mosquitto/certs/server.crt")  # ← chemin vers ton certificat serveur
client.tls_insecure_set(True)  # ← ignore la validation (utile pour test avec auto-signé)
client.on_message = on_message
client.connect("localhost", 8883, 60)
client.subscribe("capteur_present")

print("En écoute sur le topic MQTT (TLS)...")
client.loop_forever()
