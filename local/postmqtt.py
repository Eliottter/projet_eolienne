import paho.mqtt.client as mqtt
import ssl

client = mqtt.Client()
client.username_pw_set("user", "Azerty.1")
client.tls_set(ca_certs="/etc/mosquitto/certs/server.crt", cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.connect("localhost", 8883, 60)
client.publish("capteur_present", "orientation 270° (W) Vitesse du vent : 22.3")
client.disconnect()
