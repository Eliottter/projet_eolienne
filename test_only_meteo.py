import requests

# Configuration
VILLE = "Brest, France"
API_KEY = "9b4f6d96f5cd4a709db145328252201"
WEATHER_API_URL = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={VILLE}"

def get_donnee_meteo():
    try:
        print("Requête envoyée à :", WEATHER_API_URL)
        response = requests.get(WEATHER_API_URL, verify=False)  # Test SSL
        print("Code HTTP :", response.status_code)

        if response.status_code == 200:
            data = response.json()
            print(" Données météo récupérées :")
            print("Température :", data["current"]["temp_c"], "°C")
            print("Vent :", data["current"]["wind_kph"], "km/h")
            print("Direction :", data["current"]["wind_dir"], "-", data["current"]["wind_degree"], "°")
        else:
            print(" Erreur lors de la récupération :", response.text)

    except requests.exceptions.SSLError as ssl_err:
        print(" Erreur SSL :", ssl_err)
    except Exception as e:
        print(" Erreur inattendue :", e)

if __name__ == "__main__":
    get_donnee_meteo()
