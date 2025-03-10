from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.91"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres à lire
REGISTERS_TO_READ = {
    "Entrees_Carte3": 100,  # Recopie des entrées logiques I0.3 à I0.7
    "Sorties_Carte3": 120,  # Recopie des sorties logiques Q0.3.16 à Q0.3.23
    "Sorties_Carte4": 140,  # Recopie des sorties logiques Q0.4.0 à Q0.4.15
    "Codeur_Nacelle": 28    # Valeur du codeur absolu de la rotation nacelle
}

# Définition des registres d'écriture (capteurs)
REGISTERS_TO_WRITE = {
    "C1_Capteur1": 160,
    "C2_Capteur2": 161,
    "C3_Capteur3": 163
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
        result = client.read_holding_registers(address, 1)  # Lecture d'un seul registre
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

            # Affichage des valeurs lues
            for name, value in values.items():
                if value is not None:
                    print(f" {name} ({REGISTERS_TO_READ[name]}) : {value} ({bin(value)})")
                else:
                    print(f" Impossible de lire {name} ({REGISTERS_TO_READ[name]})")

            # Exemple d'écriture dans les registres des capteurs
            sensor_values = {
                "C1_Capteur1": 25,  # Exemple : température en degrés
                "C2_Capteur2": 5,   # Exemple : inclinaison en degrés
                "C3_Capteur3": 100  # Exemple : autre donnée
            }

            for name, value in sensor_values.items():
                write_register_safe(client, REGISTERS_TO_WRITE[name], value)

            time.sleep(2)  # Attente avant la prochaine lecture

    else:
        print(" Échec de la connexion.")

except Exception as e:
    print(f" Une erreur s'est produite : {e}")

finally:
    client.close()
    print(" Connexion fermée.")

