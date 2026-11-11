# ============================================
# Proyecto:  AuraBot
# Archivo:   main.py
# Objetivo:  Bucle principal no bloqueante y nexo entre HAL y MQTT
# Equipo:    Sandoval Cuevas Pedro, Taboada Ramírez Salvador,
#            Barroso Garcia Braulio Axel
# Matrículas: 23240325, 23240999, 23240327
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

import time
import comunicacion
from hal.dispositivos import GestorSensores, GestorActuadores

# Inicializar HAL
sensores = GestorSensores()
actuadores = GestorActuadores()
cliente_mqtt = None

def procesar_comando(topic, msg):
    """Callback que ejecuta comandos en los actuadores y reporta el estado."""
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    
    if topic == "aurabot/comando/servo/central":
        actuadores.controlar_servo(msg)
        cliente_mqtt.publish(b"aurabot/actuador/servo/central", msg)
        
    elif topic == "aurabot/comando/relevador/central":
        actuadores.controlar_relevador(msg)
        cliente_mqtt.publish(b"aurabot/actuador/relevador/central", msg)
        
    elif topic == "aurabot/comando/oled/central":
        actuadores.controlar_oled(msg)
        cliente_mqtt.publish(b"aurabot/actuador/oled/central", msg)

def publicar_telemetria(datos):
    """Envía lecturas al broker."""
    if cliente_mqtt:
        cliente_mqtt.publish(b"aurabot/sensor/pir/central", str(datos["pir"]))
        cliente_mqtt.publish(b"aurabot/sensor/ultrasonico/central", str(datos["distancia_cm"]))
        cliente_mqtt.publish(b"aurabot/sensor/luz/central", str(datos["luz_porcentaje"]))

def main():
    global cliente_mqtt
    if not comunicacion.conectar_wifi():
        return

    cliente_mqtt = comunicacion.iniciar_mqtt(procesar_comando)
    
    ultima_lectura = time.ticks_ms()
    
    while True:
        try:
            # Mantener conexión y escuchar comandos (no bloqueante)
            if cliente_mqtt:
                cliente_mqtt.check_msg()
            
            # Publicar sensores cada 2 segundos
            ahora = time.ticks_ms()
            if time.ticks_diff(ahora, ultima_lectura) >= 2000:
                resumen = sensores.obtener_resumen_sensores()
                print("Sensores:", resumen)
                publicar_telemetria(resumen)
                ultima_lectura = ahora
                
            # No dormir más de 0.1s para no bloquear la llegada de comandos
            time.sleep(0.05)
            
        except OSError:
            # En caso de desconexión MQTT
            print("Pérdida de conexión. Intentando reconectar...")
            time.sleep(5)
            cliente_mqtt = comunicacion.iniciar_mqtt(procesar_comando)

if __name__ == "__main__":
    main()
