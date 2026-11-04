# Tabla de Abstracción de Hardware (HAL)

| Componente | Tipo | Pin ESP32 | Tópico publicación | Tópico suscripción | Unidad | Rango |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| PIR (HC-SR501) | Sensor | [pendiente] | aurabot/sensor/pir/central | --- | 1/0 (Presencia) | [pendiente] |
| Ultrasónico (HC-SR04) | Sensor | [pendiente] | aurabot/sensor/ultrasonico/central | --- | cm | [pendiente] |
| Luz (LDR) | Sensor | [pendiente] | aurabot/sensor/luz/central | --- | % | [pendiente] |
| Servomotor (SG90) | Actuador | [pendiente] | aurabot/actuador/servo/central | aurabot/comando/servo/central | Grados (Texto) | [pendiente] |
| Relevador (1 Canal) | Actuador | [pendiente] | aurabot/actuador/relevador/central | aurabot/comando/relevador/central | 1/0 (Texto) | [pendiente] |
| Pantalla OLED | Actuador | [pendiente] | aurabot/actuador/oled/central | aurabot/comando/oled/central | Expresión | [pendiente] |
| ESP32-CAM | Cámara | --- | aurabot/sensor/camara/cam | --- | JPEG (Bytes) | --- |