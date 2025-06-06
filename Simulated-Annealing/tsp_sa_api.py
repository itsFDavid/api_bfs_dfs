# TSP con templado simulado
import math
import random
from flask import Flask, jsonify, request
import flask_cors

default_coord = {
    'Jiloyork' :(19.916012, -99.580580),
    'Toluca':(19.289165, -99.655697),
    'Atlacomulco':(19.799520, -99.873844),
    'Guadalajara':(20.677754472859146, -103.34625354877137),
    'Monterrey':(25.69161110159454, -100.321838480256),
    'QuintanaRoo':(21.163111924844458, -86.80231502121464),
    'Michohacan':(19.701400113725654, -101.20829680213464),
    'Aguascalientes':(21.87641043660486, -102.26438663286967),
    'CDMX':(19.432713075976878, -99.13318344772986),
    'QRO':(20.59719437542255, -100.38667040246602)
}

app = Flask(__name__)
flask_cors.CORS(app)

def distancia(coord1, coord2):
    """Calcula la distancia entre dos coordenadas."""
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

# Calcular la distancia cubierta por una ruta
def evalua_ruta(ruta, coord):
    """Evalua la distancia total de una ruta."""
    total = 0
    for i in range(0, len(ruta)-1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i+1]
        total = total + distancia(coord[ciudad1], coord[ciudad2])
    ciudad1 = ruta[i+1]
    ciudad2 = ruta[0]
    total = total + distancia(coord[ciudad1], coord[ciudad2])
    return total

def simulated_annealing(ruta, coord, Temperatura = 20):
    """Aplica el algoritmo de templado simulado para encontrar la mejor ruta."""
    T = Temperatura
    T_MIN = 0
    V_ENFRIAMIENTO = 100

    while T > T_MIN:
        dist_actual = evalua_ruta(ruta, coord)
        for i in range(1, V_ENFRIAMIENTO):
            # intercamio de 2 ciudades aleatoriamente
            i = random.randint(0, len(ruta) -1)
            j = random.randint(0, len(ruta) -1)
            ruta_tmp = ruta[:]
            ciudad_tmp = ruta_tmp[i]
            ruta_tmp[i] = ruta_tmp[j]
            ruta_tmp[j] = ciudad_tmp
            dist_evalua_ruta = evalua_ruta(ruta_tmp, coord)
            delta = dist_evalua_ruta - dist_actual
            if(delta < dist_actual):
                ruta = ruta_tmp[:]
                break
        # enfriar a T linealmente
        T = T - 0.005

    return ruta

# if __name__ == "__main__":
#     coord = {
#         'Jiloyork' :(19.916012, -99.580580),
#         'Toluca':(19.289165, -99.655697),
#         'Atlacomulco':(19.799520, -99.873844),
#         'Guadalajara':(20.677754472859146, -103.34625354877137),
#         'Monterrey':(25.69161110159454, -100.321838480256),
#         'QuintanaRoo':(21.163111924844458, -86.80231502121464),
#         'Michohacan':(19.701400113725654, -101.20829680213464),
#         'Aguascalientes':(21.87641043660486, -102.26438663286967),
#         'CDMX':(19.432713075976878, -99.13318344772986),
#         'QRO':(20.59719437542255, -100.38667040246602)
#     }

#     # Crear una ruta inicial aleatoria
#     ruta = []
#     for ciudad in coord:
#         ruta.append(ciudad)

#     random.shuffle(ruta)
#     print("Ruta Inicial: " + str(ruta))
#     mejor_ruta = simulated_annealing(ruta, coord)
#     print("Mejor ruta encontrada: " + str(mejor_ruta))
#     print("Distancia Total: " + str(evalua_ruta(mejor_ruta, coord)))

@app.route('/tsp-sa', methods=['POST'])
def tsp_sa():
    data = request.json
    coord = data.get("coord", default_coord)
    temperatura = data.get("temperatura", 20)
    ruta = data.get("ruta", list(coord.keys()))
    random.shuffle(ruta)
    mejor_ruta = simulated_annealing(ruta, coord, temperatura)
    mejor_dist = evalua_ruta(mejor_ruta, coord)
    return jsonify({
        "ruta": ruta,
        "distancia": evalua_ruta(ruta, coord),
        "mejor_ruta": mejor_ruta,
        "mejor_distancia": mejor_dist,
        "temperatura": temperatura
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')