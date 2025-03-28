# Vuelos con busqueda ocn profundidad iterativa
from arbol import Nodo
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
# from DFS_rec import buscar_solucion_DFS_rec

def DFS_prof_iter(nodo, solucion, conexiones):
    for limite in range(0, 100):
        visitados = []
        sol = buscar_solucion_DFS_rec(nodo, solucion, visitados, limite, conexiones)

        if sol is not None:
            return sol

def buscar_solucion_DFS_rec(nodo, solucion, visitados, limite, conexiones):
    if limite > 0:
        visitados.append(nodo)
        if nodo.get_datos() == solucion:
            return nodo
        # expandir nodos hijo (ciudades con conexion)
        dato_nodo = nodo.get_datos()
        lista_hijos = []
        for un_hijo in conexiones[dato_nodo]:
            if not un_hijo in visitados:
                hijo_nodo = Nodo(un_hijo)
                lista_hijos.append(hijo_nodo)
        nodo.set_hijos(lista_hijos)

        for nodo_hijo in nodo.get_hijos():
            if not nodo_hijo.get_datos() in visitados:
                sol = buscar_solucion_DFS_rec(nodo_hijo, solucion, visitados, limite - 1, conexiones)
                if sol is not None:
                    return sol
        return None

CONEXIONES = {
    'EDO.MEX':{'QRO','SLP','SONORA'},
    'PUEBLA':{'HIDALGO','SLP'},
    'CDMX':{'MICHOACAN'},
    'MICHOACAN':{'SONORA'},
    'SLP':{'QRO','PUEBLA','EDO.MEX','SONORA'},
    'QRO':{'EDO.MEX','SLP'},
    'HIDALGO':{'PUEBLA','SONORA'},
    'MONTERREY':{'HIDALGO','SLP'},
    'SONORA':{'MONTERREY','HIDALGO','SLP','EDO.MEX','MICHOACAN'},
    'GUADALAJARA':{'SLP','HIDALGO'}
}

# if __name__ == "__main__":
#     estado_inicial = 'EDO.MEX'
#     solucion = 'HIDALGO'
#     nodo_inicial = Nodo(estado_inicial)
#     nodo = DFS_prof_iter(nodo_inicial, solucion, CONEXIONES)
#     # Mostrar Resultado
#     if nodo is not None:
#         resultado = []
#         while nodo.get_padre() is not None:
#             resultado.append(nodo.get_datos())
#             nodo = nodo.get_padre()
#         resultado.append(estado_inicial)
#         resultado.reverse()
#         print(resultado)
#     else:
#         print("No se encontró la solución")


@app.route('/DFS_prof_iter', methods=['POST'])
@cross_origin()
def DFS_prof_iter_route():
    body = request.get_json()
    estado_inicial = body['nodo_inicial']
    solucion = body['solucion']
    nodo_inicial = Nodo(estado_inicial)
    nodo = DFS_prof_iter(nodo_inicial, solucion, CONEXIONES)
    # Mostrar Resultado
    if nodo is not None:
        resultado = []
        while nodo.get_padre() is not None:
            resultado.append(nodo.get_datos())
            nodo = nodo.get_padre()
        resultado.append(estado_inicial)
        resultado.reverse()
        return jsonify(resultado)
    else:
        return jsonify("No se encontró la solución")
if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
