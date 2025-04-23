from flask import Flask, request, jsonify
from flask_cors import CORS
import math
from operator import itemgetter

app = Flask(__name__)
CORS(app)

# Datos por defecto
coord_default = {
    'EDO.MEX': (19.29370432359307, -99.65371080401178),
    'QRO': (20.593507359686654, -100.39007276165671),
    'CDMX': (19.43291511136525, -99.13336444220519),
    'SPL': (22.15093335177082, -100.97414039898334),
    'MTY': (25.67505869471195, -100.28758283172263),
    'PUE': (19.063633672407946, -98.3069909799001),
    'GDL': (20.677204573193357, -103.34699475549439),
    'MICH': (19.702594693971918, -101.1923828770145),
    'SON': (29.075226304565465, -110.95962477492)
}

pedidos_default = {
    'EDO.MEX': 10,
    'QRO': 13,
    'CDMX': 7,
    'SPL': 11,
    'MTY': 15,
    'PUE': 8,
    'GDL': 6,
    'MICH': 7,
    'SON': 8
}

almacen_default = [19.29370432359307, -99.65371080401178]
max_carga_default = 40
tiempo_maximo_default = 8
velocidad_promedio_default = 60
tiempo_carga_por_unidad_default = 0.15

def distancia(c1, c2):
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

def en_ruta(rutas, ciudad):
    for r in rutas:
        if ciudad in r:
            return r
    return None

def peso_ruta(ruta, pedidos):
    return sum(pedidos[c] for c in ruta)

def tiempo_viaje(c1, c2, coord, v):
    return distancia(coord[c1], coord[c2]) / v

def tiempo_viaje_desde_almacen(ciudad, coord, almacen, v):
    return distancia(almacen, coord[ciudad]) / v

def tiempo_viaje_hasta_almacen(ciudad, coord, almacen, v):
    return distancia(coord[ciudad], almacen) / v

def tiempo_total_ruta(ruta, coord, v, pedidos, t_carga, almacen):
    total = tiempo_viaje_desde_almacen(ruta[0], coord, almacen, v)
    for i in range(len(ruta) - 1):
        total += tiempo_viaje(ruta[i], ruta[i + 1], coord, v)
    total += tiempo_viaje_hasta_almacen(ruta[-1], coord, almacen, v)
    total += sum(pedidos[c] * t_carga for c in ruta)
    return total

def vrp_voraz(coord, almacen, max_carga, pedidos, tiempo_max, v, t_carga):
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2 and (c2, c1) not in s:
                s[c1, c2] = distancia(coord[c1], almacen) + distancia(coord[c2], almacen) - distancia(coord[c1], coord[c2])
    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    rutas = []
    for (c1, c2), _ in s:
        r1 = en_ruta(rutas, c1)
        r2 = en_ruta(rutas, c2)

        if r1 is None and r2 is None:
            if peso_ruta([c1, c2], pedidos) <= max_carga:
                rutas.append([c1, c2])
        elif r1 is not None and r2 is None:
            if r1[0] == c1 and peso_ruta(r1, pedidos) + pedidos[c2] <= max_carga:
                r1.insert(0, c2)
            elif r1[-1] == c1 and peso_ruta(r1, pedidos) + pedidos[c2] <= max_carga:
                r1.append(c2)
        elif r1 is None and r2 is not None:
            if r2[0] == c2 and peso_ruta(r2, pedidos) + pedidos[c1] <= max_carga:
                r2.insert(0, c1)
            elif r2[-1] == c2 and peso_ruta(r2, pedidos) + pedidos[c1] <= max_carga:
                r2.append(c1)
        elif r1 != r2:
            nueva_ruta = r1 + r2
            if peso_ruta(nueva_ruta, pedidos) <= max_carga and tiempo_total_ruta(nueva_ruta, coord, v, pedidos, t_carga, almacen) <= tiempo_max:
                rutas[rutas.index(r1)] = nueva_ruta
                rutas.remove(r2)
    return rutas

@app.route("/api/vrp", methods=["POST"])
def calcular_vrp():
    data = request.json

    coord = data.get("coord", coord_default)
    pedidos = data.get("pedidos", pedidos_default)
    almacen = data.get("almacen", almacen_default)
    max_carga = data.get("max_carga", max_carga_default)
    tiempo_maximo = data.get("tiempo_maximo", tiempo_maximo_default)
    velocidad_promedio = data.get("velocidad_promedio", velocidad_promedio_default)
    tiempo_carga_por_unidad = data.get("tiempo_carga_por_unidad", tiempo_carga_por_unidad_default)

    rutas = vrp_voraz(coord, almacen, max_carga, pedidos, tiempo_maximo, velocidad_promedio, tiempo_carga_por_unidad)
    if not rutas:
        return jsonify({"error": "No se encontraron rutas viables."}), 400
    resultados = []
    for ruta in rutas:
        carga = peso_ruta(ruta, pedidos)
        tiempo = tiempo_total_ruta(ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen)
        horas = int(tiempo)
        minutos = round((tiempo - horas) * 60)
        resultados.append({
            "ruta": ruta,
            "carga": carga,
            "tiempo_estimado": f"{horas} hrs {minutos} min",
            "tiempo_total": tiempo,
        })

    return jsonify({"rutas": resultados})

if __name__ == "__main__":
    entry_endpoint = "http://localhost:5001"
    endpoints = [
        "/api/vrp"
    ]
    for endpoint in endpoints:
        # endpoint en color rojo
        print(f"\033[91mEndpoint: {entry_endpoint}{endpoint}\033[0m")
    app.run(debug=True, host="0.0.0.0", port=5001)
