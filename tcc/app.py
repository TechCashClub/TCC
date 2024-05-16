from flask import Flask, render_template, flash, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.sql import func
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import os
from os import abort
from functools import wraps
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class FormularioRegistro(FlaskForm):

    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    submit = SubmitField('Guardar')


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

"""class Admin(db.Model):
    id_admin = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    #productos = db.relationship('Producto', backref='admin', lazy=True)

"""
# Definiciones de tablas de asociación
socios_productos = db.Table('socios_productos',
    db.Column('id_socio', db.Integer, db.ForeignKey('socio.id_socio'), primary_key=True),
    db.Column('id_producto', db.Integer, db.ForeignKey('producto.id_producto'), primary_key=True)
)

socios_transacciones = db.Table('socios_transacciones',
    db.Column('id_socio', db.Integer, db.ForeignKey('socio.id_socio'), primary_key=True),
    db.Column('id_transaccion', db.Integer, db.ForeignKey('transaccion.id'), primary_key=True)
)

class Producto(db.Model):
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    caracteristicas = db.Column(db.Text, nullable=False) # tipo Text ???-------- Limitar a 1000 caracteres!!!
    ruta_imagen = db.Column(db.String(250), nullable=True) # tipo Imagen ???----- establecer ruta a la imagen
    transaccion_id = db.Column(db.Integer, db.ForeignKey('transaccion.id'), unique=True, nullable=True)  # Clave foránea como identificador de transacción
    precio_oficial = db.Column(db.Float, nullable=False)
    precio_descuento = db.Column(db.Float, nullable=True)
    fecha_insercion = db.Column(db.DateTime, default=func.now()) # importar paquete DateTime
    socios = db.relationship('Socio', secondary='socios_productos', backref=db.backref('productos', lazy='dynamic'))

class Socio(db.Model,UserMixin):
    id_socio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=False, nullable=False)
    apellido = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    username = db.Column(db.String(100), unique=False, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='socio')
                         
    def check_password(self, password):

        return check_password_hash(self.password, password)

    def is_active(self):

        return True
    
    def get_id(self):

        return str(self.id_socio)


