"""
Code 3.5 : Resume des améliorations

Lecture des registres un par un.
Boucle factorisée pour éviter les répétitions et faciliter la maintenance.
Gestion des erreurs améliorée, chaque registre est relu jusqu’à 3 fois en cas d’échec.
Affichage propre des valeurs et des ports activés.

"""

from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.62"
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture

# Définition des ports et de leur bit correspondant
PORTS = {
    8:  0b000100000000,  # 256
    9:  0b001000000000,  # 512
    10: 0b010000000000,  # 1024
    11: 0b100000000000   # 2048
}

# Liste des registres à lire individuellement
REGISTERS_TO_READ = [120, 160, 161, 162]

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
        result = client.read_holding_registers(address)  #  Lecture d'un seul registre
        if not result.isError():
            return result.registers[0]  # Retourne la valeur si la lecture est réussie
        print(f" Erreur de lecture au registre {address}. Tentative {attempt+1}/{MAX_RETRIES}")
        time.sleep(1)  # Pause avant de réessayer
    return None  # Retourne None si la lecture échoue après toutes les tentatives


def get_active_ports(value):
    """
    Vérifie quels ports sont activés en fonction du masque binaire.
    Args:
        value: Valeur lue depuis le registre.
    Returns:
        Liste des ports activés.
    """
    return [port for port, mask in PORTS.items() if value & mask]


try:
    print(" Connexion à l'automate...")
    if client.connect():  
        print(" Connexion réussie.")

        for i in range(5):  # Boucle de lecture sur 5 cycles
            print(f"\n Lecture du cycle {i+1}")

            # Lire chaque registre un par un
            values = {}
            for reg in REGISTERS_TO_READ:
                values[reg] = read_register_safe(client, reg)

            # Vérification et affichage des valeurs lues
            for reg, value in values.items():
                if value is not None:
                    print(f" Valeur lue (port {reg}): {value} ({bin(value)})")
                else:
                    print(f" Impossible de lire le registre {reg}.")

            # Vérification des ports activés à partir du registre 120
            if values[120] is not None:
                ports_actifs = get_active_ports(values[120])
                print(f" Ports activés : {ports_actifs if ports_actifs else 'Aucun'}")

            time.sleep(2)  # Attente avant la prochaine lecture

    else:
        print(" Échec de la connexion.")

except Exception as e:
    print(f" Une erreur s'est produite : {e}")

finally:
    client.close()
    print(" Connexion fermée.")
