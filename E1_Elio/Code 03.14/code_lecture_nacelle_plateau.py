"""
Ce script permet de lire la position de la NACELLE et de la position du PLATEAU GIROUETTE
"""

from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.61"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres à lire 
REGISTERS_TO_READ = {
    "Nacelle": ???,  # Mesure Analogique de la position de la Nacelle
    "Plateau": ???,  #Mesure Analogique de la position du Plateau girouette
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


try:
    print(" Connexion à l'automate...")
    if client.connect():  
        print(" Connexion réussie.")

        for i in range(100):  # Boucle de lecture sur 5 cycles
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

            time.sleep(2)  # Attente avant la prochaine lecture

    else:
        print(" Échec de la connexion.")

except Exception as e:
    print(f" Une erreur s'est produite : {e}")

finally:
    client.close()
    print(" Connexion fermée.")
