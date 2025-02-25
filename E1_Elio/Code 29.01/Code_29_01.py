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

  for i in range(10):

     print("Connexion à l'automate...")
     if client.connect():
        print("Connexion réussie.")

        # Lecture du registre 120
        result = client.read_holding_registers(120)
        if result.isError():
           print("Registre 120 : inaccessible ou vide.")
        else:
           valeur_lue = result.registers[0]
           print(f"Valeur lue : {valeur_lue} ({bin(valeur_lue)})")

           # Vérification des ports activés
           ports_actifs = [port for port, mask in PORTS.items() if valeur_lue & mask] # Savoir
           # ou
         #   ports_actifs =[]
         #   for port, mask in PORTS.items():
         #      if valeur_lue & mask: # est un ET bitwise qui sert à vérifier si un bit spécifique est activé dans la valeur lue
         #         ports_actifs.append(port)
          
           if ports_actifs:
                 print(f"Ports activés : {', '.join(map(str, ports_actifs))}")
           else:
                 print("Aucun port activé.")
          
        time.sleep(5)


  else:
     print("Échec de la connexion.")
except Exception as e:
  print(f"Une erreur s'est produite : {e}")
finally:
  client.close()
  print("Connexion fermée.")
