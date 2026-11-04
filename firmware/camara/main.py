# ============================================
# Proyecto:  AuraBot
# Archivo:   main.py (Cámara - Versión Freenove WROVER)
# Objetivo:  Capturar y publicar frames por MQTT
# ============================================

import network
import time
import camera
import gc
from umqtt.simple import MQTTClient
import config
from machine import Pin, I2C

T_NODO = b"aurabot/actuador/nodo/cam"
T_CAM = b"aurabot/sensor/camara/cam"

def conectar_wifi():
    estacion = network.WLAN(network.STA_IF)
    estacion.active(True)
    estacion.connect(config.WIFI_SSID, config.WIFI_CLAVE)
    print("Conectando a WiFi...")
    inicio = time.ticks_ms()
    while not estacion.isconnected():
        if time.ticks_diff(time.ticks_ms(), inicio) > 15000:
            print("Error: Timeout WiFi")
            return False
        time.sleep(0.5)
    print("WiFi conectado. IP:", estacion.ifconfig()[0])
    return True

def iniciar_mqtt():
    cliente = MQTTClient(
        client_id="aurabot_camara", 
        server=config.IP_BROKER, 
        user=config.USUARIO_MQTT, 
        password=config.CLAVE_MQTT,
        keepalive=30
    )
    cliente.set_last_will(T_NODO, b"offline", retain=True, qos=1)
    try:
        cliente.connect()
        cliente.publish(T_NODO, b"online", retain=True, qos=1)
        print("MQTT conectado.")
        return cliente
    except Exception as e:
        print("Fallo MQTT:", e)
        return None

def main():
    if not conectar_wifi():
        return
    
    cliente_mqtt = iniciar_mqtt()
    if not cliente_mqtt:
        return

    # ==============================================
    # INICIALIZACIÓN DE CÁMARA (FREENOVE WROVER)
    # ==============================================
    try:
        print("Mapeando pines de la Freenove WROVER...")
        # 1. Bus de comunicación I2C para el sensor
        i2c_cam = I2C(0, scl=Pin(27), sda=Pin(26), freq=100000)
        
        # 2. Crear el objeto cámara con el pinout exacto de Freenove
        # 2. Crear el objeto cámara con el pinout exacto de Freenove
        cam = camera.Camera(
            data_pins=[4, 5, 18, 19, 36, 39, 34, 35],
            vsync_pin=25,
            href_pin=23,
            pclk_pin=22,
            xclk_pin=21,
            i2c=i2c_cam
        )
        
        # 3. Formato QVGA (320x240) para fluidez en MQTT
        #cam.framesize = camera.FrameSize.QVGA
        time.sleep(1) 
        print("Cámara inicializada exitosamente.")
    except Exception as e:
        print("Error al iniciar cámara:", e)
        return

    # ==============================================
    # CICLO DE CAPTURA Y PUBLICACIÓN
    # ==============================================
    while True:
        try:
            buf = cam.capture()
            if buf:
                # Publicar JPEG crudo
                cliente_mqtt.publish(T_CAM, buf, retain=False, qos=0)
                print("Frame publicado:", len(buf), "bytes")
            
            # Limpiar memoria RAM después de cada foto
            gc.collect()
            time.sleep(2)
            
        except OSError:
            print("Pérdida de conexión MQTT. Reconectando...")
            time.sleep(5)
            cliente_mqtt = iniciar_mqtt()

if __name__ == "__main__":
    main()