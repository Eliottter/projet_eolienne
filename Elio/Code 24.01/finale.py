#test ecriture uniquement dispo pour ces address!  =adresse A0 ; A1 ; A2
#port lecture test "8" a priori, 120 decimal alors 78 hexadécimal

from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.62"  # Adresse IP de l'automate
AUTOMATE_PORT = 502           # Port Modbus TCP par défaut
                                        
# Adresses des registres Modbus 
REGISTER_TEMPERATURE = 100    # Adresse du registre pour la température test en hexa
REGISTER_INCLINATION = 120    # Adresse du registre pour l'inclinaison test en decimal

def read_modbus_register(client, address):
    """
    Lit la valeur d'un registre Modbus.
    Args:
        client: Instance de ModbusClient.
        address: Adresse du registre à lire.
    Returns:
        La valeur lue ou None en cas d'erreur.
    """
    try:
        result = client.read_holding_registers(address, 1)
        if result.isError():
            print(f"Erreur de lecture au registre {address}")
            return None
        return result.registers[0]
    except Exception as e:
        print(f"Erreur : {e}")
        return None
def acquire_data_from_automate(client, interval=2, iterations=25):
    """
    Acquiert les données de l'automate via Modbus TCP.
    Args:
        client: Instance de ModbusClient.
        interval: Intervalle entre chaque acquisition (en secondes).
        iterations: Nombre d'itérations d'acquisition.
    """
    print("Connexion à l'automate...")
    if not client.connect():
        print("Impossible de se connecter à l'automate.")
        return

    print("Connexion réussie. Début de l'acquisition des données.")
    print("------------------------------------------------------")
    
    for i in range(iterations):
        temperature = read_modbus_register(client, REGISTER_TEMPERATURE+1)
        inclination = read_modbus_register(client, REGISTER_INCLINATION+1)

        if temperature is not None and inclination is not None:
            print(f"Mesure {i + 1}:")
            print(f" - Température : {temperature / 10:.1f} °C")  # Exemple de mise à l'échelle
            print(f" - Inclinaison : {inclination / 10:.1f} °")   # Exemple de mise à l'échelle
        else:
            print("Erreur lors de la récupération des données.")

        print("------------------------------------------------------")
        time.sleep(interval)

    client.close()
    print("Acquisition terminée. Connexion fermée.")




# Exécute la simulation
if __name__ == "__main__":
    # Crée un client Modbus TCP
    client = ModbusClient(host=AUTOMATE_IP, port=AUTOMATE_PORT)

    # Lancement de l'acquisition
    acquire_data_from_automate(client)

