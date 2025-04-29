# main.py

from Final_automate_modules import AutomateModbus, BaseDeDonneesMeteo, ConvertisseurCapteurs
import time

if __name__ == "__main__":
    # Initialisation des classes principales
    automate = AutomateModbus(ip="172.90.93.61", port=502)
    bdd_meteo = BaseDeDonneesMeteo(path_db="/home/btsciel2a/Bureau/Projet_Eolienne/E1_Elio/Code Actuel/BDD_meteo_simu.db")
    convertisseur = ConvertisseurCapteurs()

    print("Connexion à l'automate...")
    if automate.connect():
        print("Connexion réussie.")
        try:
            for i in range(100):  # Boucle de lecture/écriture répétée
                print(f"\nLecture du cycle {i+1}")

                # Lecture des valeurs brutes sur l'automate
                orientation_brute = automate.read_register(150)
                vitesse_brute = automate.read_register(152)

                # Conversion des données
                orientation_deg, direction_cardinale = convertisseur.convert_orientation(orientation_brute)
                vitesse_ms = convertisseur.convert_vitesse(vitesse_brute)

                # Affichage des valeurs converties
                print(f"Orientation : {orientation_deg}° ({direction_cardinale})")
                print(f"Vitesse du vent : {vitesse_ms} m/s")

                # Récupération des dernières données météo
                temp, vitesse_bdd, direction_bdd = bdd_meteo.get_last_donnees()
                if temp is not None and vitesse_bdd is not None and direction_bdd is not None:
                    # Écriture des valeurs dans les registres cibles
                    automate.write_register(160, int(temp))
                    automate.write_register(161, int(vitesse_bdd))
                    automate.write_register(163, int(direction_bdd))
                else:
                    print("Pas de données météo disponibles.")

                time.sleep(2)  # Pause entre deux cycles
        except Exception as e:
            print(f"Erreur durant l'exécution : {e}")
        finally:
            automate.disconnect()
            print("Connexion fermée.")
    else:
        print("Échec de la connexion.")