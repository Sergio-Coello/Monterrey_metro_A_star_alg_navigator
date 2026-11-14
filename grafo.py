import os
import re
import unicodedata

import networkx as nx
import pandas as pd 


# Coste mínimo del transbordo, expresado en metros equivalentes (6 m/s).
changeWeight = 6 * 120

# Matriz de distancias en línea recta usada por la heurística de A*.
df = pd.read_excel(
    os.path.join(
        os.path.dirname(__file__),
        "resources", "static", "Metrorrey_estructura_heuristica.xlsx"
    ),
    index_col=0,
    header=0,
)

# Nodos por línea. Las estaciones de transbordo llevan el sufijo de línea.
lines = {
    "L1": [
        "Talleres", "San Bernabé", "Unidad Modelo", "Aztlán",
        "Penitenciaría", "Alfonso Reyes", "Mitras", "Simón Bolívar",
        "Hospital", "Edison", "Central", "Cuauhtémoc L1", "Del Golfo",
        "Félix U. Gómez L1", "Parque Fundidora", "Y Griega", "Eloy Cavazos",
        "Lerdo de Tejada", "Exposición",
    ],
    "L2": [
        "Sendero", "Santiago Tapia", "San Nicolás", "Anáhuac",
        "Universidad", "Niños Héroes", "Regina", "General Anaya",
        "Cuauhtémoc L2", "Alameda", "Fundadores", "Padre Mier",
        "General I. Zaragoza L2",
    ],
    "L3": [
        "General I. Zaragoza L3", "Santa Lucía", "Colonia Obrera",
        "Félix U. Gómez L3", "Metalúrgicos", "Moderna", "Ruiz Cortines",
        "Los Ángeles", "Hospital Metropolitano",
    ],
}

transb = {
    "Cuauhtémoc": ["Cuauhtémoc L1", "Cuauhtémoc L2"],
    "Félix U. Gómez": ["Félix U. Gómez L1", "Félix U. Gómez L3"],
    "General I. Zaragoza": [
        "General I. Zaragoza L2", "General I. Zaragoza L3"
    ],
}

def normalizar(nombre):
    nombre = unicodedata.normalize("NFD", nombre.strip().lower())
    return "".join(
        caracter for caracter in nombre
        if unicodedata.category(caracter) != "Mn" and caracter.isalnum()
    )


stations = []
for line_stations in lines.values():
    for station in line_stations:
        station = re.sub(r" L[123]$", "", station)
        if station not in stations:
            stations.append(station)

station_names = {normalizar(station): station for station in stations}


