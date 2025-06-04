# TSP con templado simulado
import math
import random

def distancia(coord1, coord2):
    """Calcula la distancia euclidiana entre dos coordenadas."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def evalua_ruta(ruta, coord):
    """Evalua la distancia total de una ruta."""
    total = 0
    for i in range(len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    # Regresar al punto de inicio para cerrar el ciclo
    total += distancia(coord[ruta[-1]], coord[ruta[0]])
    return total

def simulated_annealing(ruta, coord):
    """Aplica el algoritmo de templado simulado para encontrar la mejor ruta."""
    T = 1000
    T_MIN = 1e-8
    V_ENFRIAMIENTO = 0.995

    mejor_ruta = ruta[:]
    mejor_dist = evalua_ruta(mejor_ruta, coord)

    while T > T_MIN:
        # Generar vecino intercambiando dos ciudades
        i, j = random.sample(range(len(ruta)), 2)
        nueva_ruta = ruta[:]
        nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]

        dist_actual = evalua_ruta(ruta, coord)
        dist_nueva = evalua_ruta(nueva_ruta, coord)
        delta = dist_nueva - dist_actual

        # Aceptar si es mejor o con cierta probabilidad si es peor
        if delta < 0 or random.random() < math.exp(-delta / T):
            ruta = nueva_ruta[:]
            if dist_nueva < mejor_dist:
                mejor_ruta = ruta[:]
                mejor_dist = dist_nueva

        T *= V_ENFRIAMIENTO

    return mejor_ruta, mejor_dist

# Ejemplo de uso:
if __name__ == "__main__":
    # Coordenadas de ejemplo: ciudades con (x, y)
    coord = {
        0: (0, 0),
        1: (1, 5),
        2: (5, 2),
        3: (6, 6),
        4: (8, 3)
    }
    ruta_inicial = list(coord.keys())
    random.shuffle(ruta_inicial)
    mejor_ruta, mejor_dist = simulated_annealing(ruta_inicial, coord)
    print("Mejor ruta encontrada:", mejor_ruta)
    print("Distancia total:", mejor_dist)