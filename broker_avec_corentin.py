import sqlite3
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# Chemin vers la base de données
db_path = "var/www/html/capteurs_data.db"

# Création de la table si elle n'existe pas
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS test_capteurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    temperature REAL,
    angle_x REAL,
    angle_y REAL
)
''')
conn.commit()
conn.close()

# Callback lors de la réception d'un message
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("Message reçu :", payload)
        data = json.loads(payload)

        temperature = float(data["temperature"])
        angle_x = float(data["Angle X"])
        angle_y = float(data["Angle Y"])

        # Insertion dans la base
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO test_capteurs (date, temperature, angle_x, angle_y)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M"), temperature, angle_x, angle_y))
        conn.commit()
        conn.close()

        print(f"Données insérées : Temp={temperature}, X={angle_x}, Y={angle_y}")

    except Exception as e:
        print(f"Erreur traitement message : {e}")

# Configuration MQTT sans authentification
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 5)
client.subscribe("test_capteurs")

print("En écoute sur le topic test_capteurs...")
client.loop_forever()
