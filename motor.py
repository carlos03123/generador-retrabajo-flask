"""
Rework Generator - Motor de generacion
Parsea datos de flujos y genera strings de retrabajo.
"""
import pandas as pd
import re


def leer_excel(archivo):
    """Lee el archivo Excel y retorna los DataFrames de ambas hojas."""
    df_flujos = pd.read_excel(archivo, sheet_name='FlowStructures')
    df_retrabajos = pd.read_excel(archivo, sheet_name='FlowReworks')
    return df_flujos, df_retrabajos


def obtener_flujos_principales(df_flujos):
    """Extrae los flujos principales agrupados con sus pasos."""
    flujos = {}
    for _, fila in df_flujos.iterrows():
        nombre = fila['FLOW'].strip()
        if nombre not in flujos:
            flujos[nombre] = []
        flujos[nombre].append({
            'paso': fila['STEP'].strip(),
            'posicion': int(fila['POSITION']),
        })
    for nombre in flujos:
        flujos[nombre].sort(key=lambda x: x['posicion'])
    return flujos


def obtener_retrabajos(df_retrabajos):
    """Extrae los flujos de retrabajo agrupados por razon."""
    grupos = {}
    razon_actual = None

    for _, fila in df_retrabajos.iterrows():
        razon = fila.get('REASON')
        if pd.notna(razon):
            razon_actual = razon.strip()

        nombre_flujo = fila['REWORK FLOW'].strip()
        paso = fila['STEP REWORK'].strip()
        pos = int(fila['POSITION'])

        if razon_actual not in grupos:
            grupos[razon_actual] = {
                'nombre_flujo': nombre_flujo,
                'pasos': [],
            }
        grupos[razon_actual]['pasos'].append({
            'paso': paso,
            'posicion': pos,
        })

    for razon in grupos:
        grupos[razon]['pasos'].sort(key=lambda x: x['posicion'])
        grupos[razon]['primer_paso'] = grupos[razon]['pasos'][0]['paso']

    return grupos


def construir_string_retrabajo(flujo, primer_paso, retorno, razon):
    """Construye un string de retrabajo individual."""
    return f"GoToFlowPath[{flujo}/{primer_paso}] ReturnStep[{retorno}] Reason[{razon}];"


def parsear_reworks_existentes(texto):
    """Extrae los componentes de strings de rework existentes."""
    patron = r'GoToFlowPath\[([^\]]+)\]\s*ReturnStep\[([^\]]+)\]\s*Reason\[([^\]]+)\];?'
    coincidencias = re.findall(patron, texto)
    return [{'ruta': m[0], 'retorno': m[1], 'razon': m[2]} for m in coincidencias]


def generar_desde_excel(archivo):
    """Genera todos los retrabajos desde un archivo Excel."""
    df_flujos, df_retrabajos = leer_excel(archivo)
    flujos = obtener_flujos_principales(df_flujos)
    retrabajos = obtener_retrabajos(df_retrabajos)

    resultados = {}

    for nombre_flujo, pasos in flujos.items():
        datos_flujo = {'pasos': [], 'tiene_retrabajos': False}

        for info_paso in pasos:
            paso_nombre = info_paso['paso']
            pos = info_paso['posicion']

            mascara = (df_flujos['FLOW'].str.strip() == nombre_flujo) & \
                      (df_flujos['STEP'].str.strip() == paso_nombre)
            fila = df_flujos[mascara]

            strings_rework = []
            if not fila.empty:
                existente = fila.iloc[0].get('REWORKS')
                if pd.notna(existente):
                    parseados = parsear_reworks_existentes(str(existente))
                    for p in parseados:
                        razon = p['razon']
                        retorno = p['retorno']
                        if razon in retrabajos:
                            rw = retrabajos[razon]
                            strings_rework.append(construir_string_retrabajo(
                                rw['nombre_flujo'], rw['primer_paso'],
                                retorno, razon
                            ))
                    if strings_rework:
                        datos_flujo['tiene_retrabajos'] = True

            datos_flujo['pasos'].append({
                'nombre': paso_nombre,
                'posicion': pos,
                'retrabajos': strings_rework,
                'texto_rework': ' '.join(strings_rework),
            })

        resultados[nombre_flujo] = datos_flujo

    return resultados


def generar_desde_manual(nombre_flujo, pasos_principales, flujos_retrabajo, asignaciones):
    """
    Genera retrabajos desde datos manuales.
    
    pasos_principales: lista de strings
    flujos_retrabajo: { razon: { nombre_flujo, pasos: [str] } }
    asignaciones: [{ paso_detecta, razon, paso_retorno }]
    """
    datos_flujo = {'pasos': [], 'tiene_retrabajos': False}

    resultados_por_paso = {paso: [] for paso in pasos_principales}

    for asig in asignaciones:
        paso = asig['paso_detecta']
        razon = asig['razon']
        retorno = asig['paso_retorno']

        if razon in flujos_retrabajo:
            rw = flujos_retrabajo[razon]
            primer_paso = rw['pasos'][0] if rw['pasos'] else ''
            string = construir_string_retrabajo(
                rw['nombre_flujo'], primer_paso, retorno, razon
            )
            if paso in resultados_por_paso:
                resultados_por_paso[paso].append(string)

    for i, paso in enumerate(pasos_principales, 1):
        reworks = resultados_por_paso.get(paso, [])
        if reworks:
            datos_flujo['tiene_retrabajos'] = True
        datos_flujo['pasos'].append({
            'nombre': paso,
            'posicion': i,
            'retrabajos': reworks,
            'texto_rework': ' '.join(reworks),
        })

    return {nombre_flujo: datos_flujo}
