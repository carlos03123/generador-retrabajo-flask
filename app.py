"""
Rework Generator - Aplicacion Flask
Interfaz web para generar strings de retrabajo.
"""
from flask import Flask, render_template, request, jsonify
from motor import generar_desde_excel, generar_desde_manual
import os
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/procesar_excel', methods=['POST'])
def procesar_excel():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se envio ningun archivo'}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'error': 'Archivo vacio'}), 400

    if not archivo.filename.endswith('.xlsx'):
        return jsonify({'error': 'Solo se aceptan archivos .xlsx'}), 400

    try:
        # Guardar temporalmente
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        archivo.save(tmp.name)
        tmp.close()

        resultados = generar_desde_excel(tmp.name)
        os.unlink(tmp.name)

        # Convertir a formato serializable
        salida = {}
        for nombre_flujo, datos in resultados.items():
            salida[nombre_flujo] = {
                'tiene_retrabajos': datos['tiene_retrabajos'],
                'pasos': datos['pasos'],
            }

        return jsonify({'resultado': salida})

    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500


@app.route('/procesar_manual', methods=['POST'])
def procesar_manual():
    try:
        datos = request.get_json()

        nombre_flujo = datos.get('nombre_flujo', '')
        pasos = datos.get('pasos', [])
        flujos_retrabajo = datos.get('flujos_retrabajo', {})
        asignaciones = datos.get('asignaciones', [])

        if not nombre_flujo or not pasos:
            return jsonify({'error': 'Faltan datos del flujo principal'}), 400

        resultados = generar_desde_manual(
            nombre_flujo, pasos, flujos_retrabajo, asignaciones
        )

        salida = {}
        for nf, datos_flujo in resultados.items():
            salida[nf] = {
                'tiene_retrabajos': datos_flujo['tiene_retrabajos'],
                'pasos': datos_flujo['pasos'],
            }

        return jsonify({'resultado': salida})

    except Exception as e:
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
