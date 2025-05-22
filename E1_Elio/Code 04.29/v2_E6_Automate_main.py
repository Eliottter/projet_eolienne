# E6_Automate_main.py

from v2_E6_Automate_module import AutomateModbus, BaseDeDonneesMeteo, ConvertisseurCapteurs
from v2_E6_Elio_Broker import MqttPublisher
import time

# Initialisation des classes
automate = AutomateModbus(ip="172.90.93.61", port=502)
bdd_meteo = BaseDeDonneesMeteo(path_db="/home/btsciel2a/Documents/projet-ethan/BDD_meteo.db")
convertisseur = ConvertisseurCapteurs()
mqtt_publisher = MqttPublisher()  # Ajout de l'éditeur MQTT

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

                # Conversion et affichage
                orientation_deg, direction_cardinale = convertisseur.convert_orientation(orientation)
                vitesse_ms = convertisseur.convert_vitesse(vitesse)
                print(f"Orientation : {orientation_deg}° ({direction_cardinale})")
                print(f"Vitesse du vent : {vitesse_ms} m/s")

                message_mqtt = f"Orientation : {orientation_deg}° ({direction_cardinale}) Vitesse du vent : {vitesse_ms} m/s"
                mqtt_publisher.publier(message_mqtt)


                # Lecture de la BDD pour écriture dans l'automate
                temp, vitesse_bdd, direction_bdd = bdd_meteo.get_last_donnees()
                if None not in (temp, vitesse_bdd, direction_bdd):
                    automate.write_register(160, int(temp))
                    automate.write_register(161, int(vitesse_bdd))
                    automate.write_register(163, int(direction_bdd))
                    print("\nÉcriture dans l'automate réussie")

                    # Vérification
                    for reg in (160, 161, 163):
                        val = automate.read_register(reg)
                        print(f"Registre {reg} : {val}")

                    # Envoi MQTT
                    mqtt_publisher.publier()
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
