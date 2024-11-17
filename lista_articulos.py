import flet as ft
import json
import os

INVENTARIO_FILE = "inventario.json"

def cargar_inventario():
    if os.path.exists(INVENTARIO_FILE):
        with open(INVENTARIO_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_inventario(inventario):
    with open(INVENTARIO_FILE, "w") as f:
        json.dump(inventario, f, indent=4)

class ListaArticulosView(ft.Column):
    def __init__(self, on_back):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.START

        # Título
        self.title = ft.Text("Lista de Artículos", size=24, weight=ft.FontWeight.BOLD)

        # Contenedor para la lista
        self.list_view = ft.ListView(expand=True)

        # Botón volver
        self.volver_button = ft.ElevatedButton("Volver al Menú", on_click=on_back)

        # Agregar controles
        self.controls.extend([self.title, self.list_view, self.volver_button])
        print("ListaArticulosView: Controles iniciales agregados.")

    def cargar_datos(self):
        print("ListaArticulosView: Cargando datos...")
        inventario = cargar_inventario()
        print("ListaArticulosView: Datos cargados del inventario:", inventario)

        self.list_view.controls.clear()
        if inventario:
            for articulo in inventario:
                print("ListaArticulosView: Añadiendo artículo a la lista:", articulo)

                # Usamos un Row para alinear el nombre y los botones horizontalmente
                articulo_row = ft.Row(
                    controls=[
                        ft.Text(articulo["nombre"], size=16, width=200),  # Nombre del artículo
                        ft.Text(f"Cantidad: {articulo['cantidad']}", size=14),  # Cantidad del artículo
                        ft.Text(f"Precio: ${articulo['precio']:.2f}", size=14),  # Precio del artículo
                        ft.IconButton(ft.icons.DELETE, on_click=lambda _, a=articulo: self.eliminar_articulo(a)),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,  # Alineación vertical centrada
                )

                # Añadir el Row a la lista de artículos
                self.list_view.controls.append(articulo_row)

        else:
            print("ListaArticulosView: No hay artículos en el inventario.")
            self.list_view.controls.append(
                ft.Text("No hay artículos en el inventario.", color=ft.colors.RED)
            )

        # Se realiza la actualización de la vista solo después de haber sido añadida
        self.update()
        print("ListaArticulosView: Vista actualizada.")

    def eliminar_articulo(self, articulo):
        print(f"ListaArticulosView: Eliminando artículo {articulo}")
        # Confirmar eliminación
        def confirmar_eliminacion(confirmar):
            if confirmar:
                inventario = cargar_inventario()
                inventario = [a for a in inventario if a["codigo de barras"] != articulo["codigo de barras"]]
                guardar_inventario(inventario)
                print(f"ListaArticulosView: Artículo {articulo['nombre']} eliminado.")
            
            # Volver a la lista de artículos
            self.cargar_lista_principal()

        # Mostrar confirmación de eliminación
        confirmacion_view = ft.Column(
            controls=[ 
                ft.Text("¿Seguro que quieres eliminar este artículo?", size=20),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Sí", on_click=lambda _: confirmar_eliminacion(True)),
                        ft.ElevatedButton("No", on_click=lambda _: confirmar_eliminacion(False)),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,  # Espacio entre los botones
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,  # Ajustar el espacio entre los controles
        )
        self.controls.clear()
        self.controls.append(confirmacion_view)
        self.update()

    def cargar_lista_principal(self):
        """
        Limpia la pantalla y vuelve a agregar los controles principales
        """
        print("ListaArticulosView: Regresando a la lista principal.")
        self.controls.clear()
        self.controls.extend([self.title, self.list_view, self.volver_button])
        self.cargar_datos()
        self.update()
