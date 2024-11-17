from turtle import width
import flet as ft
import json
import os
from pyzbar.pyzbar import decode
import cv2
import numpy as np

INVENTARIO_FILE = "inventario.json"

def cargar_inventario():
    if os.path.exists(INVENTARIO_FILE):
        with open(INVENTARIO_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_inventario(inventario):
    with open(INVENTARIO_FILE, "w") as f:
        json.dump(inventario, f)

class BajaArticuloView(ft.Column):
    def __init__(self, on_back):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER

        # Campos y botones
        self.barra_input = ft.TextField(label="Código de Barras", expand=True)
        self.total_label = ft.Text("Total: $0.00", size=18)
        self.lista_view = ft.ListView(expand=True)

        self.confirmar_button = ft.ElevatedButton("Confirmar Baja", on_click=self.confirmar_baja)
        self.cancelar_button = ft.ElevatedButton("Cancelar", on_click=self.cancelar_baja)
        self.volver_button = ft.ElevatedButton("Volver al Menú", on_click=on_back)

        # Artículos para dar de baja
        self.articulos_para_baja = []

        # Agregar controles
        self.controls.extend([
            ft.Text("Dar de Baja", size=24, weight=ft.FontWeight.BOLD),
            self.barra_input,
            ft.ElevatedButton("Escanear Código de Barras", on_click=self.abrir_escaner),
            ft.ElevatedButton("Agregar a la Lista de Baja", on_click=self.agregar_articulo_a_lista),
            self.lista_view,
            self.total_label,
            self.confirmar_button,
            self.cancelar_button,
            self.volver_button
        ])

    def abrir_escaner(self, e):
        try:
            # Intentamos detectar si estamos en Android
            from jnius import autoclass
            from android import activity

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            BarcodeScannerActivity = autoclass('com.example.myapp.BarcodeScannerActivity')

            # Si estamos en Android, usamos la actividad nativa para escanear
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

    def agregar_articulo_a_lista(self, e):
        barra = self.barra_input.value
        if not barra:
            return

        inventario = cargar_inventario()
        for articulo in inventario:
            if str(articulo["codigo de barras"]) == barra:
                # Verificar si ya está en la lista
                for item in self.articulos_para_baja:
                    if item["articulo"]["codigo de barras"] == articulo["codigo de barras"]:
                        # Si ya está en la lista, solo actualizamos la cantidad si no hemos alcanzado el stock
                        if item["cantidad"] < articulo["cantidad"]:
                            item["cantidad"] += 1
                        self.update_lista()
                        return

                # Si no está en la lista y hay stock disponible, lo agregamos con cantidad 1
                if articulo["cantidad"] > 0:
                    self.articulos_para_baja.append({"articulo": articulo, "cantidad": 1})
                    self.update_lista()
                    return
                else:
                    ft.dialog("Error", f"No hay stock disponible para el artículo '{articulo['nombre']}'.")
                    return

    def eliminar_articulo(self, barra):
        # Eliminar artículo de la lista de baja
        self.articulos_para_baja = [item for item in self.articulos_para_baja if item["articulo"]["codigo de barras"] != barra]
        self.update_lista()

    def actualizar_cantidad(self, barra, cantidad):
        # Validación para cantidad mínima y máxima
        for item in self.articulos_para_baja:
            if item["articulo"]["codigo de barras"] == barra:
                # Asegurarse de que la cantidad sea mayor a 0
                if cantidad <= 0:
                    cantidad = 1  # La cantidad mínima permitida es 1
                articulo_stock = item["articulo"]["cantidad"]
                if cantidad > articulo_stock:
                    cantidad = articulo_stock  # No permitir más cantidad que el stock
                item["cantidad"] = cantidad
                self.update_lista()
                break


    def update_lista(self):
        # Limpiar la lista antes de agregar los artículos
        self.lista_view.controls.clear()

        for item in self.articulos_para_baja:
            # Crear un TextField para modificar la cantidad
            cantidad_input = ft.TextField(
                label="Cantidad", 
                value=str(item["cantidad"]), 
                keyboard_type="number", 
                on_blur=lambda e, barra=item["articulo"]["codigo de barras"]: self.actualizar_cantidad(barra, int(e.control.value)),
                width=120  # Ancho fijo para el campo de cantidad
            )

            # Crear el ListTile para el artículo con el nombre y la cantidad
            list_tile = ft.Row(
                controls=[
                    ft.Text(item["articulo"]["nombre"], size=16, width=200),  # Nombre del artículo
                    #ft.Text(f"Cantidad: {item['cantidad']}", size=14),  # Subtítulo de la cantidad
                ],
                alignment=ft.MainAxisAlignment.START,  # Alineación a la izquierda
                spacing=10,  # Espacio entre el nombre y la cantidad
            )

            # Crear un Row que contenga tanto el ListTile (nombre y cantidad) como los controles
            row_controls = ft.Row(
                controls=[
                    list_tile,  # Lista con el nombre y la cantidad
                    cantidad_input,  # Campo para editar la cantidad
                    ft.IconButton(ft.icons.DELETE, on_click=lambda e, barra=item["articulo"]["codigo de barras"]: self.eliminar_articulo(barra))  # Botón de eliminar
                ],
                alignment=ft.MainAxisAlignment.START,  # Alineación a la izquierda de los controles
                spacing=10,  # Espacio entre los elementos del Row
                vertical_alignment=ft.MainAxisAlignment.CENTER  # Alineación vertical centrada
            )

            # Añadir la fila de controles al ListView
            self.lista_view.controls.append(row_controls)

        self.update_total()  # Actualizamos el total después de modificar la lista



    def confirmar_baja(self, e):
        inventario = cargar_inventario()
        errores = []
        for item in self.articulos_para_baja:
            articulo = item["articulo"]
            cantidad_baja = item["cantidad"]
            for inv_articulo in inventario:
                if inv_articulo["codigo de barras"] == articulo["codigo de barras"]:
                    if cantidad_baja > inv_articulo["cantidad"]:
                        errores.append(f"La cantidad de '{articulo['nombre']}' supera el stock.")
                    else:
                        inv_articulo["cantidad"] -= cantidad_baja
                    break

        if errores:
            ft.dialog("Errores", "".join(errores))
        else:
            guardar_inventario(inventario)
            self.cancelar_baja(None)
            ft.dialog("Baja Confirmada", "Los artículos fueron dados de baja correctamente.")

    def cancelar_baja(self, e):
        self.articulos_para_baja.clear()
        self.lista_view.controls.clear()
        self.total_label.value = "Total: $0.00"
        self.update()

    def update_total(self):
        total = sum(item["cantidad"] * item["articulo"]["precio"] for item in self.articulos_para_baja)
        self.total_label.value = f"Total: ${total:.2f}"
        self.update()
