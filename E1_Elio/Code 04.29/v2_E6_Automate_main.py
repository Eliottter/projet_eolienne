from E6_Automate_module import AutomateModbus, BaseDeDonneesMeteo, BaseDeDonneesMesures, ConvertisseurCapteurs
from E6_Elio_Broker import MqttPublisher
import time

# Initialisation des classes
automate = AutomateModbus(ip="172.90.93.61", port=502)
bdd_meteo = BaseDeDonneesMeteo(path_db="/home/btsciel2a/Documents/projet-ethan/BDD_meteo.db")
bdd_mesures = BaseDeDonneesMesures(path_db="/home/btsciel2a/Documents/projet-ethan/BDD_mesures.db")
convertisseur = ConvertisseurCapteurs()
mqtt_publisher = MqttPublisher()

# Programme principal
if __name__ == "__main__":
    print("Connexion à l'automate...")
    if automate.connect():
        print("Connexion réussie.")
        try:
            for i in range(100):
                print(f"\n--- Lecture du cycle {i+1} ---")

                # === LECTURE des registres capteurs réels ===
                orientation = automate.read_register(150)
                vitesse = automate.read_register(152)

                orientation_deg, direction_cardinale = convertisseur.convert_orientation(orientation)
                vitesse_ms = convertisseur.convert_vitesse(vitesse)

                # Sauvegarde dans la BDD mesures
                bdd_mesures.ajouter_mesure(orientation, direction_cardinale, vitesse_ms)

                # === LECTURE des données météo simulées pour écriture dans l’automate ===
                temp, vitesse_bdd, direction_bdd = bdd_meteo.get_last_donnees()

                # === AFFICHAGE formaté ===
                print(f"Orientation : {orientation_deg}° ({direction_cardinale})")
                print(f"VitesseVent : {vitesse_ms} m/s\n")

                if None not in (temp, vitesse_bdd, direction_bdd):
                    print(f"Temperature : {temp}")
                    print(f"DirectionVent : {direction_bdd}\n")

                    if automate.write_register(160, int(temp)):
                        print(f"Ecriture réussie : {int(temp)} --> registre 160")
                    else:
                        print("Échec d’écriture registre 160")

                    if automate.write_register(161, int(vitesse_bdd)):
                        print(f"Ecriture réussie : {int(vitesse_bdd)} --> registre 161")
                    else:
                        print("Échec d’écriture registre 161")

                    if automate.write_register(163, int(direction_bdd)):
                        print(f"Ecriture réussie : {int(direction_bdd)} --> registre 163")
                    else:
                        print("Échec d’écriture registre 163")
                else:
                    print("Aucune donnée météo disponible.\n")

                # Publication MQTT
                mqtt_publisher.publier_donnees_mesures()

                # Séparateur visuel
                print("------------------")

                # Attente
                time.sleep(2)

        except Exception as e:
            print(f"Erreur durant l'exécution : {e}")
        finally:
            automate.disconnect()
            print("Connexion fermée.")
    else:
        print("Échec de la connexion.")
