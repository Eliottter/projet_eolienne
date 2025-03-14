from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.61"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres à lire V2
REGISTERS_TO_READ = {
    "Orientation": 150,  # Mesure Analogique orientation du vent
    "Vitesse_Vent": 152,  #Mesure Analogique Vitesse Vent 
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


            # Affichage des valeurs avec conversion pour l'orientation
            for name, value in values.items():
                if value is not None:
                    if name == "Orientation":  
                        degrees, direction = convert_orientation_to_degrees(value)
                        print(f" {name} ({REGISTERS_TO_READ[name]}) : {value}  → {degrees}° → Direction : {direction}")
                    else:
                        vitesse = convert_vitesse_vent_to_ms(value)
                        print(f" {name} ({REGISTERS_TO_READ[name]}) : {value} → {vitesse} m/s")
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
