from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  #Carga las variables de entorno desde .env

#database_url = os.getenv('DATABASE_URL')



app = Flask(__name__)

#Configurar la URI de la base de datos

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#clase Socio

class Socio(db.Model):

   id = db.Column(db.Integer, primary_key = True)
   socio = db.Column(db.String(80), unique = True, nullable = False)
   password = db.Column(db.String(120), nullable= False)






#Aplicación con las rutas y las vistas...>

@app.route('/')   # La ruta
def index():  # La vista
   
   return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():

   socio = request.form['socio']
   password = request.form['password']
   nuevo_socio = Socio(socio = socio, password = password)
   db.session.add(nuevo_socio)
   db.session.commit()

   return redirect(url_for('index'))

@app.route('/socios')
def mostrar_socios():
    socios = Socio.query.all()  # Recupera todos los socios de la base de datos
    return render_template('mostrar_socios.html', socios=socios)



if __name__ == '__main__':
    with app.app_context(): # Crea un contexto de aplicación, esto es necesario para operaciones que están fuera del flujo normal de de solicitudes, como la creación de tablas al inicio de la aplicación.
        try:
            db.create_all()  # Intenta crear las tablas en la base de datos
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
    app.run(debug=True)


