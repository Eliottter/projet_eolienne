from pymodbus.client import ModbusTcpClient as ModbusClient
import sqlite3
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.61"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres
REGISTERS_TO_READ = {
    "Orientation": 150, # Mesure Analogique orientation du vent
    "VitesseVent": 152, # Mesure Analogique Vitesse Vent
    "Temperature": 160, # Température
    "DirectionVent": 163 # Direction du vent
}

REGISTERS_TO_WRITE = {
    "C1_Capteur1": 160,  # Température
    "C2_Capteur2": 161,  # Vitesse du vent
    "C3_Capteur3": 163   # Direction du vent
}

# Connexion à l'automate
client = ModbusClient(host=AUTOMATE_IP, port=AUTOMATE_PORT)

def read_register_safe(client, address):
    for attempt in range(MAX_RETRIES):
        result = client.read_holding_registers(address)
        if not result.isError():
            return result.registers[0]
        print(f"Erreur de lecture au registre {address}. Tentative {attempt+1}/{MAX_RETRIES}")
        time.sleep(1)
    return None

def write_register_safe(client, address, value):
    """
    Fonction pour tenter plusieurs fois d'écrire dans un registre.
    Args:
        client: Instance de ModbusTcpClient.
        address: Adresse du registre à écrire.
        value: Valeur à écrire.
    Returns:
        bool: True si l'écriture est réussie, False sinon
    """
    for attempt in range(MAX_RETRIES):
        result = client.write_register(address, value)
        if not result.isError():
            print(f"Écriture réussie : {value} → registre {address}")
            return True
        print(f"Erreur d'écriture au registre {address}. Tentative {attempt+1}/{MAX_RETRIES}")
        time.sleep(1)
    return False

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
    Convertit une valeur brute du capteur (0-10000) en m/s.
    Args:
        value (int): Valeur brute du capteur.
    Returns:
        float: Vitesse du vent en m/s.
    """
    if value is None:
        return None
    return value / 20 if value / 20 <= 10000/20 else 0

def get_last_meteo_data():
    """
    Récupère les dernières données météo de la base de données. 
    Returns:
        tuple: Température (°C*10), vitesse du vent (m/s*10), direction du vent (degrés).
    """
    try:
        conn = sqlite3.connect('/home/ciel/Bureau/Elio_projet/BDD_meteo_simu.db') # ATTENTION Chemin à modifier en fonction de l'emplacement de la base de données 
        c = conn.cursor()
        c.execute("SELECT Temperature, VitesseVent, DirectionVent FROM meteo ORDER BY DateHeure DESC LIMIT 1") # selection temperature, vitesse vent, direction vent
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]*10, row[1]*10, row[2]
    except Exception as e:
        print(f"Erreur lors de la récupération des données météo : {e}")
    return None, None, None



"""
    Code principal
"""
try:
    print("Connexion à l'automate...") # Connexion à l'automate
    if client.connect(): 
        print("Connexion réussie.")
        for i in range(100): # Boucle "infinie"
            print(f"\nLecture du cycle {i+1}")
            # Lecture des registres dans REGISTERS_TO_READ
            values = {name: read_register_safe(client, reg) for name, reg in REGISTERS_TO_READ.items()}
            
            # Affichage des valeurs lues avec conversion si nécessaire
            for name, value in values.items(): # Affichage des valeurs lues
                if value is not None:
                    if name == "Orientation": # Conversion de l'orientation
                        degrees = convert_orientation_to_degrees(value)
                        print(f"{name} : {value} → {degrees}")
                    elif name == "VitesseVent":
                        vitesse = convert_vitesse_vent_to_ms(value)
                        print(f"{name} : {value} → {vitesse} m/s\n") # Conversion de la vitesse du vent
                    else:
                        print(f"{name} : {value}")
                else:
                    print(f"Impossible de lire {name}")
            
            # Écriture des valeurs météo dans l'automate
            temperature, vitesse_vent, directionVent = get_last_meteo_data()
            if temperature is not None and vitesse_vent is not None and directionVent is not None:
                sensor_values = {
                    "C1_Capteur1": int(temperature), 
                    "C2_Capteur2": int(vitesse_vent),
                    "C3_Capteur3": int(directionVent)
                }
                for name, value in sensor_values.items():
                    write_register_safe(client, REGISTERS_TO_WRITE[name], value) # Écriture des valeurs dans l'automate
            else:
                print("Données météo invalides, aucune écriture dans l'automate.")
            
            print("------------------------------------")
            time.sleep(5)
    else:
        print("Échec de la connexion.")
except Exception as e:
    print(f"Une erreur s'est produite : {e}")
finally:
    client.close()
    print("Connexion fermée.")

# if __name__ == "__main__":
#     pass


def convert_orientation_to_degrees(value):
    """
    Convertit une valeur brute 0-10000 en degrés 0-360 et associe une direction.
    """
    degrees = (value / 27.78) % 360  # 1° ≈ 27.78
    if 337.5 <= degrees or degrees < 22.5:
        direction = "Nord (N)"
    elif 22.5 <= degrees < 67.5:
        direction = "Nord-Est (NE)"
    ...
    return round(degrees, 2), direction
