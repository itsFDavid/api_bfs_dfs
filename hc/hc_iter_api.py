from flask import Flask, jsonify, request
from flask_cors import CORS
import math
import random

default_coord = {
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

app = Flask(__name__)
CORS(app)

def distancia(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def evalua_ruta(ruta, coord):
    total = 0
    for i in range(len(ruta) - 1):
        total += distancia(coord[ruta[i]], coord[ruta[i + 1]])
    total += distancia(coord[ruta[-1]], coord[ruta[0]])
    return total

def i_hill_climbing(coord, max_iteraciones=10):
    ciudades = list(coord.keys())
    mejor_ruta = None
    mejor_distancia = float('inf')

    while max_iteraciones > 0:
        ruta = list(coord.keys())
        random.shuffle(ruta)

        mejora = True
        while mejora:
            mejora = False
            dist_actual = evalua_ruta(ruta, coord)
            for i in range(len(ruta)):
                for j in range(i + 1, len(ruta)):
                    ruta_tmp = ruta[:]
                    ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
                    nueva_dist = evalua_ruta(ruta_tmp, coord)
                    if nueva_dist < dist_actual:
                        ruta = ruta_tmp
                        mejora = True
                        break
                if mejora:
                    break

        distancia_ruta = evalua_ruta(ruta, coord)
        print(f"Iteración {11 - max_iteraciones}: distancia = {distancia_ruta}")
        if distancia_ruta < mejor_distancia:
            mejor_distancia = distancia_ruta
            mejor_ruta = ruta[:]

        max_iteraciones -= 1

    return mejor_ruta, mejor_distancia

@app.route('/ihc', methods=['POST'])
def ihc():
    print("Recibiendo petición para Iterative Hill Climbing")
    data = request.json
    coord = data.get("coord", default_coord)
    ruta, distancia_total = i_hill_climbing(coord)
    return jsonify({"ruta": ruta, "distancia": distancia_total})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
