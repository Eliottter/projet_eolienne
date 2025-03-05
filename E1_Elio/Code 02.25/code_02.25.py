# Ce code a pour objectif de lire les registres 160, 161 et 162 de l'automate et d'afficher leur valeur en décimal et en binaire. 
# Afin de voir si les valeurs changent apres l'utilisation du "code ecriture" (test du code écriture)
# Il est possible de modifier le temps d'attente entre chaque lecture en modifiant la valeur de la fonction time.sleep().

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
        print(f"Port 120 : {client.read_holding_registers(120).registers[0]}")

        for i in range(5):
            # Lecture du registre 160
            result160 = client.read_holding_registers(160)  # Ajout du nombre de registres à lire
            if result160.isError():
                print("Registre 160 : inaccessible ou vide.")
            else:
                valeur_lue = result160.registers[0]
                print(f"Valeur lue (port 160): {valeur_lue} ({bin(valeur_lue)})")
##############################################################
            # Lecture du registre 161
            result161 = client.read_holding_registers(161)  # Ajout du nombre de registres à lire
            if result161.isError():
                print("Registre 161 : inaccessible ou vide.")
            else:
                valeur_lue = result161.registers[0]
                print(f"Valeur lue (port 161): {valeur_lue} ({bin(valeur_lue)})")
##############################################################
            # Lecture du registre 162
            result162 = client.read_holding_registers(162)  # Ajout du nombre de registres à lire
            if result162.isError():
                print("Registre 162 : inaccessible ou vide.")
            else:
                valeur_lue = result162.registers[0]
                print(f"Valeur lue (port 162): {valeur_lue} ({bin(valeur_lue)})")
##############################################################
            print("----------------")

            time.sleep(10) 

    else:
        print("Échec de la connexion.")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")

finally:
    client.close()
    print("Connexion fermée.")
