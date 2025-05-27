import sqlite3
import paho.mqtt.client as mqtt

# Chemin vers ta base météo
path_bdd_meteo = "/home/btsciel2a/Documents/projet-ethan/BDD_meteo.db"

try:
    # Connexion à la BDD météo
    conn = sqlite3.connect(path_bdd_meteo)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DirectionVentDegres, DirectionVentCardinal, VitesseVent 
        FROM meteo 
        ORDER BY DateHeure DESC 
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()

    if row:
        degres, cardinal, vitesse = row

        # Construction du message MQTT
        message = f"orientation {degres:.2f}° ({cardinal} Vitesse du vent : {vitesse:.2f}m/s"

        # Configuration du client MQTT avec TLS
        client = mqtt.Client()
        client.username_pw_set("user", password="Azerty.1")
        client.tls_set(ca_certs="/etc/mosquitto/certs/server.crt")
        client.tls_insecure_set(True)

        # Connexion au broker sécurisé (port 8883)
        client.connect("localhost", 8883, 60)
        client.publish("capteur_present", message)

        print(f"Message MQTT envoyé en TLS : {message}")
        client.disconnect()
    else:
        print("Aucune donnée météo trouvée.")

except Exception as e:
    print(f"Erreur : {e}")
