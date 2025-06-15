import random

def distancia(c1, c2):
    """Distancia de Manhattan entre dos coordenadas"""
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])

def contiene_secuencia_prohibida(ruta, secuencias_prohibidas):
    """Verifica si una ruta contiene alguna secuencia prohibida"""
    for i in range(len(ruta) - 1):
        par = (ruta[i], ruta[i + 1])
        if par in secuencias_prohibidas:
            return True
    return False

def evalua_ruta(ruta, coord):
    total = 0
    for i in range(len(ruta) - 1):
        total += distancia(coord[ruta[i]], coord[ruta[i + 1]])
    total += distancia(coord[ruta[-1]], coord[ruta[0]])  # Cierra ciclo
    return total

def hill_climbing(coord, restricciones=None):
    ciudades = list(coord.keys())

    # Aplicar restricciones de ciudades excluidas
    if restricciones and "excluir_ciudades" in restricciones:
        ciudades = [c for c in ciudades if c not in restricciones["excluir_ciudades"]]

    secuencias_prohibidas = set()
    if restricciones and "prohibir_secuencias" in restricciones:
        secuencias_prohibidas = set(tuple(seq) for seq in restricciones["prohibir_secuencias"])

    # Ruta inicial aleatoria
    ruta = ciudades[:]
    random.shuffle(ruta)

    mejora = True
    while mejora:
        mejora = False
        dist_actual = evalua_ruta(ruta, coord)

        for i in range(len(ruta)):
            for j in range(i + 1, len(ruta)):
                ruta_tmp = ruta[:]
                ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
                if contiene_secuencia_prohibida(ruta_tmp, secuencias_prohibidas):
                    continue
                dist_tmp = evalua_ruta(ruta_tmp, coord)
                if dist_tmp < dist_actual:
                    ruta = ruta_tmp
                    mejora = True
                    break
            if mejora:
                break

    return ruta, evalua_ruta(ruta, coord)

# -------------------------
# Ejemplo de uso
# -------------------------
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
        "prohibir_secuencias": [("CDMX", "Toluca"), ("Guadalajara", "QRO")]
    }

    ruta_final = hill_climbing(coord, restricciones)
    print("Ruta óptima:", ruta_final)
    print("Distancia total:", evalua_ruta(ruta_final, coord))
