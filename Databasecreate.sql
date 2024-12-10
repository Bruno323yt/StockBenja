-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS lara;
-- Usar la base de datos
USE lara;
-- Crear la tabla para almacenar los registros de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_apellido VARCHAR(255) NOT NULL,
    celular VARCHAR(20) NOT NULL,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_celular (celular)
);
-- Crear una tabla separada para los productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    stock INT DEFAULT 0,
    -- Nueva columna para gestionar el stock
    UNIQUE INDEX idx_nombre (nombre)
);
-- Crear una tabla para las compras (relación entre clientes y productos)
CREATE TABLE IF NOT EXISTS compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    producto_id INT NOT NULL,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    INDEX idx_fecha_compra (fecha_compra)
);
-- Agregar algunos productos de ejemplo con stock inicial
INSERT INTO productos (nombre, stock)
VALUES ('Producto A', 50),
    ('Producto B', 30),
    ('Producto C', 20);