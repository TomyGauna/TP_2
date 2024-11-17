import flet as ft
from agregar_articulo import AgregarArticuloView
from lista_articulos import ListaArticulosView
from baja import BajaArticuloView

def create_menu_view(page, agregar_view, lista_view, baja_view, navigate):
    print("create_menu_view: Creando menú principal...")
    return ft.Column(
        controls=[
            ft.Text("Menú Principal", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Agregar Artículo", on_click=lambda _: navigate(agregar_view)),
            ft.ElevatedButton("Ver Lista de Artículos", on_click=lambda _: navigate(lista_view)),
            ft.ElevatedButton("Dar de Baja", on_click=lambda _: navigate(baja_view)),
            ft.ElevatedButton("Salir", on_click=lambda _: page.window_close())
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

def main(page: ft.Page):
    page.title = "Sistema de Inventario"
    page.window.width = 800  # Cambié window_width por window.width
    page.window.height = 600  # Cambié window_height por window.height
    page.bgcolor = ft.colors.GREY_900
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Instanciar vistas
    agregar_view = AgregarArticuloView(on_back=lambda _: navigate(menu_view))
    lista_view = ListaArticulosView(on_back=lambda _: navigate(menu_view))
    baja_view = BajaArticuloView(on_back=lambda _: navigate(menu_view))

    # Función de navegación
    def navigate(view):
        # Limpiar la vista anterior del Stack
        nav_stack.controls.clear()  # Limpia todas las vistas previas del stack
        nav_stack.controls.append(view)  # Agregar la nueva vista
        page.update()  # Actualizar la página para reflejar el cambio

        # Llamar a cargar_datos cuando la vista ListaArticulosView sea visible
        if isinstance(view, ListaArticulosView):
            view.cargar_datos()

    # Crear la vista del menú pasando la función de navegación
    menu_view = create_menu_view(page, agregar_view, lista_view, baja_view, navigate)

    # Crear un Stack para las vistas y añadir la vista del menú inicialmente
    nav_stack = ft.Stack(expand=True)
    nav_stack.controls.append(menu_view)  # Solo el menú al principio

    page.add(nav_stack)

    # Iniciar mostrando el menú
    navigate(menu_view)

if __name__ == "__main__":
    print("__main__: Iniciando la aplicación...")
    ft.app(target=main)
