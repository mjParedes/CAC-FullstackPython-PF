import sqlite3
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


# Configurar la conexión a la base de datos SQLite
DATABASE = 'carsInventory.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Crear la tabla 'vehiculos' si no existe
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehiculos (
            carId INTEGER PRIMARY KEY,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


# Verificar si la base de datos existe, si no, crearla y crear la tabla
def create_database():
    conn = sqlite3.connect(DATABASE)
    conn.close()
    create_table()


# Programa principal
# Crear la base de datos y la tabla si no existen
create_database()


class Vehiculo:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self, carId, descripcion, cantidad, precio):
        self.carId = carId           # Código
        self.descripcion = descripcion  # Descripción
        self.cantidad = cantidad       # Cantidad disponible (stock)
        self.precio = precio           # Precio

    # Este método permite modificar un producto.

    def modificar(self, nueva_descripcion, nueva_cantidad, nuevo_precio):
        self.descripcion = nueva_descripcion  # Modifica la descripción
        self.cantidad = nueva_cantidad        # Modifica la cantidad
        self.precio = nuevo_precio            # Modifica el precio


# INVENTARIO

class Inventario:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()

    # Este método permite crear objetos de la clase "Vehiculo" y agregarlos al inventario.

    def agregar_vehiculo(self, carId, descripcion, cantidad, precio):
        producto_existente = self.consultar_vehiculo(carId)
        if producto_existente:
            return jsonify({'message': 'Ya existe un vehiculo con ese código.'}), 400

        sql = f'INSERT INTO vehiculos VALUES ({carId}, "{descripcion}", {cantidad}, {precio});'
        self.cursor.execute(sql)
        self.conexion.commit()
        return jsonify({'message': 'Vehiculo agregado correctamente.'}), 200

    # Este método permite consultar datos de vehiculos que están en el inventario
    # Devuelve el vehiculo correspondiente al código proporcionado o False si no existe.
    def consultar_vehiculo(self, carId):
        sql = f'SELECT * FROM vehiculos WHERE carId = {carId};'
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        if row:
            carId, descripcion, cantidad, precio = row
            return Vehiculo(carId, descripcion, cantidad, precio)
        return None

    # Este método permite modificar datos del vehiculo que están en el inventario
    # Utiliza el método consultar_vehiculo del inventario y modificar del vehiculo.

    def modificar_vehiculo(self, carId, nueva_descripcion, nueva_cantidad, nuevo_precio):
        producto = self.consultar_vehiculo(carId)
        if producto:
            producto.modificar(nueva_descripcion, nueva_cantidad, nuevo_precio)
            sql = f'UPDATE vehiculos SET descripcion = "{nueva_descripcion}", cantidad = {nueva_cantidad}, precio = {nuevo_precio} WHERE carId = {carId};'
            self.cursor.execute(sql)
            self.conexion.commit()
            return jsonify({'message': 'Vehiculo modificado correctamente.'}), 200
        return jsonify({'message': 'Vehiculo no encontrado.'}), 404

    # Este método elimina el producto indicado por codigo de la lista mantenida en el inventario.

    def eliminar_vehiculo(self, carId):
        sql = f'DELETE FROM vehiculos WHERE carId = {carId};'
        self.cursor.execute(sql)
        if self.cursor.rowcount > 0:
            self.conexion.commit()
            return jsonify({'message': 'Vehiculo eliminado correctamente.'}), 200
        return jsonify({'message': 'Vehiculo no encontrado.'}), 404

    # Este método imprime en la terminal una lista con los datos de los productos que figuran en el inventario.

    def listar_vehiculos(self):
        self.cursor.execute("SELECT * FROM vehiculos")
        rows = self.cursor.fetchall()
        vehiculos = []
        for row in rows:
            carId, descripcion, cantidad, precio = row
            vehiculo = {'carId': carId, 'descripcion': descripcion,
                        'cantidad': cantidad, 'precio': precio}
            vehiculos.append(vehiculo)
        return jsonify(vehiculos), 200


