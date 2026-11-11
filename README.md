# AuraBot — Asistente Interactivo de Escritorio
  
**Semestre:** ago-dic-2026  
**Materia:** Sistemas Programables — ISC TecNM León  

### Integrantes:
| Nombre | Matrícula | Rol | GitHub |
| :--- | :--- | :--- | :--- |
| Sandoval Cuevas Pedro | 23240325 | 🔧 Firmware ESP32 | [Pedro384e](https://github.com/) |
| Taboada Ramírez Salvador | 23240999 | 🧠 Servidor Python/IA | [salvador323](https://github.com/) |
| Barroso Garcia Braulio Axel | 23240327 | ☁️ Firebase / 🔩 Hardware | [AxelCuber15](https://github.com/) |

---

## Descripción General
AuraBot es un Sistema Inteligente de Monitoreo Ergonómico y Asistencia Cognitiva diseñado para la intervención temprana de estrés y malas posturas en entornos de trabajo remoto.

- **¿A quién ayuda?** A estudiantes universitarios de ingeniería y profesionales del sector tecnológico que enfrentan jornadas extensas frente al monitor en condiciones de aislamiento.
- **¿Qué problema resuelve?** Combate la incidencia de fatiga mental, estrés académico y episodios de ansiedad silenciosa, así como la disminución del rendimiento cognitivo por malas posturas y la falta de pausas activas.
- **¿Cómo lo resuelve de forma diferente a lo que ya existe?** Mediante Edge Computing. El sistema evalúa la biometría facial en memoria volátil (garantizando total privacidad sin subir fotos a la nube) y la postura física. Al detectar alteraciones, despliega un protocolo físico de *grounding*: activa iluminación terapéutica, reproduce estímulos auditivos guiados y marca ritmos de respiración visuales y mecánicos para evitar que la ansiedad escale a episodios críticos.

---

## Arquitectura del Sistema
![Diagrama de Arquitectura](../hardware/esquematico.png) 
*(Nota: Actualizar con la imagen final del diagrama de flujo)*

### Tópicos MQTT
| Tópico | Dirección | Descripción |
| :--- | :--- | :--- |
| `aurabot/sensor/pir/central` | ESP32 → Broker | Lectura binaria de presencia (PIR) |
| `aurabot/sensor/ultrasonico/central` | ESP32 → Broker | Distancia en centímetros |
| `aurabot/sensor/luz/central` | ESP32 → Broker | Nivel de iluminación en porcentaje |
| `aurabot/cam/frame` | ESP32-CAM → Broker | Transmisión de frames de video |
| `aurabot/comando/relevador/central` | Broker → ESP32 | Comando "encender" / "apagar" |
| `aurabot/comando/servo/central` | Broker → ESP32 | Comando "saludar" / "reposo" |
| `aurabot/comando/oled/central` | Broker → ESP32 | Comando "feliz" / "neutral" / "apagada" |

---

## Hardware

| # | Componente | Tipo | Cantidad | Costo aprox. MXN |
| :--- | :--- | :--- | :--- | :--- |
| 1 | ESP32 DevKit V1 | Microcontrolador | 1 | $120 |
| 2 | ESP32-CAM | Cámara / Visión | 1 | $130 |
| 3 | Sensor PIR (HC-SR501) | Sensor | 1 | $45 |
| 4 | Ultrasónico (HC-SR04) | Sensor | 1 | $40 |
| 5 | Fotorresistencia (LDR) | Sensor | 1 | $15 |
| 6 | Servomotor SG90 | Actuador | 1 | $55 |
| 7 | Pantalla OLED SSD1306 | Actuador | 1 | $70 |
| 8 | Relevador 5V (1 Canal) | Actuador | 1 | $35 |
| **Total** | | | | **< $600 MXN** |

### Diagrama de conexiones
![Circuito Protoboard](../media/circuito_protoboard.jpg)

---

## Software y Firmware

**Requisitos del servidor Python**
```bash
pip install -r servidor/requirements.txt
