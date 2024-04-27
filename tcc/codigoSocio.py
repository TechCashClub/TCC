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
    nombre_socio = db.Column(db.String(80), unique=True, nullable=False)
    apellidos_socio = db.Column(db.String(80), unique=True, nullable=False)
    edad_socio = db.Columb(db.Integer, nullable=False)
    direccion_de_entrega = db.Column(db.String(200), nullable=False)
    codigo_postal = db.Columb(db.Integer, nullable=False)
    localidad = db.Column(db.String(80), nullable=False)
    provincia = db.Column(db.String(80), nullable=False)
    telefono = db.Columb(db.Integer, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    login = db.Column(db.Text, nullable=False)
    passwd = db.Column(db.Text, nullable=False)
    fondo = db.Columb(db.Integer, nullable=False)
    
    def __init__(self, id_socio, nombre_socio, apellido_socio, edad_socio, direccion_de_entrega, codigo_postal, localidad, provincia, telefono, email, login, passwd, fondo): #Método constructor de la clase socio
        
        self.id_socio = id_socio
        self.nombre_socio = nombre_socio
        self.apellidos_socio = apellido_socio
        self.edad_socio = edad_socio
        self.direccion_de_entrega = direccion_de_entrega
        self.codigo_postal = codigo_postal
        self.localidad = localidad
        self.provincia = provincia
        self.telefono = telefono
        self.email = email
        self.login = login
        self.passwd = passwd
        self.fondo = fondo
        
    def __repr__(self):
        
        return f'Socio: {self.nombre_socio} {self.apellidos_socio}, {self.edad_socio} años, dirección: {self.direccion_de_entrega} - {self.codigo_postal} {self.localidad} ({self.provincia}), teléfono: {self.telefono}, correo electrónico: {self.email}.'
    
    def registro(self, nombre_socio, login, passwd):
        self.nombre_socio = nombre_socio
        self.login = login
        self.passwd = passwd
        return f'{self.nombre_socio} se ha registrado como socio con el login {self.login} y el password {self.passwd}.'
    
    def logueo(self):
        pass
    
    def recuperacion(self, email, passwd):
        pass
    
    def cerrar_sesion(self, login, passwd):
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