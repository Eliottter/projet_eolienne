from pymodbus.client import ModbusTcpClient as ModbusClient
import sqlite3
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.62"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres à lire
REGISTERS_TO_READ = {
    "VitesseVent": 160, # Température écrite par le capteur 1
    "Temperature": 161, # Inclinaison écrite par le capteur 2
    "DirectionVent": 162 # Test donnée aléatoire écrite par le capteur 3
}

# Définition des registres d'écriture (capteurs)
REGISTERS_TO_WRITE = {
    "registre1": 160,  # Température
    "registre2": 161,  # Inclinaison
    "registre3": 162   # Test donnée aléatoire
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


##########################################
def get_last_meteo_data():
    """
    Récupère la dernière entrée de la base de données météo.
    Returns:
        Tuple (température, vitesse du vent) ou (None, None) en cas d'erreur.
    """
    try:
        conn = sqlite3.connect('/home/btsciel2a/Bureau/Projet_Eolienne/E1_Elio/Code 03.14/BDD_meteo_simu.db') # Chemin de la base de données !!!!!!!!!
        c = conn.cursor()
        c.execute("SELECT VitesseVent, Temperature, DirectionVent FROM meteo ORDER BY DateHeure DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            return row[0], row[1], row[2]  # Température, Vitesse du vent
        else:
            print(" Aucune donnée trouvée dans la base de données.")
            return None, None, None
    except Exception as e:
        print(f" Erreur lors de la récupération des données météo : {e}")
        return None, None, None
##########################################



try:
    print(" Connexion à l'automate...")
    if client.connect():  
        print(" Connexion réussie.")

        for i in range(100):  # Boucle de lecture sur 100 cycles
            print(f"\n Lecture du cycle {i+1}")

            # Lire chaque registre défini dans REGISTERS_TO_READ
            values = {}
            for name, reg in REGISTERS_TO_READ.items():
                values[name] = read_register_safe(client, reg)

            # Affichage des valeurs lues
            for name, value in values.items():
                if value is not None:
                    print(f" {name} ({REGISTERS_TO_READ[name]}) : {value} ")
                else:
                    print(f" Impossible de lire {name} ({REGISTERS_TO_READ[name]})")

##########################################  
            # Récupération des données météo depuis la base de données
            temperature, vitesse_vent, directionvent = get_last_meteo_data()

            # Vérification si les valeurs sont valides avant l'écriture
            if temperature is not None and vitesse_vent is not None and directionvent is not None:
                sensor_values = {
                    "registre1": int(temperature),   # Écriture de la température
                    "registre2": int(vitesse_vent),  # Écriture de la vitesse du vent
                    "registre3": int(directionvent)  # Valeur fixe pour l'exemple
                }

                # Écriture des valeurs dans l'automate
                for name, value in sensor_values.items():
                    write_register_safe(client, REGISTERS_TO_WRITE[name], value)

            else:
                print(" Données météo invalides, aucune écriture dans l'automate.")
##########################################
            print("------------------------------------")
            time.sleep(5)  # Attente avant la prochaine lecture

    else:
        print(" Échec de la connexion.")

except Exception as e:
    print(f" Une erreur s'est produite : {e}")

finally:
    client.close()
    print(" Connexion fermée.")
