# ============================================
# Proyecto:  AuraBot
# Archivo:   dispositivos.py (HAL)
# Objetivo:  Abstracción de hardware para sensores y actuadores
# Equipo:    Sandoval Cuevas Pedro, Taboada Ramírez Salvador,
#            Barroso Garcia Braulio Axel
# Matrículas: 23240325, 23240999, 23240327
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

from machine import Pin, PWM, ADC, I2C, time_pulse_us
import time
import ssd1306

class GestorSensores:
    def __init__(self):
        # PIR en GPIO 13
        self.pir = Pin(13, Pin.IN)
        # HC-SR04 en GPIO 26 (Trig) y 25 (Echo)
        self.trig = Pin(26, Pin.OUT)
        self.echo = Pin(25, Pin.IN)
        # LDR en GPIO 34
        self.ldr = ADC(Pin(34))
        self.ldr.atten(ADC.ATTN_11DB) # Rango 0-3.3V
        
        # Historial para promedio móvil (últimas 5 lecturas)
        self.historial_distancia = [0] * 5
        self.historial_luz = [0] * 5
        self.indice = 0

    def medir_distancia(self):
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        duracion = time_pulse_us(self.echo, 1, 30000)
        if duracion > 0:
            return (duracion * 0.0343) / 2
        return -1

    def actualizar_promedios(self):
        dist_actual = self.medir_distancia()
        luz_actual = self.ldr.read()
        
        if dist_actual > 0:
            self.historial_distancia[self.indice] = dist_actual
        self.historial_luz[self.indice] = luz_actual
        
        self.indice = (self.indice + 1) % 5

    def obtener_resumen_sensores(self):
        """Lee hardware, calcula promedios y devuelve valores interpretados."""
        self.actualizar_promedios()
        distancia_promedio = sum(self.historial_distancia) / 5
        # Convertir ADC (0-4095) a porcentaje (0-100%)
        luz_promedio = sum(self.historial_luz) / 5
        luz_porcentaje = int((luz_promedio / 4095.0) * 100)
        
        return {
            "pir": self.pir.value(), # 1 o 0
            "distancia_cm": round(distancia_promedio, 1),
            "luz_porcentaje": luz_porcentaje
        }

class GestorActuadores:
    def __init__(self):
        # Relevador en GPIO 23 (Activo en HIGH por defecto, cambiar si es LOW)
        self.relevador = Pin(23, Pin.OUT)
        self.relevador_activo_alto = False 
        
        # Servo en GPIO 18 (PWM a 50Hz)
        self.servo = PWM(Pin(18), freq=50)
        
        # OLED en I2C (SDA 21, SCL 22)
        try:
            self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
            self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
            self.oled_disponible = True
        except:
            self.oled_disponible = False
            
        self.estado_seguro()

    def controlar_relevador(self, estado):
        """Recibe 'encender' o 'apagar'"""
        if estado == "encender":
            self.relevador.value(1 if self.relevador_activo_alto else 0)
        else:
            self.relevador.value(0 if self.relevador_activo_alto else 1)

    def controlar_servo(self, comando):
        """Recibe 'saludar' o 'reposo' (rango 60 a 120 grados)"""
        if comando == "saludar":
            # Movimiento rápido de saludo simulado (60 a 120)
            self.mover_servo(60)
            time.sleep(0.3)
            self.mover_servo(120)
        else:
            self.mover_servo(90) # Reposo al centro

    def mover_servo(self, grados):
        min_ns = 500000
        max_ns = 2400000
        grados = max(60, min(120, grados)) # Limitar para no forzar cartón
        ns = int(min_ns + (grados / 180) * (max_ns - min_ns))
        self.servo.duty_ns(ns)

    def controlar_oled(self, expresion):
        """Recibe 'feliz', 'neutral' o 'apagada'"""
        if not self.oled_disponible: return
        self.oled.fill(0)
        if expresion == "feliz":
            self.oled.text("^   ^", 40, 20)
            self.oled.text("\\___/", 40, 40)
        elif expresion == "neutral":
            self.oled.text("-   -", 40, 20)
            self.oled.text(" --- ", 40, 40)
        self.oled.show()

    def estado_seguro(self):
        """Apaga componentes y centra motores."""
        self.controlar_relevador("apagar")
        self.controlar_servo("reposo")
        self.controlar_oled("neutral")