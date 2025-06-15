import random
from collections import deque, defaultdict
import math
import heapq
import json
from typing import List, Dict, Tuple, Optional

# ----------------------------
# MODELO DE DATOS PARA RUTAS
# ----------------------------

class RouteStep:
    def __init__(self, distance: float, duration: float, instruction: str, 
                 name: str, way_points: List[int], type: int):
        self.distance = distance
        self.duration = duration
        self.instruction = instruction
        self.name = name
        self.way_points = way_points
        self.type = type

class RouteSegment:
    def __init__(self, distance: float, duration: float, steps: List[RouteStep]):
        self.distance = distance
        self.duration = duration
        self.steps = steps

class RouteResponse:
    def __init__(self, geometry: Dict, properties: Dict):
        self.geometry = geometry
        self.properties = properties

# ----------------------------
# GRAFO DE CALLES (SIMULACIÓN)
# ----------------------------

class StreetGraph:
    def __init__(self):
        self.nodes = {}  # {node_id: (lat, lon)}
        self.edges = defaultdict(list)  # {node_id: [(neighbor_id, street_name, length_meters)]}
        self.street_data = {}  # {(node1, node2): {'name': str, 'oneway': bool}}
    
    def add_node(self, node_id: int, lat: float, lon: float):
        self.nodes[node_id] = (lat, lon)
    
    def add_street(self, node1: int, node2: int, name: str, length: float, oneway: bool = False):
        self.edges[node1].append((node2, name, length))
        self.street_data[(node1, node2)] = {'name': name, 'oneway': oneway}
        if not oneway:
            self.edges[node2].append((node1, name, length))
            self.street_data[(node2, node1)] = {'name': name, 'oneway': oneway}
    
    def get_neighbors(self, node_id: int) -> List[Tuple[int, str, float]]:
        return self.edges.get(node_id, [])
    
    def get_street_name(self, node1: int, node2: int) -> str:
        return self.street_data.get((node1, node2), {}).get('name', 'Unknown Street')
    
    def is_oneway(self, node1: int, node2: int) -> bool:
        return self.street_data.get((node1, node2), {}).get('oneway', False)

# ----------------------------
# ALGORITMOS DE RUTA
# ----------------------------

def haversine_distance(node1: Tuple[float, float], node2: Tuple[float, float]) -> float:
    """Calcula la distancia en metros entre dos puntos geográficos."""
    lat1, lon1 = node1
    lat2, lon2 = node2
    
    R = 6371000  # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def a_star_path(graph: StreetGraph, start: int, end: int) -> Optional[List[int]]:
    """Implementación del algoritmo A* para encontrar la ruta más corta."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start] = 0
    
    f_score = {node: float('inf') for node in graph.nodes}
    f_score[start] = haversine_distance(graph.nodes[start], graph.nodes[end])
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        
        for neighbor, street_name, length in graph.get_neighbors(current):
            tentative_g_score = g_score[current] + length
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + haversine_distance(
                    graph.nodes[neighbor], graph.nodes[end])
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return None

def generate_realistic_path(graph: StreetGraph, path: List[int]) -> Dict:
    """Genera una ruta realista con geometría y propiedades similares a OpenRouteService."""
    coordinates = []
    properties = {
        "segments": [],
        "way_points": []
    }
    
    current_segment = {
        "distance": 0,
        "duration": 0,
        "steps": []
    }
    
    current_step = None
    current_street = None
    step_waypoints = []
    
    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i + 1]
        
        # Obtener información de la calle
        street_name = graph.get_street_name(node1, node2)
        street_length = next((l for n, s, l in graph.get_neighbors(node1) if n == node2 and s == street_name), 0)
        
        # Generar puntos intermedios (simulados)
        start_coord = graph.nodes[node1]
        end_coord = graph.nodes[node2]
        num_points = max(2, int(street_length // 10))  # Un punto cada ~10 metros
        segment_coords = []
        
        for j in range(num_points):
            t = j / (num_points - 1)
            lat = start_coord[0] + t * (end_coord[0] - start_coord[0])
            lon = start_coord[1] + t * (end_coord[1] - start_coord[1])
            segment_coords.append([lon, lat])  # OpenRouteService usa [lon, lat]
        
        # Manejar cambios de calle
        if street_name != current_street:
            if current_step is not None:
                # Finalizar el paso anterior
                current_step["way_points"] = [len(coordinates) - len(step_waypoints), len(coordinates)]
                current_segment["steps"].append(current_step)
                step_waypoints = []
            
            # Crear nuevo paso
            bearing = calculate_bearing(start_coord, end_coord)
            direction = get_direction_name(bearing)
            
            current_step = {
                "distance": 0,
                "duration": 0,
                "type": 1,  # 1 = turn, 11 = depart
                "instruction": f"Continue on {street_name} toward {direction}",
                "name": street_name,
                "way_points": []
            }
            current_street = street_name
        
        # Actualizar paso actual
        current_step["distance"] += street_length
        current_step["duration"] += street_length / 13.89  # Asumiendo 50 km/h
        
        # Agregar coordenadas
        coordinates.extend(segment_coords)
        step_waypoints.extend(segment_coords)
    
    # Finalizar el último paso y segmento
    if current_step is not None:
        current_step["way_points"] = [len(coordinates) - len(step_waypoints), len(coordinates)]
        current_segment["steps"].append(current_step)
        current_segment["distance"] = sum(s["distance"] for s in current_segment["steps"])
        current_segment["duration"] = sum(s["duration"] for s in current_segment["steps"])
        properties["segments"].append(current_segment)
    
    return {
        "geometry": {
            "coordinates": coordinates,
            "type": "LineString"
        },
        "properties": properties
    }

# ----------------------------
# FUNCIONES AUXILIARES
# ----------------------------

def calculate_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calcula el rumbo entre dos puntos en grados (0-360)."""
    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
    
    delta_lon = lon2 - lon1
    
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

