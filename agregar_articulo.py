import flet as ft
import json
import os
from pyzbar.pyzbar import decode
import cv2
import numpy as np

INVENTARIO_FILE = "inventario.json"

def guardar_inventario(inventario):
    with open(INVENTARIO_FILE, "w") as f:
        json.dump(inventario, f)

def cargar_inventario():
    if os.path.exists(INVENTARIO_FILE):
        with open(INVENTARIO_FILE, "r") as f:
            return json.load(f)
    return []

class AgregarArticuloView(ft.Column):
    def __init__(self, on_back):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER

        # Inputs
        self.nombre_input = ft.TextField(label="Nombre del artículo", expand=True)
        self.cantidad_input = ft.TextField(label="Cantidad", expand=True, keyboard_type=ft.KeyboardType.NUMBER)
        self.precio_input = ft.TextField(label="Precio", expand=True, keyboard_type=ft.KeyboardType.NUMBER)
        self.barra_input = ft.TextField(label="Código de Barras", expand=True)

        # Botones
        self.escanear_button = ft.ElevatedButton("Escanear Código de Barras", on_click=self.abrir_escaner)
        self.agregar_button = ft.ElevatedButton("Agregar Artículo", on_click=self.agregar_articulo)
        self.volver_button = ft.ElevatedButton("Volver al Menú", on_click=on_back)

        # Agregar controles
        self.controls.extend([
            ft.Text("Agregar Artículo", size=24, weight=ft.FontWeight.BOLD),
            self.nombre_input,
            self.cantidad_input,
            self.precio_input,
            self.barra_input,
            self.escanear_button,
            self.agregar_button,
            self.volver_button
        ])

    def abrir_escaner(self, e):
        try:
            # Verificamos si estamos en Android
            from jnius import autoclass
            from android import activity

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            BarcodeScannerActivity = autoclass('com.example.myapp.BarcodeScannerActivity')

            # Si estamos en Android, usamos la actividad de escaneo nativa
            intent = Intent(PythonActivity.mActivity, BarcodeScannerActivity)
            PythonActivity.mActivity.startActivityForResult(intent, 1)

        except ImportError:
            # Si no estamos en Android, usamos OpenCV para escanear en PC
            self.iniciar_escaneo_pc()

    def iniciar_escaneo_pc(self):
        # En el escritorio, usamos OpenCV para acceder a la cámara
        cap = cv2.VideoCapture(0)  # Abrir la cámara

        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return

        while True:
            ret, frame = cap.read()

            if not ret:
                print("No se pudo obtener un frame de la cámara")
                break

            # Detectar los códigos de barras en el frame
            decoded_objects = decode(frame)

            for obj in decoded_objects:
                # Dibujar el rectángulo alrededor del código de barras
                pts = obj.polygon
                if len(pts) == 4:
                    pts = [(int(point[0]), int(point[1])) for point in pts]
                    cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 2)
                else:
                    center = (int(obj.rect.left + obj.rect.width / 2), int(obj.rect.top + obj.rect.height / 2))
                    cv2.circle(frame, center, 5, (0, 0, 255), 2)

                # Extraer el texto del código de barras y asignarlo al input
                barcode_data = obj.data.decode("utf-8")
                self.barra_input.value = barcode_data
                self.update()  # Actualizar la vista con el código escaneado

                # Detener el escaneo después de leer un código de barras
                cap.release()
                cv2.destroyAllWindows()
                return

            # Mostrar el frame en una ventana
            cv2.imshow("Escáner de Código de Barras", frame)

            # Salir del loop si se presiona 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def agregar_articulo(self, e):
        nombre = self.nombre_input.value
        cantidad = self.cantidad_input.value
        precio = self.precio_input.value
        barra = self.barra_input.value

        if nombre and cantidad.isdigit() and precio.isdigit():
            nuevo_articulo = {
                "nombre": nombre,
                "cantidad": int(cantidad),
                "precio": float(precio),
                "codigo de barras": barra
            }
            inventario = cargar_inventario()
            inventario.append(nuevo_articulo)
            guardar_inventario(inventario)

            # Limpiar los campos
            self.nombre_input.value = ""
            self.cantidad_input.value = ""
            self.precio_input.value = ""
            self.barra_input.value = ""
            self.update()
