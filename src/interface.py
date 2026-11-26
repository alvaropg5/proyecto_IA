from pathlib import Path
from nicegui import ui
import pandas as pd
from astar import astar_algorithm

# Ruta automática hacia la carpeta 'data' (sube un nivel desde 'src' y entra en 'data')
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

# Leemos los csv de nodos y aristas con su ruta exacta
df_nodos = pd.read_csv(DATA_DIR / 'nodos_metrorrey.csv')
df_aristas = pd.read_csv(DATA_DIR / 'aristas_metrorrey.csv')

#Diccionario que relaciona los nombre de los nodos (estaciones) con sus coordenadas (latitud, longitud)
coordenadas={
    row['nombre']:(row['lat'], row['lon']) 
    for _, row in df_nodos.iterrows()
}
#Colores de las líneas del metro
colores_lineas={
    'Línea 1': '#facc15',  # Amarillo
    'Línea 2': '#16a34a',  # Verde
    'Línea 3': '#dc2626',  # Naranja
    }

capa_ruta_optima=None

def trazar_ruta_optima():
    global capa_ruta_optima
    origen = select_origen.value
    destino= select_destino.value

    if not origen or not destino:
        ui.notify('Por favor, seleccione un origen y un destino.', type='warning')
        return
    if origen == destino:
        ui.notify('El origen y el destino no pueden ser iguales.', type='warning')
        return

    ruta, tiempo = astar_algorithm(origen, destino)

    if capa_ruta_optima is not None:
        mapa.remove_layer(capa_ruta_optima)

    puntos_ruta = [coordenadas[estacion] for estacion in ruta]
    capa_ruta_optima = mapa.generic_layer(
        name='polyline',
        args=[puntos_ruta, {'color': '#2563eb', 'weight': 7, 'opacity': 0.95}]
    )

    recorrido_texto = ' → '.join(ruta)
    label_info.set_text(f'Tiempo estimado: {tiempo} minutos\nEstaciones: ({len(ruta)}) {recorrido_texto}')

ui.page_title('Metrorrey - Ruta Óptima')

with ui.row().classes('w-full h-screen no-wrap p-4 gap-4 bg-slate-100'):
    with ui.card().classes('w-96 h-full p-6 flex flex-col justify-between'):
        with ui.column().classes('w-full gap-4'):
            ui.label('Metrorrey').classes('text-2xl font-bold text-slate-800')
            ui.label('Buscador óptimo con A*').classes('text-sm text-slate-500')

            nombres_estaciones = sorted(coordenadas.keys())
            select_origen = ui.select(nombres_estaciones, label='Origen', with_input=True).classes('w-full')
            select_destino = ui.select(nombres_estaciones, label='Destino', with_input=True).classes('w-full')

            ui.button('Trazar ruta óptima', on_click=trazar_ruta_optima).classes('w-full bg-blue-600 text-white')
            ui.separator()

            label_info = ui.label('Seleccione dos estaciones para comenzar.').classes('text-sm font-medium whitespace-pre-line')
            
        #Leyenda inferior
        with ui.column().classes('gap-1 text-xs text-slate-600'):
            ui.label('● Línea 1 (Talleres - Exposición)').style('color: #eab308; font-weight: bold;')
            ui.label('● Línea 2 (Sendero - Zaragoza)').style('color: #16a34a; font-weight: bold;')
            ui.label('● Línea 3 (Zaragoza - Hosp. Metropolitano)').style('color: #dc2626; font-weight: bold;')

    #Panel con el mapa de Monterrey
    mapa = ui.leaflet(center=(25.7100, -100.3100), zoom=12).classes('flex-grow h-full rounded-xl shadow-md')

    #Dibujamos las líneas del metro usando df_aristas y colores_lineas
    for _, arista in df_aristas.iterrows():
        p1 = coordenadas[arista['origen_nombre']]
        p2 = coordenadas[arista['destino_nombre']]
        color = colores_lineas.get(arista['linea'], '#64748b')
        mapa.generic_layer(
            name='polyline',
            args=[[p1, p2], {'color': color, 'weight': 6, 'opacity': 0.85}]
        )

    #Dibujar las estaciones usando df_nodos 
    for _, nodo in df_nodos.iterrows():
        es_transbordo = '/' in str(nodo['red'])
        mapa.generic_layer(
            name='circleMarker',
            args=[
                [nodo['lat'], nodo['lon']],
                {
                    'radius': 7 if es_transbordo else 4,
                    'color': '#0f172a',
                    'weight': 2,
                    'fillColor': '#ffffff' if es_transbordo else '#334155',
                    'fillOpacity': 1.0,
                    }
                ]
            )

ui.run(port=8080)