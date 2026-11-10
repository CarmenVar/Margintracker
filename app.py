import os
import io
import pandas as pd
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, send_file
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración automática de la base de datos (Compatible con local y Render/Aiven)
database_url = os.environ.get('DATABASE_URL')

if database_url:
    url = urlparse(database_url)
    DB_HOST = url.hostname
    DB_USER = url.username
    DB_PASSWORD = url.password
    DB_NAME = url.path[1:]
    DB_PORT = url.port or 3306
else:
    # Respaldo por si mantienes tus variables separadas localmente
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'defaultdb')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=DictCursor,
        ssl={'ssl': {}}  # Esencial para que Aiven acepte la conexión segura
    )

def init_db():
    """Crea la tabla de productos automáticamente si no existe en la base de datos con todas sus columnas."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    categoria VARCHAR(100) DEFAULT 'General',
                    stock INT NOT NULL,
                    precio_costo DECIMAL(10, 2) NOT NULL,
                    precio_venta DECIMAL(10, 2) NOT NULL,
                    impuestos DECIMAL(10, 2) DEFAULT 0.0,
                    envios DECIMAL(10, 2) DEFAULT 0.0
                )
            """)
        conn.commit()
    finally:
        conn.close()

# Ejecutar la inicialización de la base de datos al arrancar la app
init_db()

@app.route('/')
def index():
    """Ruta principal: Muestra el listado de productos en la pantalla principal."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', productos=productos)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        stock = int(request.form['stock'])
        precio_costo = float(request.form['precio_costo'])
        precio_venta = float(request.form['precio_venta'])
        impuestos = float(request.form['impuestos'])
        envios = float(request.form['envios'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO productos (nombre, categoria, stock, precio_costo, precio_venta, impuestos, envios)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, categoria, stock, precio_costo, precio_venta, impuestos, envios))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
        
    return render_template('registrar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        stock = int(request.form['stock'])
        precio_costo = float(request.form['precio_costo'])
        precio_venta = float(request.form['precio_venta'])
        impuestos = float(request.form['impuestos'])
        envios = float(request.form['envios'])
        
        cur.execute("""
            UPDATE productos 
            SET nombre = %s, categoria = %s, stock = %s, precio_costo = %s, precio_venta = %s, impuestos = %s, envios = %s
            WHERE id = %s
        """, (nombre, categoria, stock, precio_costo, precio_venta, impuestos, envios, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
        
    cur.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('editar.html', producto=producto)

@app.route('/descargar-plantilla')
def descargar_plantilla():
    """Genera y descarga un archivo Excel en blanco con las columnas exactas requeridas."""
    df = pd.DataFrame(columns=['nombre', 'categoria', 'stock', 'precio_costo', 'precio_venta', 'impuestos', 'envios'])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name='plantilla_margintracker.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/importar', methods=['POST'])
def importar():
    """Procesa el archivo Excel o CSV subido, manejando valores vacíos de forma segura."""
    if 'archivo' not in request.files:
        return redirect(url_for('index'))
    
    archivo = request.files['archivo']
    
    if archivo.filename == '':
        return redirect(url_for('index'))
    
    if archivo:
        if archivo.filename.endswith('.csv'):
            df = pd.read_csv(archivo)
        elif archivo.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(archivo)
        else:
            return redirect(url_for('index'))
            
        conn = get_db_connection()
        cur = conn.cursor()
        
        for _, row in df.iterrows():
            nombre = row.get('nombre', 'Sin nombre')
            if pd.isna(nombre): 
                nombre = 'Sin nombre'
                
            categoria = row.get('categoria', 'General')
            if pd.isna(categoria): 
                categoria = 'General'
            
            stock_val = row.get('stock', 10)
            stock = int(stock_val) if pd.notna(stock_val) else 0
            
            costo_val = row.get('precio_costo', 0.0)
            precio_costo = float(costo_val) if pd.notna(costo_val) else 0.0
            
            venta_val = row.get('precio_venta', 0.0)
            precio_venta = float(venta_val) if pd.notna(venta_val) else 0.0
            
            imp_val = row.get('impuestos', 0.0)
            impuestos = float(imp_val) if pd.notna(imp_val) else 0.0
            
            env_val = row.get('envios', 0.0)
            envios = float(env_val) if pd.notna(env_val) else 0.0
            
            cur.execute("""
                INSERT INTO productos (nombre, categoria, stock, precio_costo, precio_venta, impuestos, envios)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, categoria, stock, precio_costo, precio_venta, impuestos, envios))
            
        conn.commit()
        cur.close()
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/eliminar-seleccionados', methods=['POST'])
def eliminar_seleccionados():
    ids = request.form.getlist('ids')
    if ids:
        conn = get_db_connection()
        cur = conn.cursor()
        format_strings = ','.join(['%s'] * len(ids))
        cur.execute(f"DELETE FROM productos WHERE id IN ({format_strings})", tuple(ids))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/eliminar-todos', methods=['POST'])
def eliminar_todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE productos;")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)