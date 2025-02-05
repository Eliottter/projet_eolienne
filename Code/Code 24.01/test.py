
#### Version 1 ####
# from pymodbus.client import ModbusTcpClient as ModbusClient

# import time

# client = ModbusClient(host="172.90.93.62",port=502)#"option", auto_close=True

# try:
#     print("Start client...")
#     client.connect()
#     print("Client is online")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     client.close()

from pymodbus.client import ModbusTcpClient as ModbusClient

AUTOMATE_IP = "172.90.93.62"
AUTOMATE_PORT = 502
START_ADDRESS = 0      
END_ADDRESS = 10     

def check_registers(client, start, end):
    """
    Vérifie les registres dans la plage donnée pour voir s'ils contiennent des données exploitables.
    """
    print(f"Lecture des registres de {start} à {end}...")
    for address in range(start, end + 1):
        try:
            result = client.read_holding_registers(address, 1)
            if result.isError():
                print(f"Registre {address} : inaccessible ou vide.")
            else:
                print(f"Registre {address} : valeur lue = {result.registers[0]}")
        except Exception as e:
            print(f"Erreur lors de la lecture du registre {address} : {e}")

# Connexion à l'automate
client = ModbusClient(host=AUTOMATE_IP, port=AUTOMATE_PORT)

try:
    print("Connexion à l'automate...")
    if client.connect():
        print("Connexion réussie.")
        # Vérification des registres
        check_registers(client, START_ADDRESS, END_ADDRESS)
    else:
        print("Échec de la connexion.")
except Exception as e:
    print(f"Une erreur s'est produite : {e}")
finally:
    client.close()
    print("Connexion fermée.")