def get_direction_name(bearing: float) -> str:
    """Convierte un rumbo en grados a una dirección cardinal."""
    directions = ["north", "northeast", "east", "southeast", 
                 "south", "southwest", "west", "northwest"]
    index = round(bearing / 45) % 8
    return directions[index]

def generate_realistic_street_graph(city_coords: Dict[str, Tuple[float, float]]) -> StreetGraph:
    """Genera un grafo de calles realista para las ciudades dadas."""
    graph = StreetGraph()
    
    # Asignar IDs numéricos a las ciudades
    city_ids = {city: idx for idx, city in enumerate(city_coords.keys(), start=1)}
    
    # Agregar nodos (ciudades)
    for city, node_id in city_ids.items():
        graph.add_node(node_id, *city_coords[city])
    
    # Conectar ciudades cercanas con calles simuladas
    cities = list(city_coords.keys())
    for i in range(len(cities)):
        for j in range(i+1, len(cities)):
            city1 = cities[i]
            city2 = cities[j]
            dist = haversine_distance(city_coords[city1], city_coords[city2])
            
            # Solo conectar ciudades relativamente cercanas (menos de 300 km)
            if dist < 300000:
                street_name = f"{city1}-{city2} Highway"
                graph.add_street(city_ids[city1], city_ids[city2], street_name, dist)
    
    # Agregar calles locales con más detalle
    for city, node_id in city_ids.items():
        # Crear una pequeña red de calles locales
        for k in range(4):
            # Nodos intermedios
            local_node_id = len(city_ids) + k + 1
            lat = city_coords[city][0] + random.uniform(-0.01, 0.01)
            lon = city_coords[city][1] + random.uniform(-0.01, 0.01)
            graph.add_node(local_node_id, lat, lon)
            
            # Conectar a la ciudad principal
            street_name = f"{city} Local Road {k+1}"
            length = haversine_distance(city_coords[city], (lat, lon))
            graph.add_street(node_id, local_node_id, street_name, length)
            
            # Conectar entre nodos locales
            if k > 0:
                prev_local_node = len(city_ids) + k
                street_name = f"{city} Inner Street {k}"
                length = haversine_distance(graph.nodes[prev_local_node], (lat, lon))
                graph.add_street(prev_local_node, local_node_id, street_name, length)
    
    return graph, city_ids

# ----------------------------
# ALGORITMO DE OPTIMIZACIÓN
# ----------------------------

