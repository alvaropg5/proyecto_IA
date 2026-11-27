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

es_transbordo_dict={
    row['nombre']: '/' in str(row['red']) 
    for _, row in df_nodos.iterrows()
}

linea_tramo={}
for _, row in df_aristas.iterrows():
    u, v, linea = row['origen_nombre'], row['destino_nombre'], row['linea']
    linea_tramo[(u,v)] = linea
    linea_tramo[(v,u)] = linea  

#Colores de las líneas del metro
colores_lineas={
    'Línea 1': '#facc15',  # Amarillo
    'Línea 2': '#16a34a',  # Verde
    'Línea 3': '#dc2626',  # Naranja
    }

capas_ruta=[]

def actualizar_timeline_drawer(ruta, tiempo):
    contenedor_timeline.clear()
    with contenedor_timeline:
        #Cabecera con el timepo total de la ruta
        with ui.row().classes('items-center gap-2 mb-3'):
            ui.icon('directions_subway',color='#f59e0b').classes('text-2xl')
            ui.label(f'Tiempo total: {tiempo} minutos').classes('text-xl font-bold text-amber-500')
        #Tarjeta interior con scroll para las paradas de la ruta
        with ui.scroll_area().classes('w-full flex-grow rounded-xl p-4').style('background-color: #1e293b;'):
            with ui.column().classes('w-full gap-0'):
                linea_anterior=None
                for i, estacion in enumerate(ruta):
                    #Determinar el color de la línea en este punto
                    if i < len(ruta) - 1:
                        linea_actual = linea_tramo.get((estacion, ruta[i + 1]), 'Línea 1')
                    else:
                        linea_actual = linea_anterior or 'Línea 1'
                    color_actual = colores_lineas.get(linea_actual, '#3b82f6')
                    #Si hay un cambio de línea, mostrar un mensaje de transbordo
                    if linea_anterior is not None and linea_actual != linea_anterior:
                        with ui.row().classes('items-stretch no-wrap gap-3'):
                            with ui.column().classes('items-center w-6'):
                                ui.element('div').classes('w-0.5 h-8 border-l-2 border-dashed border-slate-400')
                            with ui.column().classes('justify-center pb-2'):
                                ui.label(f'Transbordo a {linea_actual}').classes('text-xs italic text-slate-400')
                    #Fila de la estación(círculo, línea vertical y nombre de la estación)
                    with ui.row().classes('items-stretch no-wrap gap-x-3 gap-y-0'):
                        #Columna izquierda con punto de estacion y segmento conector
                        with ui.column().classes('items-center w-6 gap-0'):
                            ui.element('div').classes('w-4 h-4 rounded-full border-2 border-white shrink-0').style(
                                f'background-color: {color_actual};'
                            )
                            if i < len(ruta) - 1:
                                ui.element('div').classes('w-1 flex-grow min-h-[28px] -mt-0.5 -mb-0.5').style(
                                    f'background-color: {color_actual};'
                                )
                        #Columna derecha con el nombre de la estación
                        with ui.column().classes('pb-4 gap-0'):
                            ui.label(estacion).classes('text-sm font-bold text-amber-400 leading-tight')
                            if i==0:
                                ui.label(f'Origen {linea_actual}').classes('text-xs text-slate-400')
                            elif i==len(ruta)-1:
                                ui.label(f'Destino').classes('text-xs text-slate-400')
                    linea_anterior = linea_actual


def limpiar_panel():
    global capas_ruta
    select_origen.set_value(None)
    select_destino.set_value(None)
    for capa in capas_ruta:
        mapa.remove_layer(capa)
    capas_ruta.clear()
    drawer_ruta.hide()

def trazar_ruta_optima():
    global capas_ruta
    origen = select_origen.value
    destino= select_destino.value

    if not origen or not destino:
        ui.notify('Por favor, seleccione un origen y un destino.', type='warning')
        return
    if origen == destino:
        ui.notify('El origen y el destino no pueden ser iguales.', type='warning')
        return

    ruta, tiempo = astar_algorithm(origen, destino)
    for capa in capas_ruta:
        mapa.remove_layer(capa)
    capas_ruta.clear()

    puntos_ruta = [coordenadas[estacion] for estacion in ruta]
    linea_azul = mapa.generic_layer(
        name = 'polyline',
        args = [puntos_ruta, {'color': '#2563eb', 'weight': 9, 'opacity': 0.95}]
    )
    capas_ruta.append(linea_azul)

    for estacion in ruta:
        lat, lon = coordenadas[estacion]
        es_transbordo = es_transbordo_dict.get(estacion, False)
        punto = mapa.generic_layer(
            name='circleMarker',
            args=[
                [lat, lon],
                {
                    'radius': 7 if es_transbordo else 5,
                    'color': "#1e293b",
                    'weight': 2,
                    'fillColor': '#ffffff' if es_transbordo else '#334155',
                    'fillOpacity': 1.0,
                }
            ]
        )
        capas_ruta.append(punto)
    
    actualizar_timeline_drawer(ruta, tiempo)
    drawer_ruta.show()

ui.page_title('Metrorrey - Ruta Óptima')

drawer_ruta = ui.right_drawer(value=False, fixed=True).classes(
   'w-80 p-4 flex flex-col justify-between text-white').style('background-color: #0f172a;')
with drawer_ruta:
    contenedor_timeline = ui.column().classes('w-full flex-grow overflow-hidden gap-2')
    ui.button('Cerrar',on_click=drawer_ruta.hide).classes(
        'w-full mt-3 font-bold text-slate-200'
    ).style('background-color: #451a1a;')

with ui.row().classes('w-full h-screen no-wrap p-4 gap-4 bg-slate-100'):
    with ui.card().classes('w-96 h-full p-6 flex flex-col justify-between text-white').style('background-color: #1e293b;'):
        with ui.column().classes('w-full gap-4'):
            ui.label('Metrorrey').classes('text-2xl font-bold text-white')
            ui.label('Buscador óptimo con A*').classes('text-sm text-slate-500')

            nombres_estaciones = sorted(coordenadas.keys())
            select_origen = ui.select(nombres_estaciones, label='Origen', with_input=True).props('outlined bg-color="white"').classes('w-full')
            select_destino = ui.select(nombres_estaciones, label='Destino', with_input=True).props('outlined bg-color="white"').classes('w-full')
            ui.button('Limpiar' , on_click=limpiar_panel).classes('w-full bg-blue-600 text-white')
            ui.button('Trazar ruta óptima', on_click=trazar_ruta_optima).classes('w-full bg-blue-600 text-white')
            
        #Leyenda inferior
        with ui.column().classes('gap-1 text-xs text-slate-600'):
            ui.label('● Línea 1 (Talleres - Exposición)').style('color: #facc15; font-weight: bold;')
            ui.label('● Línea 2 (Sendero - Zaragoza)').style('color: #4ade80; font-weight: bold;')
            ui.label('● Línea 3 (Zaragoza - Hosp. Metropolitano)').style('color: #f87171; font-weight: bold;')

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