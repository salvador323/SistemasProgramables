import paho.mqtt.client as mqtt
import cv2
import numpy as np

# ============================================
# DATOS DEL BROKER (Pon los de tu Mosquitto)
# ============================================
BROKER = "192.168.1.95" # Usamos 127.0.0.1 porque este script corre en la misma PC que Mosquitto
USUARIO = "admin"  # <--- CAMBIA ESTO
CLAVE = "MiClave2026"      # <--- CAMBIA ESTO
TOPICO = "aurabot/sensor/camara/cam"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("¡Conectado a Mosquitto exitosamente!")
        client.subscribe(TOPICO)
        print(f"Suscrito y esperando video en: {TOPICO}...")
    else:
        print("Error de conexión. Código:", rc)

def on_message(client, userdata, msg):
    try:
        # 1. Convertir los bytes recibidos a un arreglo numérico
        nparr = np.frombuffer(msg.payload, np.uint8)
        
        # 2. Intentar decodificar como imagen
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is not None:
            # 3. Mostrar la imagen en una ventana ampliada
            img_grande = cv2.resize(img, (640, 480)) # Hacemos la ventana más grande para ver mejor
            cv2.imshow("AuraBot - Ojos", img_grande)
            cv2.waitKey(1) # Refrescar la ventana al instante
        else:
            # Si los 38400 bytes vienen en formato RAW crudo (sin compresión JPEG)
            print("Recibiendo bytes crudos, decodificando matriz YUV/RGB565...")
            # Redimensionamos los bytes exactos a la resolución matemática QQVGA
            img_raw = nparr.reshape(120, 160, 2)
            # Extraemos solo el canal de luminancia (escala de grises) para visualización rápida
            img_gray = img_raw[:, :, 0]
            img_grande = cv2.resize(img_gray, (640, 480))
            cv2.imshow("AuraBot - Ojos (Raw)", img_grande)
            cv2.waitKey(1)
            
    except Exception as e:
        pass # Ignoramos fotogramas corruptos para que el video no se trabe

# Configuración del cliente MQTT
cliente = cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
cliente.username_pw_set(USUARIO, CLAVE)
cliente.on_connect = on_connect
cliente.on_message = on_message

print("Iniciando Visor de AuraBot...")
try:
    cliente.connect(BROKER, 1883, 60)
    cliente.loop_forever()
except KeyboardInterrupt:
    print("\nCerrando visor...")
    cv2.destroyAllWindows()