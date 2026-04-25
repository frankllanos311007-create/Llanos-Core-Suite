import os
import time
import requests
import subprocess
import sys

# Configuración de Alta Velocidad
FIREBASE_URL = "https://llanos-core-gestion-docmentos-default-rtdb.firebaseio.com/registros.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_cloud():
    try:
        # Timeout corto para respuesta rápida
        response = requests.get(FIREBASE_URL, timeout=3)
        data = response.json()
        if data and isinstance(data, dict) and "error" not in data:
            return True
    except:
        pass
    return False

def start_monitor():
    print("--- MONITOR LLANOS CORE (ALTA VELOCIDAD) ---")
    print("Vigilando la nube cada 5 segundos...")
    
    while True:
        if check_cloud():
            print("(!) REGISTRO DETECTADO. Lanzando sistema de inmediato...")
            try:
                # Lanzar el sistema de forma independiente
                subprocess.Popen(['start', 'Ejecutar.bat'], shell=True, cwd=BASE_DIR)
                # Esperamos 3 minutos antes de volver a chequear (tiempo de gracia)
                time.sleep(180) 
            except Exception as e:
                print(f"Error: {e}")
        
        # AHORA CHEQUEA CADA 5 SEGUNDOS
        time.sleep(5)

if __name__ == "__main__":
    try:
        start_monitor()
    except Exception as e:
        time.sleep(10)
