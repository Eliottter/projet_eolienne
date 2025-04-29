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
            result = self.client.read_holding_registers(address, 1)
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
            conn = sqlite3.connect(self.path_db)
            c = conn.cursor()
            c.execute("SELECT VitesseVent, Temperature, DirectionVent FROM meteo ORDER BY DateHeure DESC LIMIT 1")
            row = c.fetchone()
            conn.close()
            if row:
                return row[1], row[0], row[2]  # Temperature, Vitesse, Direction
            else:
                return None, None, None
        except Exception as e:
            print(f"Erreur d'accès BDD : {e}")
            return None, None, None

class ConvertisseurCapteurs:
    """
    Classe utilitaire pour convertir les données brutes en valeurs physiques
    """
    @staticmethod
    def convert_orientation(value):
        """Convertit une valeur brute de girouette en angle et direction cardinale"""
        if value is None:
            return None, None
        degrees = (value / 27.78) % 360
        if degrees < 22.5 or degrees >= 337.5:
            direction = "Nord (N)"
        elif degrees < 67.5:
            direction = "Nord-Est (NE)"
        elif degrees < 112.5:
            direction = "Est (E)"
        elif degrees < 157.5:
            direction = "Sud-Est (SE)"
        elif degrees < 202.5:
            direction = "Sud (S)"
        elif degrees < 247.5:
            direction = "Sud-Ouest (SO)"
        elif degrees < 292.5:
            direction = "Ouest (O)"
        else:
            direction = "Nord-Ouest (NO)"
        return round(degrees, 2), direction

    @staticmethod
    def convert_vitesse(value):
        """Convertit une valeur brute d'anémomètre en vitesse m/s"""
        if value is None:
            return None
        return value / 1000.0
