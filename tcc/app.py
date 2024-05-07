from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
import os
from functools import wraps

load_dotenv()  #Carga las variables de entorno desde .env

#database_url = os.getenv('DATABASE_URL')


#Clave secreta de FLASK
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

#FLASK-LOGIN---------------------------------------------------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Esta sería la vista que maneja el inicio de sesión

@login_manager.user_loader
def load_user(id_socio):
    return db.session.get(Socio,id_socio) 

#-------------------------------------------------------------------------------------


admin_username = os.getenv('ADMIN_USERNAME')
admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')

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

class Socio(db.Model,UserMixin):
    id_socio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=False, nullable=False)
    apellido = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='socio')
                         
    def check_password(self, password):

        return check_password_hash(self.password, password)

    def is_active(self):

        return True
    
    def get_id(self):

        return str(self.id_socio)
#--------------------------------------------------------------------------------------------------------------------












# Decorador para restringir acceso a las rutas solo administrador
    
    


"""

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Necesitas iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

"""





def require_role(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("No tienes permiso para acceder a esta página.")
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return decorated_function
    return decorator












@app.route('/index', methods=['GET','POST']) # RUTA INICIAL DE LA APP
@require_role('admin')
@login_required
def index():
    
    return render_template("bienvenida.html")
    
    
"""
@app.route('/', methods=['GET','POST']) #RUTA AL LOGIN
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')

        if username == admin_username and check_password_hash(admin_password_hash, password):
            session['logged_in'] = True  # Indica que el administrador está logueado
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')
"""
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f" Username: {username}, Password: {password}") # Debuggeando
        #usando session para la consulta
        user = db.session.query(Socio).filter_by(nombre=username).first()
        print(f"User found: {user}") # Debuggeando
        
        if user is not None and user.check_password(password):
            

            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('index'))
            elif user.role == 'socio':
                return redirect(url_for('socio', id_socio=user.id_socio))
            else:
                flash('Acceso no autorizado.')
                return redirect(url_for('login'))
        flash('Nombre de usuario o contraseña incorrecto.')
    return render_template('login.html')




@app.route('/logout')
def logout():
    session.clear()  # Limpia la sesión para remover cualquier dato del usuario logueado
    return redirect(url_for('login'))  # Redirige al usuario a la página de login




@app.route('/socio_dashboard/<int:id_socio>') # DASHBOARD DEL SOCIO
@require_role('socio')
def socio(id_socio):
    info_socio = db.session.get(Socio,id_socio)
    if not info_socio:
        return 'Socio no encontrado', 404
    return render_template('socio.html', nombre= info_socio.nombre, apellido=info_socio.apellido, email=info_socio.email)








@app.route('/registro', methods=['GET', 'POST'])  # RUTA DE REGISTRO DE LOS SOCIOS
@require_role('admin')
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

@app.route('/eliminar_socio/<int:id>', methods=['POST']) # RUTA PARA BORRAR REGISTRO DE SOCIO
@require_role('admin')
def eliminar_socio(id):
    socio = Socio.query.get_or_404(id)
    db.session.delete(socio)
    db.session.commit()
    #flash('Socio eliminado con éxito.', 'success')
    return redirect(url_for('mostrar_socios'))

@app.route('/socio/<int:id_socio>/editar', methods=['GET', 'POST'])
@require_role('admin')
def editar_socio(id_socio):
    socio = Socio.query.get_or_404(id_socio)
    if request.method == 'POST':
        socio.nombre = request.form['nombre']
        socio.apellido = request.form['apellido']
        socio.email = request.form['email']
        socio.username = request.form['username']
        # Aquí se debería agregar validaciones para asegurar que email y username sigan siendo únicos, etc.
        try:
            db.session.commit()
            #flash('Los datos del socio han sido actualizados con éxito.', 'success')
            return redirect(url_for('mostrar_socios'))
        except:
            db.session.rollback()
            #flash('Error al actualizar los datos. Asegúrate de que el email y nombre de usuario sean únicos.', 'error')
            return redirect(url_for('editar_socio', socio= socio))
    
    return render_template('editar_socio.html', socio = socio)    

@app.route('/registrado')  # RUTA DE CONFIRMACIÓN DE SOCIO REGISTRADO
@require_role('admin')
def pagina_registrado():
    return redirect(url_for('mostrar_socios'))



@app.route('/registro_productos', methods=['GET', 'POST'])  #RUTA DE REGISTRO DE LOS PRODUCTOS
@require_role('admin')
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
@require_role('admin')
def producto_registrado():
    return redirect(url_for('mostrar_productos'))


@app.route('/socios')  #RUTA PARA MOSTRAR TODOS LOS SOCIOS
@require_role('admin')
def mostrar_socios():
    socios = Socio.query.all()  # Recupera todos los socios de la base de datos
    return render_template('mostrar_socios.html', socios = socios)

@app.route('/productos') #RUTA PARA MOSTRAR TODOS LOS PRODUCTOS
@require_role('admin')
def mostrar_productos():

    productos = Producto.query.all() # Recupera todos los socios de la base de datos
    return render_template('mostrar_productos.html', productos = productos)

@app.route('/eliminar/<int:id>', methods=['POST']) #RUTA PARA ELIMINAR UN PRODUCTO 
@require_role('admin')
def eliminar_producto(id):
    productos = Producto.query.get_or_404(id)
    db.session.delete(productos)
    db.session.commit()
    flash('Producto eliminado con éxito.', 'success')
    return redirect(url_for('mostrar_productos'))

if __name__ == '__main__':
    with app.app_context(): # Crea un contexto de aplicación, esto es necesario para operaciones que están fuera del flujo normal de de solicitudes, como la creación de tablas al inicio de la aplicación.
        try:
            db.create_all()  # Intenta crear las tablas en la base de datos
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
    app.run(debug=True)


