from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import random
from collections import deque

app = Flask(__name__)
CORS(app)

COORDENADAS_DEFECTO = {
    'Jiloyork': (19.916012, -99.580580),
    'Toluca': (19.289165, -99.655697),
    'Atlacomulco': (19.799520, -99.873844),
    'Guadalajara': (20.677754472859146, -103.34625354877137),
    'Monterrey': (25.69161110159454, -100.321838480256),
    'QuintanaRoo': (21.163111924844458, -86.80231502121464),
    'Michohacan': (19.701400113725654, -101.20829680213464),
    'Aguascalientes': (21.87641043660486, -102.26438663286967),
    'CDMX': (19.432713075976878, -99.13318344772986),
    'QRO': (20.59719437542255, -100.38667040246602)
}

def distancia(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def evalua_ruta(ruta, coord):
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

def tabu_search(coord, iteraciones=100, tamaño_tabu=10):
    ciudades = list(coord.keys())
    mejor_ruta = ciudades[:]
    random.shuffle(mejor_ruta)
    mejor_costo = evalua_ruta(mejor_ruta, coord)

    actual_ruta = mejor_ruta[:]
    actual_costo = mejor_costo
    lista_tabu = deque(maxlen=tamaño_tabu)

    for _ in range(iteraciones):
        vecinos = generar_vecinos(actual_ruta)
        vecinos.sort(key=lambda x: evalua_ruta(x[0], coord))

        for vecino, movimiento in vecinos:
            if movimiento not in lista_tabu:
                costo = evalua_ruta(vecino, coord)
                if costo < mejor_costo:
                    mejor_ruta = vecino[:]
                    mejor_costo = costo
                actual_ruta = vecino[:]
                actual_costo = costo
                lista_tabu.append(movimiento)
                break
    return mejor_ruta, mejor_costo

@app.route('/api/tabu-tsp', methods=['POST'])
def resolver_tsp():
    data = request.get_json(silent=True) or {}

    coord = data.get("coord", COORDENADAS_DEFECTO)
    iteraciones = data.get("iteraciones", 100)
    tamaño_tabu = data.get("tabu_tam", 10)
    # print("DATA RECIBIDA:", {
    #     "coord": coord,
    #     "iteraciones": iteraciones,
    #     "tamaño_tabu": tamaño_tabu
    # })

    try:
        ruta, distancia_total = tabu_search(coord, iteraciones, tamaño_tabu)
        return jsonify({
            "ruta": ruta,
            "distancia": distancia_total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
