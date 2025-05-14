from Final_automate_modules import AutomateModbus, BaseDeDonneesMeteo, ConvertisseurCapteurs
import time

# Initialisation des classes principales
automate = AutomateModbus(ip="172.90.93.61", port=502)
bdd_meteo = BaseDeDonneesMeteo(path_db="/home/ciel/Bureau/Elio_projet/BDD_meteo_simu.db")
convertisseur = ConvertisseurCapteurs()

# Fonction pour afficher les données converties
def afficher_donnees_converties(orientation, vitesse):
    orientation_deg, direction_cardinale = convertisseur.convert_orientation(orientation)
    vitesse_ms = convertisseur.convert_vitesse(vitesse)
    print(f"Orientation : {orientation_deg}° ({direction_cardinale})")
    print(f"Vitesse du vent : {vitesse_ms} m/s")

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

                # Affichage des conversions
                afficher_donnees_converties(orientation, vitesse)

                # Données météo à écrire
                temp, vitesse_bdd, direction_bdd = bdd_meteo.get_last_donnees()
                if None not in (temp, vitesse_bdd, direction_bdd):
                    ecrire_donnees_meteo(temp, vitesse_bdd, direction_bdd)
                    verifier_ecriture()
                else:
                    print("Aucune donnée météo disponible.")

                time.sleep(5)

        except Exception as e:
            print(f"Erreur durant l'exécution : {e}")
        finally:
            automate.disconnect()
            print("Connexion fermée.")
    else:
        print("Échec de la connexion.")