# Clase Transaccion, añadida relación con Producto
class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=func.now())
    fecha_fin = db.Column(db.DateTime, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id_producto'))
    producto = db.relationship('Producto', foreign_keys=[producto_id], backref=db.backref('transaccion_relacionada', uselist=False))
    socios = db.relationship('Socio', secondary='socios_transacciones', backref=db.backref('transacciones', lazy='dynamic'))

    def agregar_socio(self, socio):
        if self.fecha_inicio <= datetime.now() <= self.fecha_fin:
            self.socios.append(socio)
            db.session.commit()
            print(f"Socio {socio.id_socio} agregado. Total de socios: {len(self.socios)}")
        else:
            print("La puja está cerrada o aún no ha comenzado.")

    def calcular_descuento(self):
        numero_de_socios = len(self.socios)
        descuento = min(30, numero_de_socios ** 2 * 0.1)
        return descuento



#--------------------------------------------------------------------------------------------------------------------

@app.route('/calendar_events')

def calendar_events():
    require_role('socio')
    print(f"Current user: {current_user}")  # Debugging
    assert current_user.is_authenticated, "User is not authenticated"
    assert hasattr(current_user, 'id_socio'), "Current user does not have attribute 'id_socio'"
    
    transacciones = Transaccion.query.join(socios_transacciones, Transaccion.id == socios_transacciones.c.id_transaccion).filter(socios_transacciones.c.id_socio == current_user.id_socio).all()
    events = [
        {
            'title': transaccion.producto.nombre,
            'start': transaccion.fecha_inicio.isoformat(),
            'end': transaccion.fecha_fin.isoformat()
        } for transaccion in transacciones
    ]
    print(events)  # Imprimir los datos para verificar
    return jsonify(events)








@app.route('/crear_transaccion', methods=['GET'])
def mostrar_formulario():
    return render_template('crear_transaccion.html')


@app.route('/crear_transaccion', methods=['POST'])
def procesar_formulario():
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    producto_id = request.form['producto_id']
    
    # Convertir las fechas de string a tipo datetime
    from datetime import datetime
    formato = '%Y-%m-%dT%H:%M'
    fecha_inicio = datetime.strptime(fecha_inicio, formato)
    fecha_fin = datetime.strptime(fecha_fin, formato)
    
    # Crear una nueva instancia de Transaccion
    nueva_transaccion = Transaccion(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        producto_id=producto_id
    )
    
    # Añadir la transacción a la base de datos
    db.session.add(nueva_transaccion)
    db.session.commit()
    
    # Redirigir a otra página o mostrar un mensaje de éxito
    return redirect(url_for('mostrar_formulario'))


"""
@app.route('/listar_transacciones')
@login_required
def listar_transacciones():
    if current_user.role != 'admin':
        flash('No tienes acceso a este recurso.','warning')  # Forbid access if the user is not an admin
    
    transacciones = Transaccion.query.all()
    return render_template('listar_transacciones.html', transacciones=transacciones)
"""


@app.route('/listar_transacciones')
@login_required
def listar_transacciones():
    if current_user.role != 'admin':
        flash('No tienes acceso a este recurso.', 'warning')
        return redirect(url_for('login'))  # Redirige a otra página si el usuario no es administrador

    transacciones_info = []
    transacciones = Transaccion.query.options(db.joinedload(Transaccion.socios)).all()
    for transaccion in transacciones:
        socios_names = [socio.nombre for socio in transaccion.socios]  # Lista de nombres de socios
        transacciones_info.append({
            'transaccion': transaccion,
            'socios': socios_names  # Pasamos la lista de nombres
        })

    return render_template('listar_transacciones.html', transacciones=transacciones_info)








@app.route('/editar_transaccion/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_transaccion(id):
    if current_user.role != 'admin':
        abort(403)  # Forbid access if the user is not an admin
    
    transaccion = Transaccion.query.get_or_404(id)
    
    if request.method == 'POST':
        transaccion.fecha_inicio = request.form['fecha_inicio']
        transaccion.fecha_fin = request.form['fecha_fin']
        transaccion.producto_id = request.form['producto_id']
        db.session.commit()
        flash('Transacción actualizada correctamente.', 'success')
        return redirect(url_for('listar_transacciones'))
    
    productos = Producto.query.all()  # Obtener todos los productos para mostrar en el formulario de edición
    return render_template('editar_transacciones.html', transaccion=transaccion, productos=productos)



@app.route('/eliminar_transaccion/<int:id>', methods=['POST'])   # Eliminar transacción
@login_required
def eliminar_transaccion(id):
    if current_user.role != 'admin':
        abort(403)  # Forbid access if the user is not an admin
    
    transaccion = Transaccion.query.get_or_404(id)
    db.session.delete(transaccion)
    db.session.commit()
    flash('Transacción eliminada correctamente.', 'success')
    return redirect(url_for('listar_transacciones'))




@app.route('/unirse_transaccion/<int:transaccion_id>', methods=['POST'])   #Unirse a transacción
@login_required
def unirse_transaccion(transaccion_id):
    transaccion = Transaccion.query.get_or_404(transaccion_id)
    socio = Socio.query.get(session['id_socio'])  # Suponiendo que almacenamos el ID del socio en la sesión

    # Verificar si el socio ya está unido
    if socio not in transaccion.socios:
        transaccion.socios.append(socio)
        db.session.commit()
        flash('Te has unido a la transacción exitosamente!', 'success')
    else:
        flash('Ya estás unido a esta transacción.', 'info')

    return redirect(url_for('socio_dashboard'))

















@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = FormularioRegistro()
    if form.validate_on_submit():
        usuario_existente = Socio.query.filter_by(email=form.email.data).first() or Socio.query.filter_by(username=form.username.data).first()
        if usuario_existente:
            flash('El email o nombre de usuario ya está registrado.', 'warning')
            return redirect(url_for('signup'))
        
        # Hashear la contraseña antes de guardarla
        hashed_password = generate_password_hash(form.password.data)
        
        nuevo_socio = Socio(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            email=form.email.data,
            password=hashed_password,
            username=form.username.data
        )
        db.session.add(nuevo_socio)
        db.session.commit()
        flash('Registro completado con éxito.', 'success')
        return redirect(url_for('login'))
    return render_template('formulario_registro.html', form=form)










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
#@require_role('admin')
@login_required
def index():
    
    return render_template("bienvenida.html")
    
"""   

@app.route('/', methods=['GET', 'POST'])   # RUTA de login 
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

"""

@app.route('/')
def inicio():

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Usando session para la consulta
        user = db.session.query(Socio).filter_by(nombre=username).first()

        if user and user.check_password(password):  # Suponiendo que existe la función check_password
            login_user(user)  # Autenticación con Flask-Login
            if user.role == 'admin':
                return redirect(url_for('index'))
            elif user.role == 'socio':
                session['id_socio'] = user.id_socio  # Guarda el ID del socio en la sesión
                return redirect(url_for('socio_dashboard'))  # Cambiado para usar la ruta sin ID
            else:
                flash('Acceso no autorizado.')
                return redirect(url_for('login'))
        flash('Nombre de usuario o contraseña incorrecto.')
    return render_template('login.html')




@app.route('/logout')
def logout():
    session.clear() 
    logout_user() # Limpia la sesión para remover cualquier dato del usuario logueado
    return redirect(url_for('login'))  # Redirige al usuario a la página de login


from datetime import datetime, timezone

@app.route('/socio_dashboard')
@login_required
def socio_dashboard():
    socio = current_user  # Usando directamente current_user, que debería estar autenticado

    # Filtrar transacciones disponibles
    ahora = datetime.now(timezone.utc)
    transacciones = Transaccion.query.filter(
        Transaccion.fecha_inicio <= ahora,
        Transaccion.fecha_fin >= ahora
    ).all()

    transacciones_disponibles = [{
        'transaccion': transaccion,
        'is_member': socio in transaccion.socios,
        'producto': transaccion.producto  # Asegúrate de que cada transaccion tiene un producto asociado
    } for transaccion in transacciones]

    return render_template('socio.html', socio=socio, transacciones_disponibles=transacciones_disponibles)













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







@app.route('/socio/<int:id_socio>/editar', methods=['GET', 'POST'])  #Ruta para editar socio
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
    #socios = Socio.query.all()  # Recupera todos los socios de la base de datos
    socios = db.session.query(Socio).filter_by(role='socio').all()
    return render_template('mostrar_socios.html', socios = socios)

@app.route('/productos') #RUTA PARA MOSTRAR TODOS LOS PRODUCTOS
#@require_role('admin')
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

@app.route('/baja_socio/<int:id_socio>', methods=['POST'])
@login_required
def baja_socio(id_socio):
    socio = Socio.query.get_or_404(id_socio)
    if socio != current_user:
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('socio_dashboard'))
    
    db.session.delete(socio)
    db.session.commit()
    
    flash('Te has dado de baja del club.', 'success')
    return redirect(url_for('index'))








if __name__ == '__main__':
    with app.app_context(): # Crea un contexto de aplicación, esto es necesario para operaciones que están fuera del flujo normal de de solicitudes, como la creación de tablas al inicio de la aplicación.
        try:
            db.create_all()  # Intenta crear las tablas en la base de datos
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
    app.run(debug=True)


