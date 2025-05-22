# automate_modules.py

# Importation des bibliothèques nécessaires
from pymodbus.client import ModbusTcpClient as ModbusClient  # Client pour communication Modbus TCP
import sqlite3  # Pour gérer la base de données SQLite
import time     # Pour les délais entre tentatives de lecture/écriture

MAX_RETRIES = 3  # Nombre maximum de tentatives en cas d'échec d'une opération Modbus

class AutomateModbus:
    """
    Classe pour gérer la communication avec un automate industriel via le protocole Modbus TCP.
    Permet de se connecter, lire et écrire des registres.
    """
    def __init__(self, ip, port=502):
        # Initialisation du client Modbus avec l'adresse IP et le port spécifiés
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
        Tente jusqu’à MAX_RETRIES fois avant d’abandonner.
        """
        for attempt in range(MAX_RETRIES):
            result = self.client.read_holding_registers(address)
            if not result.isError():
                return result.registers[0]  # Retourne la valeur lue si pas d'erreur
            time.sleep(1)  # Pause avant de réessayer
        print(f"Erreur de lecture au registre {address}")  # Message d’erreur après les tentatives échouées
        return None

    def write_register(self, address, value):
        """
        Écriture sécurisée d'une valeur dans un registre de l’automate.
        Tente jusqu’à MAX_RETRIES fois avant d’abandonner.
        """
        for attempt in range(MAX_RETRIES):
            result = self.client.write_register(address, value)
            if not result.isError():
                return True  # Écriture réussie
            time.sleep(1)  # Pause avant de réessayer
        print(f"Erreur d'écriture au registre {address}")  # Message d’erreur après les tentatives échouées
        return False


class BaseDeDonneesMeteo:
    """
    Classe pour interagir avec une base de données SQLite contenant les données météo simulées.
    """
    def __init__(self, path_db):
        # Chemin vers le fichier de base de données
        self.path_db = path_db

    def get_last_donnees(self):
        """
        Récupère la dernière ligne de données météo dans la base.
        Retourne la température, la vitesse et la direction du vent.
        Les valeurs numériques sont multipliées par 10 pour conversion.
        """
        try:
            # Connexion à la base de données SQLite (chemin codé en dur ici)
            conn = sqlite3.connect('/var/www/html/BDD_meteo.db')
            c = conn.cursor()
            # Requête pour obtenir la dernière entrée
            c.execute("SELECT Temperature, VitesseVent, DirectionVentDegres FROM meteo ORDER BY DateHeure DESC LIMIT 1")
            row = c.fetchone()  # Récupère une seule ligne
            conn.close()
            if row:
                # Retour des valeurs converties
                return row[0]*10, row[1]*10, row[2]
        except Exception as e:
            # En cas d'erreur lors de la lecture de la base
            print(f"Erreur lors de la récupération des données météo : {e}")
        return None, None, None


class ConvertisseurCapteurs:
    """
    Classe utilitaire contenant des méthodes statiques de conversion de valeurs brutes issues de capteurs.
    """

    @staticmethod
    def convert_orientation(value):
        """
        Convertit une valeur brute d’orientation (0-10000) en angle (0-360°) et direction cardinale.
        Args:
            value (int): Valeur brute du capteur.
        Returns:
            tuple: (angle en degrés, direction cardinale)
        """
        if value is None:
            return None, "Valeur invalide"

        # Conversion de l’unité brute vers des degrés (1° ≈ 27.78 unités)
        degrees = (value / 27.78) % 360  # Normalisation pour rester dans 0–360°

        # Correspondance entre les plages de degrés et les points cardinaux
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

        return round(degrees, 2), direction  # Résultat arrondi à 2 décimales

    @staticmethod
    def convert_vitesse(value):
        """
        Convertit une valeur brute d’anémomètre en vitesse du vent (m/s).
        On divise par 20 selon le facteur de calibration.
        """
        if value is None:
            return None
        return value / 20 if value / 20 <= 500 else 0  # Limite à 500 m/s pour éviter les valeurs aberrantes
