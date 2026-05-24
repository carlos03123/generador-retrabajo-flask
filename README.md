# Generador de Retrabajo en Industria y Manufactura

**Proyecto Final de la materia Paradigmas de Programacion**  
**UABC Campus Otay | 2026-1**  
**Alumno:** Carlos Rene Lopez Cervantes

---

## ¿Qué es?

Un programa que genera automaticamente los strings de configuracion de retrabajo para flujos de produccion. En los procesos industriales, cuando un producto falla en algun paso del proceso, se desvia a un flujo de retrabajo y despues regresa al flujo principal. Este generador automatiza la creacion del texto de configuracion con el formato:

```
GoToFlowPath[Flujo de Retrabajo/Primer Paso] ReturnStep[Paso de Retorno] Reason[Razón];
```

---

## Mi propuesta

### Explicando la tarea a realizar

Lo primero fue revisar la plantillade Excel que proporciono el profesor. Identifique que tiene dos hojas: `FlowStructures` con los flujos principales y sus pasos, y `FlowReworks` con los flujos de retrabajo agrupados por razon. El diagrama de Excalidraw aclaro el formato del output esperado: un string compuesto por tres partes (GoToFlowPath, ReturnStep, Reason).

El problema se reduce a: dado un conjunto de pasos principales y retrabajos, generar automaticamente el string que conecta cada razon con su flujo de retrabajo correspondiente.

### Seleccion de herramientas

Decidi usar **Flask** como framework web porque queria tener control total sobre el frontend y el backend. A diferencia de frameworks como Streamlit que generan la interfaz automaticamente, Flask me permite disenar el HTML y CSS a mi gusto y manejar la logica del servidor por separado.

- **Python + Flask** para el backend y las rutas de la API
- **HTML/CSS/JavaScript** para el frontend, sin dependencias externas
- **Pandas** para la lectura del Excel
- **ChatGpt** como herramienta de apoyo en el desarrollo

La arquitectura quedo separada en tres capas:
1. `motor.py` — la logica de generacion (parsing, agrupacion, construccion de strings)
2. `app.py` — el servidor Flask con dos endpoints (Excel y manual)
3. `templates/index.html` + `static/style.css` — la interfaz web

### Como funciona el algoritmo

1. Lee los pasos del flujo principal y los ordena por posicion
2. Lee los flujos de retrabajo y los agrupa por razon, identificando el primer paso de cada uno
3. Para cada asignacion, busca el flujo de retrabajo que corresponde a la razon indicada
4. Concatena el nombre del flujo + "/" + primer paso del retrabajo
5. Arma el string completo con el formato requerido

Para el modo Excel, utilizo expresiones regulares para parsear los strings de retrabajo que ya existen en la columna REWORKS y regenerarlos a partir de los datos de FlowReworks.

### Problemas que surgieron

**1. Archivos temporales al subir Excel**
Flask no permite leer directamente el archivo subido con pandas. Tuve que guardar el archivo en un directorio temporal, procesarlo, y luego eliminarlo para no dejar basura en el servidor.

**2. Comunicacion entre frontend y backend**
Para el modo manual, el frontend envia los datos como JSON al servidor. Tuve que estructurar bien el objeto JSON para que el backend pudiera interpretarlo correctamente: pasos como lista, retrabajos como diccionario indexado por razon, y asignaciones como lista de objetos.

**3. Diseño responsive**
El formulario de asignaciones tiene 3 columnas + un boton de eliminar. En pantallas chicas se veia apretado, asi que use CSS Grid con un layout adaptable.

### Pruebas realizadas

- Probe con el Excel de ejemplo del profesor (Proceso Envasado Leche + Final Assembly Route) y el output coincidio con lo esperado
- Probe el modo manual ingresando un flujo personalizado con multiples retrabajos por paso
- Verifique que el drag & drop de archivos funcionara correctamente

---

## Herramientas utilizadas

| Herramienta | Uso |
|---|---|
| Python 3 | Lenguaje principal |
| Flask | Framework web para el servidor |
| Pandas | Lectura y procesamiento de Excel |
| openpyxl | Motor de lectura de archivos .xlsx |
| HTML/CSS/JS | Interfaz web (sin frameworks externos) |
| regex (re) | Parseo de strings de rework existentes |
| Git / GitHub | Control de versiones |
| ChatGpt | Apoyo en desarrollo y debugging |

---

## Como ejecutar

### Requisitos
- Python 3.9 o superior
- pip

### Instalacion

```bash
git clone https://github.com/carlos03123/generador-retrabajo-flask.git
cd generador-retrabajo-flask

pip install -r requirements.txt

python app.py
```

Se abre en `http://localhost:5000`.

### Uso

**Modo Excel:** Arrastra o selecciona un archivo `.xlsx` con las hojas `FlowStructures` y `FlowReworks`.

**Modo Manual:** Escribe el nombre del flujo, los pasos, agrega los retrabajos con sus razones, y define las asignaciones.

---

## Estructura del proyecto

```
rework-generator-flask/
├── app.py                    # Servidor Flask (rutas y endpoints)
├── motor.py                  # Logica del generador (funciones core)
├── requirements.txt          # Dependencias (flask, pandas, openpyxl)
├── templates/
│   └── index.html            # Interfaz web
├── static/
│   └── style.css             # Estilos de la interfaz
├── Rework_Generator.xlsx     # Plantilla de ejemplo
└── README.md                 # Este documento
```

---

## Conclusion

El proyecto usa Flask para dar control total sobre la interfaz y separar bien las responsabilidades entre frontend y backend. La logica del generador es sencilla pero efectiva: parsear, agrupar y concatenar. Lo mas valioso fue entender que el requerimiento del cliente (el profesor) se reduce a un generador de strings con formato especifico, y construir una herramienta que lo haga de forma limpia y reutilizable.
