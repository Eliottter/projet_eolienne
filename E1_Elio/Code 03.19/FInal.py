from pymodbus.client import ModbusTcpClient as ModbusClient
import sqlite3
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.61"  # Nouvelle adresse IP
AUTOMATE_PORT = 502
MAX_RETRIES = 3  # Nombre de tentatives en cas d'échec de lecture/écriture

# Définition des registres
REGISTERS_TO_READ = {
    "Orientation": 150,
    "VitesseVent": 152,
    "Temperature": 160,
    "DirectionVent": 163
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
    for attempt in range(MAX_RETRIES):
        result = client.write_register(address, value)
        if not result.isError():
            print(f"Écriture réussie : {value} → registre {address}")
            return True
        print(f"Erreur d'écriture au registre {address}. Tentative {attempt+1}/{MAX_RETRIES}")
        time.sleep(1)
    return False

def convert_orientation_to_degrees(value):
    if value is None:
        return None, "Valeur invalide"
    degrees = (value / 27.78) % 360
    return round(degrees, 2)

def convert_vitesse_vent_to_ms(value):
    if value is None:
        return None
    return value / 20 if value / 20 <= 10000/20 else 0

def get_last_meteo_data():
    try:
        conn = sqlite3.connect('/home/ciel/Bureau/Elio_projet/BDD_meteo_simu.db')
        c = conn.cursor()
        c.execute("SELECT Temperature, VitesseVent, DirectionVent FROM meteo ORDER BY DateHeure DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]*10, row[1]*10, row[2]
    except Exception as e:
        print(f"Erreur lors de la récupération des données météo : {e}")
    return None, None, None

try:
    print("Connexion à l'automate...")
    if client.connect():
        print("Connexion réussie.")
        for i in range(100):
            print(f"\nLecture du cycle {i+1}")
            values = {name: read_register_safe(client, reg) for name, reg in REGISTERS_TO_READ.items()}
            
            for name, value in values.items():
                if value is not None:
                    if name == "Orientation":
                        degrees = convert_orientation_to_degrees(value)
                        print(f"{name} : {value} → {degrees}°")
                    elif name == "VitesseVent":
                        vitesse = convert_vitesse_vent_to_ms(value)
                        print(f"{name} : {value} → {vitesse} m/s")
                    else:
                        print(f"{name} : {value}")
                else:
                    print(f"Impossible de lire {name}")
            
            temperature, vitesse_vent, directionVent = get_last_meteo_data()
            if temperature is not None and vitesse_vent is not None and directionVent is not None:
                sensor_values = {
                    "C1_Capteur1": int(temperature),
                    "C2_Capteur2": int(vitesse_vent),
                    "C3_Capteur3": int(directionVent)
                }
                for name, value in sensor_values.items():
                    write_register_safe(client, REGISTERS_TO_WRITE[name], value)
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
