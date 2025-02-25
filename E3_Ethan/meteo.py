import requests
import time

# Configuration
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
API_KEY = "94df689b87c4a001afc9562d1bfb2888"  # Votre clé API OpenWeatherMap

# Fonction pour récupérer les données météorologiques
def get_weather_data(lat, lon):
    try:
        url = WEATHER_API_URL.format(lat=lat, lon=lon, API_KEY=API_KEY)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Échec de la récupération des données météorologiques. Code d'erreur: {response.status_code}")
            print("Réponse de l'API:", response.text)
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données météorologiques: {e}")
        return None

# Fonction principale
def main():
    # Coordonnées de Brest (latitude et longitude)
    lat = 48.3904
    lon = -4.4861

    while True:
        weather_data = get_weather_data(lat, lon)
        if weather_data:
            print("Données météo récupérées :", weather_data)
        time.sleep(60)

if __name__ == "__main__":
    main()
