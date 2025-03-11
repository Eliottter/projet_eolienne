import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

# Le chemin vers ta base de données (ajuste ce chemin)
DATABASE_PATH = '/chemin/vers/ta/base/BDD_meteo.db'

# Fonction pour récupérer les dernières données météo depuis la base de données
def get_weather_data_from_db():
    conn = sqlite3.connect(DATABASE_PATH)  # Connexion à la base de données SQLite
    cursor = conn.cursor()

    # Exécution de la requête pour récupérer la dernière entrée de la table 'meteo'
    cursor.execute("SELECT * FROM meteo ORDER BY DateHeure DESC LIMIT 1")
    data = cursor.fetchone()

    conn.close()

    if data:
        return {
            'DateHeure': data[0],  # Heure et date
            'VitesseVent': data[1],  # Vitesse du vent
            'Temperature': data[2],  # Température
            'DirectionVent': data[3],  # Direction du vent
        }
    else:
        return None

# Route principale pour afficher la page avec les données météo
@app.route('/')
def index():
    # Récupérer les données météo depuis la base de données
    weather_data = get_weather_data_from_db()
    
    # Rendre le template avec les données météo
    return render_template('index.html', weather_data=weather_data)

def get_weather_data_from_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meteo ORDER BY DateHeure DESC LIMIT 1")
        data = cursor.fetchone()
        conn.close()
        
        if data:
            return {
                'DateHeure': data[0],
                'VitesseVent': data[1],
                'Temperature': data[2],
                'DirectionVent': data[3],
            }
        else:
            return None
    except Exception as e:
        print("Erreur lors de la connexion à la base de données:", e)
        return None

if __name__ == '__main__':
    app.run(debug=True)
