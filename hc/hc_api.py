# TSP con Hill Climning
from flask import Flask, jsonify, request
from flask_cors import CORS
import math
import random

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
CORS(app)

def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

# Calcular la distancia cubierta por cada ruta
def evalua_ruta(ruta):
    total = 0
    for i in range(0, len(ruta)-1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i+1]
        total = total + distancia(default_coord[ciudad1], default_coord[ciudad2])
    ciudad1 = ruta[i+1]
    ciudad2 = ruta[0]
    total = total + distancia(default_coord[ciudad1], default_coord[ciudad2])
    return total

def hill_climbing(coord):
    # Crear la ruta inicial Aleatoria
    ruta = []
    for ciudad in coord:
        ruta.append(ciudad)
    random.shuffle(ruta)

    mejora = True
    while mejora:
        mejora = False
        dist_actual = evalua_ruta(ruta)
        # Evaluar Vecinos
        for i in range (0, len(ruta)):
            if mejora:
                break
            for j in range(0, len(ruta)):
                if i!= j:
                    ruta_tmp = ruta[:]
                    ciudad_tmp = ruta[i]
                    ruta_tmp[i] = ruta_tmp[j]
                    ruta_tmp[j] = ciudad_tmp
                    dist = evalua_ruta(ruta_tmp)
                    if dist < dist_actual:
                        # Se ha encontrado un vecino que mejora el resultado
                        mejora = True
                        ruta = ruta_tmp[:]
                        break
    return ruta

@app.route('/hc', methods=['POST'])
def hc():
    print("Recibiendo peticion")
    data = request.json
    coord = data.get("coord", default_coord)
    ruta = hill_climbing(coord)
    return jsonify({"ruta": ruta, "distancia": evalua_ruta(ruta)})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