def crear_grafo():
    """Crea el grafo con las distancias de los tramos y los transbordos."""
    G = nx.Graph()

    # Línea 1
    G.add_edge("Talleres", "San Bernabé", weight=1390)
    G.add_edge("San Bernabé", "Unidad Modelo", weight=1000)
    G.add_edge("Unidad Modelo", "Aztlán", weight=1320)
    G.add_edge("Aztlán", "Penitenciaría", weight=1100)
    G.add_edge("Penitenciaría", "Alfonso Reyes", weight=800)
    G.add_edge("Alfonso Reyes", "Mitras", weight=1140)
    G.add_edge("Mitras", "Simón Bolívar", weight=780)
    G.add_edge("Simón Bolívar", "Hospital", weight=780)
    G.add_edge("Hospital", "Edison", weight=1170)
    G.add_edge("Edison", "Central", weight=950)
    G.add_edge("Central", "Cuauhtémoc L1", weight=760)
    G.add_edge("Cuauhtémoc L1", "Del Golfo", weight=1040)
    G.add_edge("Del Golfo", "Félix U. Gómez L1", weight=980)
    G.add_edge("Félix U. Gómez L1", "Parque Fundidora", weight=860)
    G.add_edge("Parque Fundidora", "Y Griega", weight=870)
    G.add_edge("Y Griega", "Eloy Cavazos", weight=1600)
    G.add_edge("Eloy Cavazos", "Lerdo de Tejada", weight=1170)
    G.add_edge("Lerdo de Tejada", "Exposición", weight=700)

    # Línea 2
    G.add_edge("Sendero", "Santiago Tapia", weight=1090)
    G.add_edge("Santiago Tapia", "San Nicolás", weight=770)
    G.add_edge("San Nicolás", "Anáhuac", weight=1530)
    G.add_edge("Anáhuac", "Universidad", weight=1790)
    G.add_edge("Universidad", "Niños Héroes", weight=850)
    G.add_edge("Niños Héroes", "Regina", weight=1030)
    G.add_edge("Regina", "General Anaya", weight=1300)
    G.add_edge("General Anaya", "Cuauhtémoc L2", weight=1170)
    G.add_edge("Cuauhtémoc L2", "Alameda", weight=1030)
    G.add_edge("Alameda", "Fundadores", weight=530)
    G.add_edge("Fundadores", "Padre Mier", weight=520)
    G.add_edge("Padre Mier", "General I. Zaragoza L2", weight=540)

    # Línea 3
    G.add_edge("General I. Zaragoza L3", "Santa Lucía", weight=1250)
    G.add_edge("Santa Lucía", "Colonia Obrera", weight=590)
    G.add_edge("Colonia Obrera", "Félix U. Gómez L3", weight=810)
    G.add_edge("Félix U. Gómez L3", "Metalúrgicos", weight=650)
    G.add_edge("Metalúrgicos", "Moderna", weight=1220)
    G.add_edge("Moderna", "Ruiz Cortines", weight=770)
    G.add_edge("Ruiz Cortines", "Los Ángeles", weight=520)
    G.add_edge("Los Ángeles", "Hospital Metropolitano", weight=1770)

    # Transbordos
    G.add_edge("Cuauhtémoc L1", "Cuauhtémoc L2", weight=240 * 6)
    G.add_edge("Félix U. Gómez L1", "Félix U. Gómez L3", weight=300 * 6)
    G.add_edge(
        "General I. Zaragoza L2", "General I. Zaragoza L3", weight=120 * 6
    )

    return G


def estaciones_publicas():
    return stations.copy()


def nombre_correcto(station):
    return normalizar(station) in station_names


def linea(station):
    for line, line_stations in lines.items():
        if station in line_stations:
            return line
    return None


def lineas(listStations):
    return list(map(linea, listStations))


def obtener_ruta(G, origin, target):
    """Busca con A* entre las variantes de línea de origen y destino."""
    origin = station_names.get(normalizar(origin))
    target = station_names.get(normalizar(target))
    if origin is None or target is None:
        raise ValueError("La estación de origen o destino no existe.")

    optOrigin = transb.get(origin, [origin])
    optTarget = transb.get(target, [target])
    minWeight = float("inf")
    minPath = []

    for orig in optOrigin:
        for targ in optTarget:
            try:
                path = nx.astar_path(
                    G, orig, targ, heuristic=heuristica, weight="weight"
                )
            except nx.NetworkXNoPath:
                continue

            weight = sum(
                G[path[i]][path[i + 1]]["weight"]
                for i in range(len(path) - 1)
            )
            if weight < minWeight:
                minWeight = weight
                minPath = path

    return (minPath, minWeight) if minPath else (None, None)


def heuristica(current, target):
    """Usa la distancia del Excel y suma el transbordo mínimo si cambia línea."""
    current_line = linea(current)
    target_line = linea(target)
    current_name = re.sub(r" L[123]$", "", current)
    target_name = re.sub(r" L[123]$", "", target)

    if current == target:
        return 0

    try:
        distance = float(df[current_name][target_name])
    except (KeyError, TypeError, ValueError):
        distance = 0

    if pd.isna(distance):
        distance = 0
    if current_line != target_line:
        distance += changeWeight

    return max(0, distance)


def limpiar_estaciones(listStations):
    return [re.sub(r" L[123]$", "", station) for station in listStations]


def calcular_transbordos(path):
    """Cuenta los cambios de línea que aparecen como estación duplicada."""
    clean_path = limpiar_estaciones(path)
    return sum(
        first == second
        for first, second in zip(clean_path, clean_path[1:])
    )


graph = crear_grafo()
