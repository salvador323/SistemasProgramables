#config.py
# ============================================
# Proyecto:  AuraBot
# Archivo:   config_ejemplo.py
# Objetivo:  Almacenar credenciales de red y MQTT (ignorado en git)
# Equipo:    Sandoval Cuevas Pedro, Taboada Ramírez Salvador,
#            Barroso Garcia Braulio Axel (matrículas: [pendiente])
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

WIFI_SSID = "PAPUINTERNET"
WIFI_CLAVE = "Ruqv9qUxU9"

IP_BROKER = "192.168.1.95"  # La IP de la computadora que corre Mosquitto
USUARIO_MQTT = "admin"   # O vacío si configuraron allow_anonymous true
CLAVE_MQTT = "MiClave2026"       # O vacío