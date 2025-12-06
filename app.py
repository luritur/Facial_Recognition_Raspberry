from flask import Flask, render_template
app = Flask(__name__)
# Página principal (dashboard)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Página de camara
@app.route('/camara_directo')
def camara_directo():
    return render_template('camara_directo.html')

# Página de registro
@app.route('/registro_empleados')
def registro_empleados():
    return render_template('registro_empleados.html')

# Página de navegación
@app.route('/base')
def navegar():
    return render_template('base.html')

@app.route('/agregar_empleado', methods=['POST'])
def agregar_empleado():
    # Aquí procesas los datos del formulario
    # Luego rediriges de vuelta a la página de registro
    return render_template('registro_empleados.html')

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=8000, debug=True)