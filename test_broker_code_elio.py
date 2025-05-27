# v2Final_automate_main.py

from v2Final_automate_modules import AutomateModbus, BaseDeDonneesMeteo, ConvertisseurCapteurs
import time
import paho.mqtt.client as mqtt

# Initialisation des classes principales
automate = AutomateModbus(ip="172.90.93.61", port=502)
bdd_meteo = BaseDeDonneesMeteo(path_db="./var/www/html/BDD_meteo.db")
convertisseur = ConvertisseurCapteurs()

# Fonction pour afficher et retourner les données converties
def afficher_et_formater_donnees_converties(orientation, vitesse):
    orientation_deg, direction_cardinale = convertisseur.convert_orientation(orientation)
    vitesse_ms = convertisseur.convert_vitesse(vitesse)
    message = f"Orientation : {orientation_deg}° ({direction_cardinale}) Vitesse du vent : {vitesse_ms} m/s"
    print(message)
    return message
l
# Fonction pour écrire les données météo dans les bons registres
def ecrire_donnees_meteo(temp, vitesse, direction):
    automate.write_register(160, int(temp))
    automate.write_register(161, int(vitesse))
    automate.write_register(163, int(direction))
    print("\nDonnées météo écrites dans l'automate :")
    print(f"Température : {temp}, Vitesse : {vitesse}, Direction : {direction}")

# Fonction de lecture des registres météo écrits
def verifier_ecriture():
    print("\nVérification des écritures :")
    for reg in (160, 161, 163):
        val = automate.read_register(reg)
        print(f"Valeur lue au registre {reg} : {val}")

# Fonction pour envoyer un message via MQTT
def envoyer_message_mqtt(message):
    client = mqtt.Client()
    client.username_pw_set("user", password="Azerty.1")  # Authentification MQTT
    try:
        client.connect("172.90.93.66", 1883, 60)  # Connexion au broker MQTT local
        client.publish("capteur_present", message)
        print(f"Message MQTT envoyé : {message}")
        client.disconnect()
    except Exception as e:
        print(f"Erreur lors de l'envoi MQTT : {e}")

# Programme principal
if __name__ == "__main__":
    print("Connexion à l'automate...")
    if automate.connect():
        print("Connexion réussie.")
        try:
            for i in range(100):
                print(f"\n--- Lecture du cycle {i+1} ---")

                # Lecture des valeurs brutes
                orientation = automate.read_register(150)
                vitesse = automate.read_register(152)

                # Affichage + message à renvoyer
                message = afficher_et_formater_donnees_converties(orientation, vitesse)

                # Envoi via MQTT
                envoyer_message_mqtt(message)

                # Données météo à écrire
                temp, vitesse_bdd, direction_bdd = bdd_meteo.get_last_donnees()
                if None not in (temp, vitesse_bdd, direction_bdd):
                    ecrire_donnees_meteo(temp, vitesse_bdd, direction_bdd)
                    verifier_ecriture()
                else:
                    print("Aucune donnée météo disponible.")

                time.sleep(2)

        except Exception as e:
            print(f"Erreur durant l'exécution : {e}")
        finally:
            automate.disconnect()
            print("Connexion fermée.")
    else:
        print("Échec de la connexion.")
