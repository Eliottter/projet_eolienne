#Ecriture port : 160; 161; 162 en decimal (A0; A1; A2 hexa)
from pymodbus.client import ModbusTcpClient as ModbusClient
import time

# Configuration de l'automate
AUTOMATE_IP = "172.90.93.62"
AUTOMATE_PORT = 502

# Définition des ports et de leur bit correspondant
PORTS = {
  8:  0b000100000000,  # 256
  9:  0b001000000000,  # 512
  10: 0b010000000000,  # 1024
  11: 0b100000000000   # 2048
}

# Connexion à l'automate
client = ModbusClient(host=AUTOMATE_IP, port=AUTOMATE_PORT)

try:
    print("Connexion à l'automate...")
    if client.connect():  #  Vérifier la connexion
        print("Connexion réussie.")

        for i in range(3):
                ### Écriture dans le registre 160
            valeur_a_ecrire = 0# Mettre la valeur que l'on veux écrire
            port_utiliser = 160+i

            write_result = client.write_register(port_utiliser, valeur_a_ecrire)
            if write_result.isError():
                print(f"Échec de l'écriture {port_utiliser} ")
            else:
                print(f" Écriture réussie {port_utiliser} ")
            time.sleep(1)  # Attente avant la prochaine lecture/écriture

            valeur_lue = client.read_holding_registers(160+i).registers[0]
            print(f"Valeur lue : {valeur_lue} ({bin(valeur_lue)})")
            time.sleep(1)

    else:
        print("Échec de la connexion.")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")

finally:
    client.close()
    print("Connexion fermée.")
