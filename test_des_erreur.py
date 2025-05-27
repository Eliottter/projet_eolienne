import socket
import requests
import subprocess

# Configuration
HOST = "api.weatherapi.com"
IP_TEST = "8.8.8.8"
VILLE = "Brest"

URL_HTTP = f"http://api.weatherapi.com/v1/current.json?key=9b4f6d96f5cd4a709db145328252201&q={VILLE}"
URL_HTTPS = f"https://api.weatherapi.com/v1/current.json?key=9b4f6d96f5cd4a709db145328252201&q={VILLE}"

def test_ping(host):
    try:
        subprocess.run(["ping", "-c", "1", host], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Ping OK"
    except subprocess.CalledProcessError:
        return False, "Ping échoué"

def test_port(host, port, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"Port {port} OK"
    except Exception as e:
        return False, f"Port {port} KO ({str(e)})"

def test_http(url):
    try:
        r = requests.get(url, timeout=5)
        return True, f"HTTP {url} OK (code {r.status_code})"
    except Exception as e:
        return False, f"HTTP {url} KO ({str(e)})"

def test_https(url):
    try:
        r = requests.get(url, timeout=5, verify=True)
        return True, f"HTTPS {url} OK (code {r.status_code})"
    except Exception as e:
        return False, f"HTTPS {url} KO ({str(e)})"

def run_tests():
    print("=== TESTS DE CONNEXION ===")
    tests = []

    # Ping
    tests.append(test_ping(IP_TEST))

    # Ports
    for port in [22, 80, 443]:
        tests.append(test_port(HOST, port))

    # Requête API WeatherAPI en HTTP
    tests.append(test_http(URL_HTTP))

    # Requête API WeatherAPI en HTTPS
    tests.append(test_https(URL_HTTPS))

    print("\n=== RESULTATS ===")
    for success, msg in tests:
        print(("OK   " if success else "FAIL ") + "- " + msg)

if __name__ == "__main__":
    run_tests()
