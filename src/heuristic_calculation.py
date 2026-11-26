import math
import json


def calculo_tiempo(lat1:int, long1:int, lat2:int, long2:int)->int: 
    radio_tierra = 6371  # Radio de la Tierra en kilómetros
    vMax = 80  # Velocidad máxima en km/h
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(long2 - long1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = radio_tierra * c
    tiempo = round((distancia / vMax)*60, 2)  # Convertir a minutos
    return tiempo

def generar_json():
    with open('paradas.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    nodos = data['elements']
    matriz_heuristica = {}

    for nodo_a in nodos:
        id_a = nodo_a['tags']['name']
        lat_a = nodo_a['lat']
        long_a = nodo_a['lon']
        matriz_heuristica[id_a] = {}

        for nodo_b in nodos:
            id_b = nodo_b['tags']['name']
            lat_b = nodo_b['lat']
            long_b = nodo_b['lon']

            if id_a == id_b:
                matriz_heuristica[id_a][id_b] = 0
            if id_a != id_b:
                tiempo = calculo_tiempo(lat_a, long_a, lat_b, long_b)

                matriz_heuristica[id_a][id_b] = tiempo
    with open('heuristica.json', 'w', encoding='utf-8') as file:
        json.dump(matriz_heuristica, file, indent=2, ensure_ascii=False)


generar_json()
