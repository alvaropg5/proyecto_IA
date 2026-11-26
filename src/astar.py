import json
import networkx as nx


 #Se crea el grafo a partir de los datos de los archivos JSON
with open("grafo_tiempos.json", "r") as file:
    time_graph = json.load(file)

with open("heuristica.json", "r") as file:
    heuristic = json.load(file)
graph = nx.Graph()

for origin, neighbors in time_graph.items():
    for destination, time in neighbors.items():
        graph.add_edge(origin, destination, weight=time)

def get_heuristic(node1, node2)-> tuple[list[str], float]:
    return heuristic[node1][node2]

def astar_algorithm(start, goal):
    route = nx.astar_path(graph, start, goal, heuristic=get_heuristic, weight='time')
    total_time = nx.astar_path_length(graph, start, goal, heuristic=get_heuristic, weight='time')

    return route, total_time