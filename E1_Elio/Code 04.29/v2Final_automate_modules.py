# automate_modules.py
from pymodbus.client import ModbusTcpClient as ModbusClient
import sqlite3
import time

MAX_RETRIES = 3  # Nombre de tentatives pour lecture/écriture

class AutomateModbus:
    """
    Classe pour gérer la communication avec l'automate via Modbus TCP
    """
    def __init__(self, ip, port=502):
        self.client = ModbusClient(host=ip, port=port)

    def connect(self):
        """Connexion à l'automate"""
        return self.client.connect()

    def disconnect(self):
        """Déconnexion de l'automate"""
        self.client.close()

    def read_register(self, address):
        """Lecture sécurisée d'un registre"""
        for attempt in range(MAX_RETRIES):
            result = self.client.read_holding_registers(address)
            if not result.isError():
                return result.registers[0]
            time.sleep(1)
        print(f"Erreur de lecture au registre {address}")
        return None

    def write_register(self, address, value):
        """Écriture sécurisée dans un registre"""
        for attempt in range(MAX_RETRIES):
            result = self.client.write_register(address, value)
            if not result.isError():
                return True
            time.sleep(1)
        print(f"Erreur d'écriture au registre {address}")
        return False

class BaseDeDonneesMeteo:
    """
    Classe pour accéder à la base de données SQLite contenant les données météo
    """
    def __init__(self, path_db):
        self.path_db = path_db

    def get_last_donnees(self):
        """Récupération de la dernière ligne de données météo"""
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

class ConvertisseurCapteurs:
    """
    Classe utilitaire pour convertir les données brutes en valeurs physiques
    """
    @staticmethod
    def convert_orientation(value):
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
            direction = "Nord (N)"
        elif 22.5 <= degrees < 67.5:
            direction = "Nord-Est (NE)"
        elif 67.5 <= degrees < 112.5:
            direction = "Est (E)"
        elif 112.5 <= degrees < 157.5:
            direction = "Sud-Est (SE)"
        elif 157.5 <= degrees < 202.5:
            direction = "Sud (S)"
        elif 202.5 <= degrees < 247.5:
            direction = "Sud-Ouest (SO)"
        elif 247.5 <= degrees < 292.5:
            direction = "Ouest (O)"
        elif 292.5 <= degrees < 337.5:
            direction = "Nord-Ouest (NO)"
        else:
            direction = "Inconnu"

        return round(degrees, 2), direction  # On arrondit à 2 décimales

    @staticmethod
    def convert_vitesse(value):
        """Convertit une valeur brute d'anémomètre en vitesse m/s"""
        if value is None:
            return None
        return value / 20 if value / 20 <= 10000/20 else 0
