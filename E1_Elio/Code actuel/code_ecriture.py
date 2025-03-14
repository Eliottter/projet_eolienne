from pymodbus.client import ModbusTcpClient as ModbusClient
import sqlite3
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.61"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres à lire
REGISTERS_TO_READ = {
    "Orientation": 150,  # Mesure Analogique orientation du vent
    "Vitesse_Vent": 152,  #Mesure Analogique Vitesse Vent 

}

# Définition des registres d'écriture (capteurs)
REGISTERS_TO_WRITE = {
    "C1_Capteur1": 160,  # Température
    "C2_Capteur2": 161,  # Vitesse du vent
    "C3_Capteur3": 163   # Exemple : autre donnée
}

# Connexion à l'automate
client = ModbusClient(host=AUTOMATE_IP, port=AUTOMATE_PORT)


def read_register_safe(client, address):
    """
    Fonction pour tenter plusieurs fois de lire un registre.
    Args:
        client: Instance de ModbusTcpClient.
        address: Adresse du registre à lire.
    Returns:
        Valeur du registre ou None en cas d'échec.
    """
    for attempt in range(MAX_RETRIES):
        result = client.read_holding_registers(address)  # Lecture d'un seul registre
        if not result.isError():
            return result.registers[0]  # Retourne la valeur si la lecture est réussie
        print(f" Erreur de lecture au registre {address}. Tentative {attempt+1}/{MAX_RETRIES}")
        time.sleep(1)  # Pause avant de réessayer
    return None  # Retourne None si la lecture échoue après toutes les tentatives


def write_register_safe(client, address, value):
    """
    Fonction pour tenter plusieurs fois d'écrire une valeur dans un registre.
    Args:
        client: Instance de ModbusTcpClient.
        address: Adresse du registre à écrire.
        value: Valeur à écrire.
    Returns:
        True si l'écriture est réussie, False sinon.
    """
    for attempt in range(MAX_RETRIES):
        result = client.write_register(address, value)
        if not result.isError():
            print(f" Écriture réussie : {value} → registre {address}")
            return True
        print(f" Erreur d'écriture au registre {address}. Tentative {attempt+1}/{MAX_RETRIES}")
        time.sleep(1)
    return False  # Retourne False si l'écriture échoue



def convert_orientation_to_degrees(value):
    """
    Convertit une valeur brute du capteur (0-10000) en degrés (0°-360°).
    Args:
        value (int): Valeur brute du capteur.
    Returns:
        tuple: (angle en degrés, direction cardinale)
    """
    if value is None:
        return None, "Valeur invalide"

    # Conversion en degrés (1° ≈ 27.78 unités)
    degrees = (value / 27.78) % 360  # Normalisation sur 360°

    # Définition des plages pour chaque direction
    if 337.5 <= degrees or degrees < 22.5:
        direction = "Sud (S)"
    elif 22.5 <= degrees < 67.5:
        direction = "Sud-Ouest (SO)"
    elif 67.5 <= degrees < 112.5:
        direction = "Ouest (O)"
    elif 112.5 <= degrees < 157.5:
        direction = "Nord-Ouest (NO)"
    elif 157.5 <= degrees < 202.5:
        direction = "Nord (N)"
    elif 202.5 <= degrees < 247.5:
        direction = "Nord-Est (NE)"
    elif 247.5 <= degrees < 292.5:
        direction = "Est (E)"
    elif 292.5 <= degrees < 337.5:
        direction = "Sud-Est (SE)"
    else:
        direction = "Inconnu"

    return round(degrees, 2), direction  # On arrondit à 2 décimales



def convert_vitesse_vent_to_ms(value):
    """
    Convertit une valeur brute de l'anémomètre 
    """
    if value is None:
        return None, "Valeur invalide"
    vitesse_conv = value/20
    if vitesse_conv > 10000/20:
        vitesse = 0
    else:
        vitesse = vitesse_conv
    return vitesse


##############
def get_last_meteo_data():
    """
    Récupère la dernière entrée de la base de données météo.
    Returns:
        Tuple (température, vitesse du vent) ou (None, None) en cas d'erreur.
    """
    try:
        conn = sqlite3.connect('/home/btsciel2a/Bureau/Projet_Eolienne/E1_Elio/Code Actuel/BDD_meteo_simu.db')
        c = conn.cursor()
        c.execute("SELECT Temperature, VitesseVent FROM meteo ORDER BY DateHeure DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            return row[0], row[1]  # Température, Vitesse du vent
        else:
            print(" Aucune donnée trouvée dans la base de données.")
            return None, None
    except Exception as e:
        print(f" Erreur lors de la récupération des données météo : {e}")
        return None, None
##############

try:
    print(" Connexion à l'automate...")
    if client.connect():  
        print(" Connexion réussie.")

        for i in range(5):  # Boucle de lecture sur 5 cycles
            print(f"\n Lecture du cycle {i+1}")

            # Lire chaque registre défini dans REGISTERS_TO_READ
            values = {}
            for name, reg in REGISTERS_TO_READ.items():
                values[name] = read_register_safe(client, reg)

            # Affichage des valeurs avec conversion pour l'orientation
            for name, value in values.items():
                if value is not None:
                    if name == "Orientation":  
                        degrees, direction = convert_orientation_to_degrees(value)
                        print(f" {name} ({REGISTERS_TO_READ[name]}) : {value}  → {degrees}° → Direction : {direction}")
                    else:
                        vitesse = convert_vitesse_vent_to_ms(value)
                        print(f" {name} ({REGISTERS_TO_READ[name]}) : {value} → {vitesse} m/s")
                        # print(f" {name} ({REGISTERS_TO_READ[name]}) : {value}m/s ")  # Affichage brut pour vitesse vent
                else:
                    print(f" Impossible de lire {name} ({REGISTERS_TO_READ[name]})")

##########################################
            # Récupération des données météo depuis la base de données
            temperature, vitesse_vent = get_last_meteo_data()

            # Vérification si les valeurs sont valides avant l'écriture
            if temperature is not None and vitesse_vent is not None:
                sensor_values = {
                    "C1_Capteur1": int(temperature),  # Écriture de la température
                    "C2_Capteur2": int(vitesse_vent),  # Écriture de la vitesse du vent
                    "C3_Capteur3": 100  # Valeur fixe pour l'exemple
                }

                # Écriture des valeurs dans l'automate
                for name, value in sensor_values.items():
                    write_register_safe(client, REGISTERS_TO_WRITE[name], value)

            else:
                print(" Données météo invalides, aucune écriture dans l'automate.")
##########################################
            time.sleep(2)  # Attente avant la prochaine lecture

    else:
        print(" Échec de la connexion.")

except Exception as e:
    print(f" Une erreur s'est produite : {e}")

finally:
    client.close()
    print(" Connexion fermée.")
