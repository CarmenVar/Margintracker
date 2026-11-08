import os
import io
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Función para conectar a la base de datos MySQL local
def get_db_connection():
    url = os.getenv("DATABASE_URL")
    
    if url.startswith("mysql+pymysql://"):
        url = url.replace("mysql+pymysql://", "")
    elif url.startswith("mysql://"):
        url = url.replace("mysql://", "")
        
    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, db_name = host_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 3306

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name,
        cursorclass=DictCursor
    )
    return conn

# Inicializar la tabla en MySQL si no existe
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            stock INT NOT NULL DEFAULT 0,
            precio_costo DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            precio_venta DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            impuestos DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            envios DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            margen_neto DECIMAL(10, 2) GENERATED ALWAYS AS (
                precio_venta - (precio_costo + impuestos + envios)
            ) STORED
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Ejecutar la creación de la tabla al arrancar
with app.app_context():
    init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos ORDER BY id ASC;")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', productos=productos)

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
            
            # Manejo seguro para evitar errores con celdas vacías (NaN)
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
@app.route('/registrar', methods=('GET', 'POST'))
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

@app.route('/editar/<int:id>', methods=('GET', 'POST'))
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

@app.route('/eliminar/<int:id>', methods=('POST', 'GET'))
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