import flet as ft
import pymysql


# Función para conectar con la base de datos
def conectar_db():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="lara",
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None


# Función para obtener la lista de productos
def obtener_productos():
    conexion = conectar_db()
    if not conexion:
        return []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM productos")
            productos = cursor.fetchall()
        return productos
    except pymysql.MySQLError as err:
        print(f"Error al obtener productos: {err}")
        return []
    finally:
        conexion.close()


# Función para obtener el stock actual
def obtener_stock():
    conexion = conectar_db()
    if not conexion:
        return []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT nombre, stock FROM productos")
            stock = cursor.fetchall()
        return stock
    except pymysql.MySQLError as err:
        print(f"Error al obtener el stock: {err}")
        return []
    finally:
        conexion.close()


# Función para actualizar el stock de un producto
def actualizar_stock(producto_id, cantidad):
    conexion = conectar_db()
    if not conexion:
        print("No se pudo establecer conexión con la base de datos.")
        return
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE productos
                SET stock = stock + %s
                WHERE id = %s
                """,
                (cantidad, producto_id)
            )
            conexion.commit()
    except pymysql.MySQLError as err:
        print(f"Error al actualizar el stock: {err}")
    finally:
        conexion.close()


# Función principal de Flet
def main(page: ft.Page):
    page.title = "Distribuidora Cobra"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Función para abrir un diálogo de forma segura
    def abrir_dialogo(dialog):
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Función para cerrar un diálogo
    def cerrar_dialogo(dialog):
        dialog.open = False
        if dialog in page.overlay:
            page.overlay.remove(dialog)
        page.update()

    # Función para procesar una compra
    def realizar_compra(e):
        producto_id = int(producto_dropdown.value)
        cantidad = int(cantidad_input.value)

        if not producto_id or not cantidad:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, selecciona un producto e ingresa una cantidad válida."))
            page.snack_bar.open = True
            page.update()
            return

        actualizar_stock(producto_id, cantidad)
        page.snack_bar = ft.SnackBar(ft.Text("Compra registrada exitosamente."))
        page.snack_bar.open = True
        cantidad_input.value = ""
        page.update()

    # Función para procesar una venta
    def realizar_venta(e):
        producto_id = int(producto_dropdown.value)
        cantidad = int(cantidad_input.value)

        if not producto_id or not cantidad:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, selecciona un producto e ingresa una cantidad válida."))
            page.snack_bar.open = True
            page.update()
            return

        # Restar la cantidad del stock
        actualizar_stock(producto_id, -cantidad)
        page.snack_bar = ft.SnackBar(ft.Text("Venta registrada exitosamente."))
        page.snack_bar.open = True
        cantidad_input.value = ""
        page.update()

    # Función para mostrar el formulario de compra o venta
    def mostrar_formulario(tipo):
        productos = obtener_productos()
        if not productos:
            page.snack_bar = ft.SnackBar(ft.Text("No hay productos disponibles."))
            page.snack_bar.open = True
            return

        # Crear menú desplegable de productos
        opciones_productos = [
            ft.dropdown.Option(str(producto["id"]), text=producto["nombre"]) for producto in productos
        ]
        producto_dropdown.options = opciones_productos

        # Configurar acción según el tipo (compra o venta)
        if tipo == "compra":
            titulo = "Registrar Compra"
            accion = realizar_compra
        elif tipo == "venta":
            titulo = "Registrar Venta"
            accion = realizar_venta

        page.clean()
        page.add(
            ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD),
            producto_dropdown,
            cantidad_input,
            ft.ElevatedButton(titulo, on_click=accion),
            ft.ElevatedButton("Volver", on_click=mostrar_pantalla_principal),
        )

    # Función para mostrar la pantalla principal
    def mostrar_pantalla_principal(e=None):
        page.clean()
        page.add(
            ft.Text("Bienvenidos a la página oficial de la distribuidora Cobra", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("Registrar Compra", on_click=lambda e: mostrar_formulario("compra")),
                ft.ElevatedButton("Registrar Venta", on_click=lambda e: mostrar_formulario("venta")),
                ft.ElevatedButton("Ver Stock", on_click=ver_stock),
            ], alignment=ft.MainAxisAlignment.CENTER),
        )

    # Configuración inicial de elementos reutilizables
    producto_dropdown = ft.Dropdown(label="Seleccionar Producto", width=300)
    cantidad_input = ft.TextField(label="Cantidad", width=300)

    # Función para mostrar el stock actual
    def ver_stock(e):
        stock = obtener_stock()

        if not stock:
            page.snack_bar = ft.SnackBar(ft.Text("No hay productos disponibles en el stock."))
            page.snack_bar.open = True
            return

        stock_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cantidad")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["nombre"])),
                    ft.DataCell(ft.Text(str(item["stock"]))),
                ]) for item in stock
            ],
        )

        dialogo_stock = ft.AlertDialog(
            title=ft.Text("Stock Actual"),
            content=stock_table,
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(dialogo_stock)),
            ],
        )
        abrir_dialogo(dialogo_stock)

    # Mostrar la pantalla principal al inicio
    mostrar_pantalla_principal()


ft.app(target=main)
