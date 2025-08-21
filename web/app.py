from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "tu_clave_secreta_aqui"  # necesario para usar flash y sesiones

# Datos de conexión DB
DB_HOST = "dpg-d26e2sje5dus73djs3pg-a.oregon-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "listi_dz0x"
DB_USER = "listi_dz0x_user"
DB_PASS = "NyqDiVArgAqrOMnjIAqAylWWWvmJPcYm"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        sslmode='require'
    )

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contra = request.form.get("contrasena")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user['contraseña'], contra):
            return render_template("bienvenida.html", usuario=usuario)
        else:
            flash("Usuario o contraseña incorrectos", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contra = request.form.get("contrasena")

        if not usuario or not contra:
            flash("Completa todos los campos", "error")
            return redirect(url_for("registro"))

        conn = get_db_connection()
        cur = conn.cursor()

        # Crear tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
                contraseña TEXT NOT NULL
            );
        """)
        conn.commit()

        cur.execute("SELECT 1 FROM usuarios WHERE nombre_usuario = %s", (usuario,))
        if cur.fetchone():
            flash("El usuario ya existe", "error")
            cur.close()
            conn.close()
            return redirect(url_for("registro"))

        contra_hash = generate_password_hash(contra)
        cur.execute("INSERT INTO usuarios (nombre_usuario, contraseña) VALUES (%s, %s)", (usuario, contra_hash))
        conn.commit()
        cur.close()
        conn.close()

        flash("Usuario registrado correctamente, podés iniciar sesión", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)
