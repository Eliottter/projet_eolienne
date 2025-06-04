import asyncio
import websockets
import sys


async def send_message():
    try:
        # Version corrigée sans le paramètre timeout dans connect()
        async with websockets.connect("ws://127.0.0.1:8765") as ws:
            message = "Hello Server"
            await ws.send(message)
            print(f"Envoyé: {message}")

            # Gestion du timeout pour la réception
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=10)
                print(f"Reçu: {response}")
            except asyncio.TimeoutError:
                print("Timeout: Pas de réponse du serveur")

    except Exception as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(send_message())
