from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#Configurar la URI de la base de datos

app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)    # Crear el objeto db de la clase SQLAlchemy que recibe como parámetro app

#Definición de un modelo simple, por ejemplo la clase Socio...>

class Socio(db.model):
    
    id_socio = db.Column(db.Integer, primary_key=True) # crea las columnas para los registros de la DB
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    apellido = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)
    
    def __init__(self, id_socio, nombre, apellido, email, password, username): #Método constructor de la clase socio
        
        self.id_socio = id_socio
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password = password
        self.username = username
        
    def __repr__(self):
        
        return f'Socio: {self.nombre} {self.apellido}, correo electrónico: {self.email}.'
    
    def registro(self, nombre, username, password):
        self.nombre = nombre
        self.username = username
        self.password = password
        return f'{self.nombre} se ha registrado como socio con el login {self.username} y el password {self.password}.'
    
    def logueo(self):
        pass
    
    def recuperacion(self, email, password):
        pass
    
    def cerrar_sesion(self, username, password):
        pass
    
    def proponer_productos(self, Producto.nombre, Producto.caracteristicas, Producto.imagen):
        pass
    
    def fondos(self, fondo):
        pass
    
    def seleccionar_transaccion(self, id_socio, fondo, Transaccion.identificador, Producto.identificador, Producto.nombre, Producto.caracteristicas, Fabricante.identificador, Fabricante.nombre, Fabricante.marca):
        pass
    
    
    """ Esto es el ORM (Mapeo relacional de objetos) > traducir las clases y objetos a tablas y registros de la base de datos SQL.

        BASE DE DATOS DEL CLUB
    
                            TABLA SOCIOS = class Socio                      TABLA PRODUCTOS = class Producto
            
                    id_socio   nombre_socio  apellido_socio ... COLUMNAS
FILA (Registros)        01         Juan           Jiménez = objeto de Socio
                        02         Pepe           García
                        ...
    
    

"""

#Aplicación con las rutas y las vistas...>

@app.route('/') # La ruta
def index(): # La vista
    return "Hola mundo"

db.create_all() # Crea las tablas en la base de datos
app.run(debug=True)