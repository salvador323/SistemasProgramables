import paho.mqtt.client as mqtt
import cv2
import numpy as np
import os
import sys
import json

IP_BROKER = "127.0.0.1"
PUERTO = 1883
TOPICO_CAMARA = "aurabot/sensor/camara/cam"
TOPICO_ESTADO_ROSTRO = "aurabot/estado_actual/rostro"

script_dir = os.path.dirname(os.path.abspath(__file__))
ruta_xml = os.path.join(script_dir, "haarcascade_frontalface_default.xml")
ruta_modelo = os.path.join(script_dir, "modelo_rostro.yml")
ruta_nombres = os.path.join(script_dir, "usuarios.json")

nombres = {"0": "Desconocido"}
if os.path.exists(ruta_nombres):
    with open(ruta_nombres, "r") as f:
        nombres = json.load(f)

face_cascade = cv2.CascadeClassifier(ruta_xml)
if face_cascade.empty() or not os.path.exists(ruta_modelo):
    print("[!] ERROR: Archivos del modelo no encontrados.")
    sys.exit()

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(ruta_modelo)

contador_ausente = 0
UMBRAL_ESTABILIDAD = 5
estado_anterior = None

def al_conectar(cliente, userdata, flags, rc, properties=None):
    print(f"[✓] Conectado a Mosquitto (Código: {rc})")
    cliente.subscribe(TOPICO_CAMARA)

def al_recibir_mensaje(cliente, userdata, msg):
    global contador_ausente, estado_anterior
    try:
        nparr = np.frombuffer(msg.payload, np.uint8)
        if len(nparr) == 38400:
            frame16 = nparr.view(np.uint16).byteswap().reshape((120, 160))
            b = (frame16 & 0x1F) << 3
            g = ((frame16 >> 5) & 0x3F) << 2
            r = ((frame16 >> 11) & 0x1F) << 3
            frame = np.dstack((b, g, r)).astype(np.uint8)
            frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_LINEAR)
        else:
            return

        grises = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grises = cv2.equalizeHist(grises)
        
        rostros = face_cascade.detectMultiScale(grises, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))
        
        rostro_valido = []
        if len(rostros) > 0:
            rostro_principal = max(rostros, key=lambda r: r[2] * r[3])
            rostro_valido = [rostro_principal]

        nombre_persona_actual = "Desconocido"

        for (x, y, w, h) in rostro_valido:
            rostro_recortado = grises[y:y+h, x:x+w]
            rostro_recortado = cv2.resize(rostro_recortado, (100, 100))
            
            # --- MISMO FILTRO DE SUAVIZADO AL RECONOCER ---
            rostro_recortado = cv2.GaussianBlur(rostro_recortado, (3, 3), 0)
            
            id_predicho, distancia = recognizer.predict(rostro_recortado)
            
            # Umbral de tolerancia ampliado a 85 gracias al filtro Gaussiano
            if distancia < 85:
                nombre_persona_actual = nombres.get(str(id_predicho), "Desconocido")
                color_recuadro = (0, 255, 0)
            else:
                nombre_persona_actual = nombres["0"]
                color_recuadro = (0, 0, 255)
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), color_recuadro, 2)
            cv2.putText(frame, f"{nombre_persona_actual} ({int(distancia)})", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_recuadro, 2)
        
        if len(rostro_valido) > 0:
            contador_ausente = 0
            if estado_anterior != nombre_persona_actual:
                cliente.publish(TOPICO_ESTADO_ROSTRO, nombre_persona_actual.encode('utf-8'))
                estado_anterior = nombre_persona_actual
        else:
            contador_ausente += 1
            if contador_ausente >= UMBRAL_ESTABILIDAD and estado_anterior != "ausente":
                cliente.publish(TOPICO_ESTADO_ROSTRO, b"ausente")
                estado_anterior = "ausente"
            
        cv2.imshow("AuraBot - Reconocimiento Facial", frame)
        cv2.waitKey(1)
        
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir_mensaje
    cliente.connect(IP_BROKER, PUERTO, 60)
    print("[*] Detector activo...")
    cliente.loop_forever()