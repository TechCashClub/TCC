from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import os

load_dotenv()  #Carga las variables de entorno desde .env

#database_url = os.getenv('DATABASE_URL')



app = Flask(__name__)

#Configurar la URI de la base de datos

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

#Definición de clases: ----------------------------------------------------------------------------------------------

class Admin(db.Model):
    id_admin = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    #productos = db.relationship('Producto', backref='admin', lazy=True)

# Tabla de asociación para la relación N:N entre Socios y Productos
socios_productos = db.Table('socios_productos',
    db.Column('id_socio', db.Integer, db.ForeignKey('socio.id_socio'), primary_key=True),
    db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), primary_key=True)
)

class Producto(db.Model):
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    caracteristicas = db.Column(db.Text, nullable=False) # tipo Text ???-------- Limitar a 1000 caracteres!!!
    ruta_imagen = db.Column(db.String(250), nullable=True) # tipo Imagen ???----- establecer ruta a la imagen
    transaccion = db.Column(db.String(100), unique=True, nullable=True)
    precio_oficial = db.Column(db.Float, nullable=False)
    precio_descuento = db.Column(db.Float, nullable=True)
    fecha_insercion = db.Column(db.DateTime, default=func.now()) # importar paquete DateTime


    socios = db.relationship('Socio', secondary=socios_productos, backref=db.backref('productos', lazy='dynamic'))

class Socio(db.Model):
    id_socio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=False, nullable=False)
    apellido = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
                         
    # ... otros campos? ...


#--------------------------------------------------------------------------------------------------------------------

@app.route('/', methods=['GET','POST']) # RUTA INICIAL DE LA APLICACIÓN
def index():

    return render_template("base.html")




@app.route('/registro', methods=['GET', 'POST'])  # RUTA DE REGISTRO DE LOS SOCIOS
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        username = request.form['username']

        nuevo_socio = Socio(nombre=nombre, apellido=apellido, email=email, password=password, username=username)
        db.session.add(nuevo_socio)
        db.session.commit()

        return redirect(url_for('pagina_registrado'))
    return render_template('registro.html')

@app.route('/registrado')  # RUTA DE CONFIRMACIÓN DE SOCIO REGISTRADO
def pagina_registrado():
    return '<h1>Registro completado con éxito</h1>'



@app.route('/registro_productos', methods=['GET', 'POST'])  #RUTA DE REGISTRO DE LOS PRODUCTOS
def registro_productos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        caracteristicas = request.form['Caracteristicas']
        marca = request.form['marca']
        precio_oficial = request.form['precio_oficial']
        ruta_imagen = request.form['ruta_imagen']

        nuevo_producto = Producto(nombre=nombre, caracteristicas=caracteristicas, marca=marca, precio_oficial = precio_oficial, ruta_imagen = ruta_imagen)
        db.session.add(nuevo_producto)
        db.session.commit()

        return redirect(url_for('producto_registrado'))
    return render_template('registro_productos.html')

@app.route('/registrado_producto')  #RUTA DE CONFIRMACIÓN DE PRODUCTO REGISTRADO
def producto_registrado():
    return '<h1>Registro completado con éxito</h1>'

"""
#Aplicación con las rutas y las vistas...>

@app.route('/')   # La ruta
def index():  # La vista
   
   return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():

   nombre = request.form['nombre']
   password = request.form['password']
   nuevo_socio = Socio(nombre = nombre, password = password)
   db.session.add(nuevo_socio)
   db.session.commit()

   return redirect(url_for('index'))
"""
@app.route('/socios')  #RUTA PARA MOSTRAR TODOS LOS SOCIOS
def mostrar_socios():
    socios = Socio.query.all()  # Recupera todos los socios de la base de datos
    return render_template('mostrar_socios.html', socios = socios)

@app.route('/productos') #RUTA PARA MOSTRAR TODOS LOS PRODUCTOS
def mostrar_productos():
    productos = Producto.query.all() # Recupera todos los socios de la base de datos
    return render_template('mostrar_productos.html', productos = productos)

if __name__ == '__main__':
    with app.app_context(): # Crea un contexto de aplicación, esto es necesario para operaciones que están fuera del flujo normal de de solicitudes, como la creación de tablas al inicio de la aplicación.
        try:
            db.create_all()  # Intenta crear las tablas en la base de datos
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
    app.run(debug=True)