def tabu_search_ors(coord: Dict[str, Tuple[float, float]], 
                   iteraciones: int = 100, 
                   tamaño_tabu: int = 10, 
                   restricciones: Optional[Dict] = None) -> Dict:
    """Algoritmo Tabu Search que devuelve resultados en formato similar a OpenRouteService."""
    # Procesar restricciones
    ciudades_excluidas = set(restricciones.get("excluir_ciudades", [])) if restricciones else set()
    secuencias_prohibidas = set(tuple(seq) for seq in restricciones.get("prohibir_secuencias", [])) if restricciones else set()
    
    # Filtrar ciudades excluidas
    coord_filtradas = {k: v for k, v in coord.items() if k not in ciudades_excluidas}
    
    # Generar grafo de calles realista
    street_graph, city_ids = generate_realistic_street_graph(coord_filtradas)
    
    # Algoritmo Tabu Search para optimizar el orden de ciudades
    ciudades = list(coord_filtradas.keys())
    mejor_ruta = ciudades.copy()
    random.shuffle(mejor_ruta)
    
    # Función para evaluar una ruta
    def evaluar_ruta(ruta):
        # Verificar secuencias prohibidas
        for i in range(len(ruta) - 1):
            if (ruta[i], ruta[i+1]) in secuencias_prohibidas:
                return float('inf')
        
        # Calcular distancia total
        total = 0
        for i in range(len(ruta) - 1):
            path = a_star_path(street_graph, city_ids[ruta[i]], city_ids[ruta[i+1]])
            if path:
                for j in range(len(path) - 1):
                    for neighbor, name, length in street_graph.get_neighbors(path[j]):
                        if neighbor == path[j+1]:
                            total += length
                            break
        return total
    
    mejor_distancia = evaluar_ruta(mejor_ruta)
    lista_tabu = deque(maxlen=tamaño_tabu)
    
    for _ in range(iteraciones):
        # Generar vecinos intercambiando dos ciudades
        vecinos = []
        for i in range(len(ciudades)):
            for j in range(i+1, len(ciudades)):
                vecino = mejor_ruta.copy()
                vecino[i], vecino[j] = vecino[j], vecino[i]
                vecinos.append(vecino)
        
        # Evaluar vecinos
        mejor_vecino = None
        mejor_vecino_distancia = float('inf')
        
        for vecino in vecinos:
            if tuple(vecino) not in lista_tabu:
                distancia = evaluar_ruta(vecino)
                if distancia < mejor_vecino_distancia:
                    mejor_vecino = vecino
                    mejor_vecino_distancia = distancia
        
        # Actualizar mejor solución
        if mejor_vecino is not None and mejor_vecino_distancia < mejor_distancia:
            mejor_ruta = mejor_vecino
            mejor_distancia = mejor_vecino_distancia
            lista_tabu.append(tuple(mejor_ruta))
    
    # Generar la ruta detallada en formato OpenRouteService
    geometry_coords = []
    properties_segments = []
    way_points = []
    current_waypoint = 0
    
    for i in range(len(mejor_ruta) - 1):
        city1 = mejor_ruta[i]
        city2 = mejor_ruta[i+1]
        path = a_star_path(street_graph, city_ids[city1], city_ids[city2])
        
        if path:
            # Generar segmento detallado
            segment = generate_realistic_path(street_graph, path)
            
            # Agregar coordenadas
            geometry_coords.extend(segment["geometry"]["coordinates"])
            
            # Actualizar waypoints
            way_points.append(current_waypoint)
            current_waypoint += len(segment["geometry"]["coordinates"])
            
            # Agregar segmento a propiedades
            properties_segments.extend(segment["properties"]["segments"])
    
    # Agregar último waypoint
    way_points.append(current_waypoint - 1)
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": geometry_coords
                },
                "properties": {
                    "segments": properties_segments,
                    "way_points": way_points,
                    "summary": {
                        "distance": sum(s["distance"] for s in properties_segments),
                        "duration": sum(s["duration"] for s in properties_segments)
                    }
                }
            }
        ]
    }

# ----------------------------
# EJEMPLO DE USO
# ----------------------------

if __name__ == "__main__":
    coord = {
        "Jiloyork": [19.91, -99.58],
        "Toluca": [19.28, -99.65],
        "Atlacomulco": [19.79, -99.87],
        "Guadalajara": [20.68, -103.34],
        "Monterrey": [25.69, -100.32],
        "QuintanaRoo": [21.16, -86.80],
        "Michoacan": [19.70, -101.20],
        "Aguascalientes": [21.87, -102.26],
        "CDMX": [19.43, -99.13],
        "QRO": [20.59, -100.38]
    }

    restricciones = {
        "excluir_ciudades": [],
        "prohibir_secuencias": [
            ["CDMX", "Toluca"],
            ["Toluca", "CDMX"]
        ]
    }

    resultado = tabu_search_ors(
        coord=coord,
        iteraciones=50,
        tamaño_tabu=15,
        restricciones=restricciones
    )

    print(json.dumps(resultado, indent=2))
