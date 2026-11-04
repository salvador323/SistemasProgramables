# ============================================
# Proyecto:  AuraBot
# Archivo:   detector_rostro.py
# Objetivo:  Detectar presencia de un rostro usando modelo SSD de OpenCV
# Equipo:    Sandoval Cuevas Pedro, Taboada Ramírez Salvador,
#            Barroso Garcia Braulio Axel (matrículas: [pendiente])
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# MODELO:                 ResNet-10 SSD (Caffe)
# PREDICCIÓN:             Clasificación binaria (Rostro detectado / No detectado)
# PRECISIÓN APROXIMADA:   [pendiente]%
# RECALL APROXIMADO:      [pendiente]%
# ============================================

import cv2
import os
import numpy as np

class DetectorRostro:
    def __init__(self, ruta_prototxt, ruta_modelo, umbral_confianza=0.7):
        """
        Inicializa el modelo de red neuronal.
        Recibe: Rutas a los archivos de configuración (.prototxt) y pesos (.caffemodel).
        Hace: Carga el modelo SSD en memoria.
        Devuelve: Objeto de la clase DetectorRostro.
        """
        self.umbral = umbral_confianza
        self.red_neuronal = cv2.dnn.readNetFromCaffe(ruta_prototxt, ruta_modelo)

    def analizar_imagen(self, imagen):
        """
        Procesa una imagen para buscar rostros.
        Recibe: Matriz de imagen (numpy array de OpenCV).
        Hace: Convierte la imagen a un blob, la pasa por la red neuronal y cuenta las detecciones válidas.
        Devuelve: Booleano (True si hay al menos un rostro con confianza > umbral, False en caso contrario).
        """
        (alto, ancho) = imagen.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(imagen, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        
        self.red_neuronal.setInput(blob)
        detecciones = self.red_neuronal.forward()
        
        for i in range(0, detecciones.shape[2]):
            confianza = detecciones[0, 0, i, 2]
            if confianza > self.umbral:
                return True
        return False

def validar_modelo():
    """
    Ejecuta una prueba del modelo con imágenes estáticas para calcular precisión.
    Recibe: Nada.
    Hace: Lee imágenes de 'datos_validacion/', las analiza y calcula verdaderos positivos (VP), 
          falsos positivos (FP), etc.
    Devuelve: Nada (Imprime los resultados en consola).
    """
    carpeta_base = "datos_validacion"
    # Nota: El equipo debe crear manualmente las subcarpetas 'con_rostro' y 'sin_rostro' 
    # dentro de 'datos_validacion/' y poner ahí algunas fotos para correr esta prueba.
    
    detector = DetectorRostro(
        ruta_prototxt="modelos/deploy.prototxt", 
        ruta_modelo="modelos/res10_300x300_ssd_iter_140000.caffemodel"
    )
    
    vp, vn, fp, fn = 0, 0, 0, 0

    print("Iniciando validación del modelo...")
    
    # Evaluar imágenes con rostro (Esperado: True)
    ruta_con = os.path.join(carpeta_base, "con_rostro")
    if os.path.exists(ruta_con):
        for archivo in os.listdir(ruta_con):
            imagen = cv2.imread(os.path.join(ruta_con, archivo))
            if imagen is not None:
                if detector.analizar_imagen(imagen): vp += 1
                else: fn += 1

    # Evaluar imágenes sin rostro (Esperado: False)
    ruta_sin = os.path.join(carpeta_base, "sin_rostro")
    if os.path.exists(ruta_sin):
        for archivo in os.listdir(ruta_sin):
            imagen = cv2.imread(os.path.join(ruta_sin, archivo))
            if imagen is not None:
                if not detector.analizar_imagen(imagen): vn += 1
                else: fp += 1

    total = vp + vn + fp + fn
    if total > 0:
        precision = vp / (vp + fp) if (vp + fp) > 0 else 0
        recall = vp / (vp + fn) if (vp + fn) > 0 else 0
        print(f"Total imágenes: {total}")
        print(f"Precisión: {precision * 100:.2f}%")
        print(f"Recall: {recall * 100:.2f}%")
        print("¡Anota estos valores en el encabezado del archivo y reemplaza los [pendiente]!")
    else:
        print("No se encontraron imágenes de prueba en la carpeta 'datos_validacion/'.")

if __name__ == "__main__":
    validar_modelo()