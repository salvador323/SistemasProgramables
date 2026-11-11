import paho.mqtt.client as mqtt
import cv2
import numpy as np
import sys
import os
import json
import urllib.request

IP_BROKER = "127.0.0.1"
PUERTO = 1883
TOPICO_CAMARA = "aurabot/sensor/camara/cam"

script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(script_dir, "dataset")
ruta_xml = os.path.join(script_dir, "haarcascade_frontalface_default.xml")
ruta_nombres = os.path.join(script_dir, "usuarios.json")
url_xml = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"

if not os.path.exists(ruta_xml) or os.path.getsize(ruta_xml) < 10000:
    urllib.request.urlretrieve(url_xml, ruta_xml)

face_cascade = cv2.CascadeClassifier(ruta_xml)

print("\n=== REGISTRO DE USUARIOS EN AURABOT ===")
user_id = input("ID numérico del usuario (ej: 1, 2, 3): ").strip()
user_name = input("Nombre de la persona: ").strip()

if not user_id.isdigit():
    print("[!] El ID debe ser un número.")
    sys.exit()

user_id = int(user_id)

usuarios = {"0": "Desconocido"}
if os.path.exists(ruta_nombres):
    with open(ruta_nombres, "r") as f:
        usuarios = json.load(f)

usuarios[str(user_id)] = user_name
with open(ruta_nombres, "w") as f:
    json.dump(usuarios, f, indent=4)

user_folder = os.path.join(dataset_dir, f"user_{user_id}")
os.makedirs(user_folder, exist_ok=True)

muestras = 0
TOTAL_MUESTRAS = 30

def al_recibir_mensaje(cliente, userdata, msg):
    global muestras
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
        
        if len(rostros) > 0:
            rostro_principal = max(rostros, key=lambda r: r[2] * r[3])
            (x, y, w, h) = rostro_principal
            
            rostro_recortado = grises[y:y+h, x:x+w]
            rostro_recortado = cv2.resize(rostro_recortado, (100, 100))
            
            # --- FILTRO CLAVE: Elimina reflejos de lentes y artefactos de luz ---
            rostro_recortado = cv2.GaussianBlur(rostro_recortado, (3, 3), 0)
            
            muestras += 1
            cv2.imwrite(os.path.join(user_folder, f"foto_{muestras}.jpg"), rostro_recortado)
            
            instruccion = f"Registrando '{user_name}': {muestras}/{TOTAL_MUESTRAS} (Mueve levemente la cabeza)"
            print(f"[*] {instruccion}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{muestras}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("AuraBot - Registro Continuo", frame)
        cv2.waitKey(1)
        
        if muestras >= TOTAL_MUESTRAS:
            cv2.destroyAllWindows()
            cliente.disconnect()
            entrenar_modelo_completo()
            sys.exit()
            
    except Exception as e:
        print("[!] Error:", e)

def entrenar_modelo_completo():
    print("\n[y] Entrenando modelo facial agnóstico a lentes...")
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
    
    rostros_totales = []
    etiquetas_totales = []
    
    for item in os.listdir(dataset_dir):
        folder_path = os.path.join(dataset_dir, item)
        if os.path.isdir(folder_path) and item.startswith("user_"):
            id_actual = int(item.split("_")[1])
            for filename in os.listdir(folder_path):
                if filename.endswith(".jpg"):
                    img_path = os.path.join(folder_path, filename)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        rostros_totales.append(img)
                        etiquetas_totales.append(id_actual)
                        
    if len(rostros_totales) > 0:
        recognizer.train(rostros_totales, np.array(etiquetas_totales))
        recognizer.write(os.path.join(script_dir, "modelo_rostro.yml"))
        print(f"[✓] Modelo actualizado. {len(rostros_totales)} muestras procesadas.")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_message = al_recibir_mensaje
cliente.connect(IP_BROKER, PUERTO, 60)
cliente.subscribe(TOPICO_CAMARA)
cliente.loop_forever()