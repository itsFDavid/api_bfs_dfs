import math
import random

def distancia(c1, c2):
    """Distancia de Manhattan entre dos coordenadas"""
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])

def contiene_secuencia_prohibida(ruta, secuencias_prohibidas):
    """Verifica si una ruta contiene alguna secuencia prohibida"""
    for i in range(len(ruta) - 1):
        if (ruta[i], ruta[i + 1]) in secuencias_prohibidas:
            return True
    return False

def evalua_ruta(ruta, coord, secuencias_prohibidas):
    """Evalúa la ruta calculando la distancia total o devuelve infinito si viola restricciones"""
    if contiene_secuencia_prohibida(ruta, secuencias_prohibidas):
        return float('inf')
    total = 0
    for i in range(len(ruta) - 1):
        total += distancia(coord[ruta[i]], coord[ruta[i + 1]])
    # Para ciclo cerrado, sumar distancia del último al primero (opcional)
    # total += distancia(coord[ruta[-1]], coord[ruta[0]])
    return total

def generar_vecino(ruta):
    """Genera un vecino intercambiando dos ciudades al azar"""
    vecino = ruta[:]
    i, j = random.sample(range(len(ruta)), 2)
    vecino[i], vecino[j] = vecino[j], vecino[i]
    return vecino

def simulated_annealing(coord, iteraciones=1000, temp_inicial=1000, temp_final=1, enfriamiento=0.995, restricciones=None):
    ciudades = list(coord.keys())

    if restricciones and "excluir_ciudades" in restricciones:
        ciudades = [c for c in ciudades if c not in restricciones["excluir_ciudades"]]

    secuencias_prohibidas = set()
    if restricciones and "prohibir_secuencias" in restricciones:
        secuencias_prohibidas = set(tuple(seq) for seq in restricciones["prohibir_secuencias"])

    actual = ciudades[:]
    random.shuffle(actual)
    mejor = actual[:]

    costo_actual = evalua_ruta(actual, coord, secuencias_prohibidas)
    costo_mejor = costo_actual

    temperatura = temp_inicial

    for i in range(iteraciones):
        vecino = generar_vecino(actual)
        costo_vecino = evalua_ruta(vecino, coord, secuencias_prohibidas)

        delta = costo_vecino - costo_actual

        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            actual = vecino
            costo_actual = costo_vecino
            if costo_actual < costo_mejor:
                mejor = actual
                costo_mejor = costo_actual

        temperatura = max(temperatura * enfriamiento, temp_final)

    return mejor, costo_mejor

# Ejemplo de uso:
if __name__ == "__main__":
    coord = {
        'Jiloyork': (19.916012, -99.580580),
        'Toluca': (19.289165, -99.655697),
        'Atlacomulco': (19.799520, -99.873844),
        'Guadalajara': (20.677754, -103.346254),
        'Monterrey': (25.691611, -100.321838),
        'QuintanaRoo': (21.163112, -86.802315),
        'Michohacan': (19.701400, -101.208297),
        'Aguascalientes': (21.876410, -102.264387),
        'CDMX': (19.432713, -99.133183),
        'QRO': (20.597194, -100.386670)
    }

    restricciones = {
        # "excluir_ciudades": ["QuintanaRoo", "Monterrey"],
        "prohibir_secuencias": [("Toluca", "CDMX"), ("Guadalajara", "Michoacan")]
    }

    mejor_ruta, mejor_costo = simulated_annealing(coord, iteraciones=5000, temp_inicial=1000, alpha=0.995, restricciones=restricciones)
    print("Mejor ruta encontrada:", mejor_ruta)
    print("Costo (distancia total):", mejor_costo)