# CARRITO
class Carrito:

    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()
        self.items = []

    def agregar(self, carId, cantidad, inventario):
        vehiculo = inventario.consultar_producto(carId)
        if vehiculo is None:
            return jsonify({'message': 'El vehiculo no existe.'}), 404
        if vehiculo.cantidad < cantidad:
            return jsonify({'message': 'Cantidad en stock insuficiente.'}), 400

        for item in self.items:
            if item.carId == carId:
                item.cantidad += cantidad
                sql = f'UPDATE vehiculos SET cantidad = cantidad - {cantidad}  WHERE carId = {carId};'
                self.cursor.execute(sql)
                self.conexion.commit()
                return jsonify({'message': 'Vehiculo agregado al carrito correctamente.'}), 200

        nuevo_item = Vehiculo(carId, vehiculo.descripcion,
                              cantidad, vehiculo.precio)
        self.items.append(nuevo_item)
        sql = f'UPDATE vehiculos SET cantidad = cantidad - {cantidad}  WHERE carId = {carId};'
        self.cursor.execute(sql)
        self.conexion.commit()
        return jsonify({'message': 'Vehiculo agregado al carrito correctamente.'}), 200

    def quitar(self, carId, cantidad, inventario):
        for item in self.items:
            if item.carId == carId:
                if cantidad > item.cantidad:
                    return jsonify({'message': 'Cantidad a quitar mayor a la cantidad en el carrito.'}), 400
                item.cantidad -= cantidad
                if item.cantidad == 0:
                    self.items.remove(item)
                sql = f'UPDATE vehiculos SET cantidad = cantidad + {cantidad} WHERE carId = {carId};'
                self.cursor.execute(sql)
                self.conexion.commit()
                return jsonify({'message': 'Vehiculo quitado del carrito correctamente.'}), 200
        return jsonify({'message': 'El vehiculo no se encuentra en el carrito.'}), 404

    def mostrar(self):
        vehiculos_carrito = []
        for item in self.items:
            vehiculo = {'carId': item.carId, 'descripcion': item.descripcion,
                        'cantidad': item.cantidad, 'precio': item.precio}
            vehiculos_carrito.append(vehiculo)
        return jsonify(vehiculos_carrito), 200


app = Flask(__name__)
CORS(app)

carrito = Carrito()         # Instanciamos un carrito
inventario = Inventario()   # Instanciamos un inventario


# ROUTES

# Ruta para obtener el index
@app.route('/')
def index():
    return 'API de Consesionaria'

# Ruta para obtener los datos de un vehiculo según su código
@app.route('/vehiculos/<int:carId>', methods=['GET'])
def obtener_vehiculo(carId):
    vehiculo = inventario.consultar_vehiculo(carId)
    if vehiculo:
        return jsonify({
            'carId': vehiculo.carId,
            'descripcion': vehiculo.descripcion,
            'cantidad': vehiculo.cantidad,
            'precio': vehiculo.precio
        }), 200
    return jsonify({'message': 'vehiculo no encontrado.'}), 404

# Ruta para obtener la lista de vehiculos del inventario
@app.route('/vehiculos', methods=['GET'])
def obtener_vehiculos():
    return inventario.listar_vehiculos()


# Ruta para agregar un vehiculo al inventario
@app.route('/vehiculos', methods=['POST'])
def agregar_vehiculo():
    carId = request.json.get('carId')
    descripcion = request.json.get('descripcion')
    cantidad = request.json.get('cantidad')
    precio = request.json.get('precio')
    return inventario.agregar_vehiculo(carId, descripcion, cantidad, precio)


# Ruta para modificar un vehiculo del inventario
@app.route('/vehiculos/<int:carId>', methods=['PUT'])
def modificar_vehiculo(carId):
    nueva_descripcion = request.json.get('descripcion')
    nueva_cantidad = request.json.get('cantidad')
    nuevo_precio = request.json.get('precio')
    return inventario.modificar_producto(carId, nueva_descripcion, nueva_cantidad, nuevo_precio)

# Ruta para eliminar un producto del inventario


@app.route('/vehiculos/<int:carId>', methods=['DELETE'])
def eliminar_vehiculo(carId):
    return inventario.eliminar_vehiculo(carId)

# Ruta para agregar un producto al carrito


@app.route('/carrito', methods=['POST'])
def agregar_carrito():
    carId = request.json.get('carId')
    cantidad = request.json.get('cantidad')
    inventario = Inventario()
    return carrito.agregar(carId, cantidad, inventario)

# Ruta para quitar un producto del carrito


@app.route('/carrito', methods=['DELETE'])
def quitar_carrito():
    carId = request.json.get('carId')
    cantidad = request.json.get('cantidad')
    inventario = Inventario()
    return carrito.quitar(carId, cantidad, inventario)

# Ruta para obtener el contenido del carrito


@app.route('/carrito', methods=['GET'])
def obtener_carrito():
    return carrito.mostrar()


# Finalmente, si estamos ejecutando este archivo, lanzamos app.
if __name__ == '__main__':
    app.run(debug=True)
