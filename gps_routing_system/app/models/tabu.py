import random
from collections import deque
import requests
import re
from dotenv import load_dotenv
import os

load_dotenv()

API_ROUTE ='https://api.openrouteservice.org/v2/directions/driving-car/geojson'
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY no está configurada. Asegúrate de tener un archivo .env con la clave API_KEY.")


# 1. Distancia Manhattan
def distancia(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

# 2. Verificar secuencias prohibidas
def contiene_secuencia_prohibida(ruta, secuencias_prohibidas):
    for i in range(len(ruta) - 1):
        if (ruta[i], ruta[i+1]) in secuencias_prohibidas:
            return True
    return False

# 3. Evaluar la ruta con restricciones
def evalua_ruta(ruta, coord, secuencias_prohibidas):
    if contiene_secuencia_prohibida(ruta, secuencias_prohibidas):
        return float('inf')
    total = 0
    for i in range(len(ruta) - 1):
        total += distancia(coord[ruta[i]], coord[ruta[i+1]])
    total += distancia(coord[ruta[-1]], coord[ruta[0]])
    return total

def generar_vecinos(ruta):
    vecinos = []
    for i in range(len(ruta)):
        for j in range(i + 1, len(ruta)):
            vecino = ruta[:]
            vecino[i], vecino[j] = vecino[j], vecino[i]
            vecinos.append((vecino, (i, j)))
    return vecinos

def tabu_search(coord, iteraciones=100, tamaño_tabu=10, restricciones=None):
    # Filtrar ciudades excluidas
    ciudades_excluidas = set()
    if restricciones and "excluir_ciudades" in restricciones:
        ciudades_excluidas = set(restricciones["excluir_ciudades"])
        coord = {k: v for k, v in coord.items() if k not in ciudades_excluidas}

    secuencias_prohibidas = set()
    if restricciones and "prohibir_secuencias" in restricciones:
        print("Aplicando restricciones de secuencias prohibidas")
        print(restricciones["prohibir_secuencias"])
        secuencias_prohibidas = set(tuple(seq) for seq in restricciones["prohibir_secuencias"])

    ciudades = list(coord.keys())
    if not ciudades:
        raise ValueError("No hay ciudades disponibles tras aplicar las restricciones.")

    mejor_ruta = ciudades[:]
    random.shuffle(mejor_ruta)
    mejor_costo = evalua_ruta(mejor_ruta, coord, secuencias_prohibidas)

    actual_ruta = mejor_ruta[:]
    actual_costo = mejor_costo
    lista_tabu = deque(maxlen=tamaño_tabu)

    for it in range(iteraciones):
        vecinos = generar_vecinos(actual_ruta)
        vecinos.sort(key=lambda x: evalua_ruta(x[0], coord, secuencias_prohibidas))

        for vecino, movimiento in vecinos:
            if movimiento not in lista_tabu:
                costo = evalua_ruta(vecino, coord, secuencias_prohibidas)
                if costo < mejor_costo:
                    mejor_ruta = vecino[:]
                    mejor_costo = costo
                actual_ruta = vecino[:]
                actual_costo = costo
                lista_tabu.append(movimiento)
                break
    # obtener las coordenadas de la mejor ruta
    puntos = [coord[ciudad] for ciudad in mejor_ruta]
    # Obtener las coordenadas en formato [lng, lat] para cada punto
    coordinates = [[lng, lat] for lat, lng in puntos]
    # Hacer peticion a la API de OpenRouteService con el body las coordenadas
    print(coordinates)
    body = {
        "coordinates": coordinates,
        "language": "es",
        "instructions": "true"
    }
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(
            API_ROUTE,
            headers=headers,
            json=body,
            params={"api_key": API_KEY},
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            try:
                error_json = response.json()
                if error_json.get("error", {}).get("code") == 2010:
                    msg = error_json["error"]["message"]
                    # Extraer la coordenada que falló
                    match = re.search(r"coordinate \d+: (-?\d+\.\d+) (-?\d+\.\d+)", msg)
                    if match:
                        lng_str, lat_str = match.groups()
                        lat, lng = float(lat_str), float(lng_str)

                        # Buscar el nombre del punto correspondiente
                        for nombre, (p_lat, p_lng) in coord.items():
                            if abs(p_lat - lat) < 0.0005 and abs(p_lng - lng) < 0.0005:
                                raise ValueError(
                                    f"No se pudo encontrar una vía cercana a menos de 350 metros para el punto **{nombre}**.\n\n"
                                    "Algunas razones posibles:\n"
                                    "- Seleccionaste un punto en un lugar alejado de calles (por ejemplo, un parque, lago, terreno baldío o edificio sin acceso vial).\n"
                                    "- Si el punto está fuera de la red de carreteras, el cálculo de ruta falla."
                                ) from e
            except Exception as parse_error:
                raise ValueError(f"Error al analizar respuesta 404: {parse_error}") from parse_error
        raise requests.exceptions.HTTPError(f"Error al obtener la ruta: {response.status_code} - {response.text}")

    data = response.json()
    # print(data)


    return {
        "ruta": mejor_ruta,
        "data": data
    }

# Ejemplo de uso
if __name__ == "__main__":
    coord = {
        'Jiloyork': (19.91, -99.58),
        'Toluca': (19.28, -99.65),
        'Atlacomulco': (19.79, -99.87),
        'Guadalajara': (20.68, -103.34),
        'Monterrey': (25.69, -100.32),
        'QuintanaRoo': (21.16, -86.80),
        'Michoacan': (19.70, -101.20),
        'Aguascalientes': (21.87, -102.26),
        'CDMX': (19.43, -99.13),
        'QRO': (20.59, -100.38)
    }

    restricciones = {
        # "excluir_ciudades": ['QuintanaRoo'],
        "prohibir_secuencias": [('CDMX', 'Toluca'), ('Guadalajara', 'Michoacan'), ("Jiloyork", "Toluca")]
    }

    resultado = tabu_search(coord, iteraciones=200, tamaño_tabu=20, restricciones=restricciones)
    ruta = resultado['ruta']
    distancia_total = resultado['distancia']
    print("Mejor ruta encontrada:")
    print(ruta)
    print("Distancia total:", distancia_total)
    print("Ruta con coordenadas:")
    for ciudad in ruta:
        print(f"{ciudad}: {coord[ciudad]}")
    
