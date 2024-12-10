import flet as ft
import pymysql
from datetime import datetime

print("Hola Benja")
# Conexión a la base de datos MySQL
def conectar_db():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="lara",
            cursorclass=pymysql.cursors.DictCursor  # Para obtener resultados como diccionarios
        )
    except pymysql.MySQLError as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Función para verificar si un celular ya existe y obtener los productos asociados
def verificar_celular_existe(celular):
    conexion = conectar_db()
    if not conexion:
        return []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombre
            FROM clientes c
            JOIN compras co ON c.id = co.cliente_id
            JOIN productos p ON co.producto_id = p.id
            WHERE c.celular = %s
        """, (celular,))
        resultado = cursor.fetchall()
    conexion.close()
    return resultado

# Función para obtener todos los productos que un cliente ha comprado
def obtener_compras_cliente(celular):
    conexion = conectar_db()
    if not conexion:
        return []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombre
            FROM clientes c
            JOIN compras co ON c.id = co.cliente_id
            JOIN productos p ON co.producto_id = p.id
            WHERE c.celular = %s
        """, (celular,))
        productos = cursor.fetchall()
    conexion.close()
    return productos

# Función para agregar registros a la base de datos con fecha de compra
def agregar_registro_db(nombre_apellido, producto, celular):
    conexion = conectar_db()
    if not conexion:
        print("No se pudo establecer conexión con la base de datos.")
        return
    with conexion.cursor() as cursor:
        # Insertar o obtener el cliente
        cursor.execute("SELECT id FROM clientes WHERE celular = %s", (celular,))
        cliente = cursor.fetchone()
        if not cliente:
            cursor.execute("INSERT INTO clientes (nombre_apellido, celular) VALUES (%s, %s)", (nombre_apellido, celular))
            cliente_id = cursor.lastrowid
        else:
            cliente_id = cliente['id']
        
        # Insertar o obtener el producto
        cursor.execute("SELECT id FROM productos WHERE nombre = %s", (producto,))
        producto_existente = cursor.fetchone()
        if not producto_existente:
            cursor.execute("INSERT INTO productos (nombre) VALUES (%s)", (producto,))
            producto_id = cursor.lastrowid
        else:
            producto_id = producto_existente['id']
        
        # Registrar la compra
        cursor.execute("INSERT INTO compras (cliente_id, producto_id) VALUES (%s, %s)", (cliente_id, producto_id))
        conexion.commit()
    conexion.close()

# Función para obtener el stock actual
def obtener_stock():
    conexion = conectar_db()
    if not conexion:
        return []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombre, COUNT(co.id) as cantidad
            FROM productos p
            LEFT JOIN compras co ON p.id = co.producto_id
            GROUP BY p.id
            ORDER BY cantidad DESC
        """)
        stock = cursor.fetchall()
    conexion.close()
    return stock

# Función principal de Flet
def main(page: ft.Page):
    page.title = "Distribuidora Cobra"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def ver_stock(e):
        stock = obtener_stock()
        stock_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cantidad")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["nombre"])),
                    ft.DataCell(ft.Text(str(item["cantidad"]))),
                ]) for item in stock
            ],
        )
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Stock Actual"),
            content=stock_table,
            actions=[ft.TextButton("Cerrar", on_click=close_dialog)],
        )
        page.dialog.open = True
        page.update()

    def mostrar_form_compra(e):
        page.clean()
        page.add(
            ft.Text("Añadir Compra", size=20, weight=ft.FontWeight.BOLD),
            nombre_apellido_input,
            celular_input,
            producto_input,
            ft.ElevatedButton("Agregar Registro", on_click=agregar_registro),
            ft.ElevatedButton("Volver", on_click=mostrar_pantalla_principal),
        )

    def agregar_registro(e):
        nombre_apellido = nombre_apellido_input.value
        producto = producto_input.value
        celular = celular_input.value
        
        if nombre_apellido and producto and celular:
            productos_existentes = verificar_celular_existe(celular)
            if productos_existentes:
                def mostrar_lista_compras(e):
                    productos_cliente = obtener_compras_cliente(celular)
                    lista_compras = ft.Column()
                    for producto in productos_cliente:
                        lista_compras.controls.append(ft.Text(f"Producto: {producto['nombre']}"))
                    lista_compras.controls.append(ft.Text(f"Datos del Cliente: {nombre_apellido} - Celular: {celular}"))
                    
                    def close_historial_dialog(e):
                        page.dialog.open = False
                        page.update()

                    page.dialog = ft.AlertDialog(
                        title=ft.Text("Historial de Compras"),
                        content=lista_compras,
                        actions=[ft.TextButton("Cerrar", on_click=close_historial_dialog)],
                    )
                    page.dialog.open = True
                    page.update()
                
                def close_warning_dialog(e):
                    page.dialog.open = False
                    page.update()

                productos_str = ", ".join([p["nombre"] for p in productos_existentes])
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Advertencia"),
                    content=ft.Text(f"Este usuario ya ha comprado: {productos_str}."),
                    actions=[
                        ft.TextButton("OK", on_click=close_warning_dialog),
                        ft.TextButton("Lista", on_click=mostrar_lista_compras)
                    ],
                )
                page.dialog.open = True
                page.update()

            agregar_registro_db(nombre_apellido, producto, celular)
            nombre_apellido_input.value = ""
            producto_input.value = ""
            celular_input.value = ""
            page.update()

    def mostrar_pantalla_principal(e=None):
        page.clean()
        page.add(
            ft.Text("Bienvenidos a la página oficial de la distribuidora Cobra", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("Ver Stock Actual", on_click=ver_stock),
                ft.ElevatedButton("Añadir Compra", on_click=mostrar_form_compra),
            ], alignment=ft.MainAxisAlignment.CENTER),
        )

    nombre_apellido_input = ft.TextField(label="Nombre y Apellido", width=300)
    celular_input = ft.TextField(label="Número de Celular", width=300)
    producto_input = ft.TextField(label="Qué Compró", width=300)

    mostrar_pantalla_principal()

ft.app(target=main)
