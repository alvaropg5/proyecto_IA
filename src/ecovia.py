import json

with open("ecovia.json", encoding="utf-8") as archivo:
    datos = json.load(archivo)

estaciones = []

for elem in datos["elements"]:
    nombre = elem["tags"]["name"]
    lat = elem["center"]["lat"]
    lon = elem["center"]["lon"]
    if nombre == "Ecovía Estación Regina":
        continue

    nombre = nombre.replace("Ecovía - ", "")

    estaciones.append({"nombre": nombre, "lat": lat, "lon": lon})

estaciones.sort(key=lambda e: e["lon"])

for e in estaciones:
    print(e["nombre"], e["lon"])

print("Total:", len(estaciones))

import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    h = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

K = 30.1 / 29.4
VELOCIDAD = 20.8

total_min = 0
for i in range(len(estaciones) - 1):
    a = estaciones[i]
    b = estaciones[i + 1]
    d = haversine(a["lat"], a["lon"], b["lat"], b["lon"])
    minutos = d * K / VELOCIDAD * 60
    total_min = total_min + minutos
    print(a["nombre"], "->", b["nombre"], round(minutos, 1), "min")

print("Tiempo total:", round(total_min), "min")

grafo_ecovia = {}

for e in estaciones:
    grafo_ecovia["Ecovía: " + e["nombre"]] = {}

for i in range(len(estaciones) - 1):
    a = estaciones[i]
    b = estaciones[i + 1]
    d = haversine(a["lat"], a["lon"], b["lat"], b["lon"])
    minutos = round(d * K / VELOCIDAD * 60, 1)

    nombre_a = "Ecovía: " + a["nombre"]
    nombre_b = "Ecovía: " + b["nombre"]

    grafo_ecovia[nombre_a][nombre_b] = {"tiempo": minutos, "linea": "Ecovía"}
    grafo_ecovia[nombre_b][nombre_a] = {"tiempo": minutos, "linea": "Ecovía"}

with open("grafo_ecovia.json", "w", encoding="utf-8") as archivo:
    json.dump(grafo_ecovia, archivo, ensure_ascii=False, indent=2)

