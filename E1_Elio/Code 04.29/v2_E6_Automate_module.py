# automate_modules.py

# Importation des bibliothèques nécessaires
from pymodbus.client import ModbusTcpClient as ModbusClient
import sqlite3
import time

MAX_RETRIES = 3  # Nombre maximum de tentatives en cas d'échec d'une opération Modbus

class AutomateModbus:
    """
    Classe pour gérer la communication avec un automate industriel via le protocole Modbus TCP.
    Permet de se connecter, lire et écrire des registres.
    """
    def __init__(self, ip, port=502):
        self.client = ModbusClient(host=ip, port=port)

    def connect(self):
        """Établit la connexion avec l'automate"""
        return self.client.connect()

    def disconnect(self):
        """Ferme la connexion avec l'automate"""
        self.client.close()

    def read_register(self, address):
        """
        Lecture sécurisée d’un registre de l’automate.
        """
        for attempt in range(MAX_RETRIES):
            result = self.client.read_holding_registers(address)
            if not result.isError():
                return result.registers[0]
            time.sleep(1)
        print(f"Erreur de lecture au registre {address}")
        return None

    def write_register(self, address, value):
        """
        Écriture sécurisée d'une valeur dans un registre de l’automate.
        """
        for attempt in range(MAX_RETRIES):
            result = self.client.write_register(address, value)
            if not result.isError():
                return True
            time.sleep(1)
        print(f"Erreur d'écriture au registre {address}")
        return False


class BaseDeDonneesMeteo:
    """
    Classe pour interagir avec une base de données SQLite contenant les données météo simulées.
    """
    def __init__(self, path_db):
        self.path_db = path_db

    def get_last_donnees(self):
        """
        Récupère la dernière ligne de données météo dans la base.
        """
        try:
            conn = sqlite3.connect(self.path_db)
            c = conn.cursor()
            c.execute("SELECT Temperature, VitesseVent, DirectionVentDegres FROM meteo ORDER BY DateHeure DESC LIMIT 1")
            row = c.fetchone()
            conn.close()
            if row:
                return row[0]*10, row[1]*10, row[2]
        except Exception as e:
            print(f"Erreur lors de la récupération des données météo : {e}")
        return None, None, None


class ConvertisseurCapteurs:
    """
    Classe utilitaire contenant des méthodes statiques de conversion de valeurs brutes issues de capteurs.
    """
    @staticmethod
    def convert_orientation(value):
        if value is None:
            return None, "Valeur invalide"
        degrees = (value / 27.78) % 360
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
        return round(degrees, 2), direction

    @staticmethod
    def convert_vitesse(value):
        if value is None:
            return None
        return value / 20 if value / 20 <= 500 else 0


class BaseDeDonneesMesures:
    """
    Classe pour gérer la base de données contenant les mesures réelles de l’automate (orientation brute, vitesse).
    """
    def __init__(self, path_db):
        self.path_db = path_db
        self.creer_table_si_absente()

    def creer_table_si_absente(self):
        """Crée la table si elle n'existe pas déjà"""
        try:
            conn = sqlite3.connect(self.path_db)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS mesures (
                    DateHeure DATETIME DEFAULT CURRENT_TIMESTAMP,
                    OrientationBrute INTEGER,
                    DirectionCardinale TEXT,
                    Vitesse_ms REAL
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la création de la table mesures : {e}")

    def ajouter_mesure(self, orientation_brute, direction_cardinale, vitesse_ms):
        """Insère une nouvelle mesure dans la base"""
        try:
            conn = sqlite3.connect(self.path_db)
            c = conn.cursor()
            c.execute("""
                INSERT INTO mesures (OrientationBrute, DirectionCardinale, Vitesse_ms)
                VALUES (?, ?, ?)
            """, (orientation_brute, direction_cardinale, vitesse_ms))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur lors de l'insertion de la mesure : {e}")

    def get_last_donnees(self):
        """Récupère la dernière mesure enregistrée"""
        try:
            conn = sqlite3.connect(self.path_db)
            c = conn.cursor()
            c.execute("""
                SELECT OrientationBrute, DirectionCardinale, Vitesse_ms
                FROM mesures
                ORDER BY DateHeure DESC
                LIMIT 1
            """)
            row = c.fetchone()
            conn.close()
            return row if row else (None, None, None)
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
            return None, None, None

