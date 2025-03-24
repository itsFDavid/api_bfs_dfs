# from flask import Flask, request, jsonify
# from flask_cors import CORS
from arbol import Nodo

# app = Flask(__name__)
# CORS(app)


def buscar_solucion_DFS_rec(nodo_inicial, solucion, visitados):
    visitados.append(nodo_inicial.get_datos())

    if nodo_inicial.get_datos() == solucion:
        return nodo_inicial

    # Expandir nodos sucesores (hijos)
    datos_nodo = nodo_inicial.get_datos()
    hijo = [datos_nodo[1], datos_nodo[0], datos_nodo[2], datos_nodo[3]]
    hijo_izquierdo = Nodo(hijo)
    hijo = [datos_nodo[0], datos_nodo[2], datos_nodo[1], datos_nodo[3]]
    hijo_central = Nodo(hijo)
    hijo = [datos_nodo[0], datos_nodo[1], datos_nodo[3], datos_nodo[2]]
    hijo_derecho = Nodo(hijo)
    nodo_inicial.set_hijos([hijo_izquierdo, hijo_central, hijo_derecho])

    for nodo_hijo in nodo_inicial.get_hijos():
        if not nodo_hijo.get_datos() in visitados:
            # Llamada recursiva
            sol = buscar_solucion_DFS_rec(nodo_hijo, solucion, visitados)
            if sol is not None:
                return sol
    return None

if __name__ == "__main__":
    estado_inicial = [4, 2, 3, 1]
    solucion = [1, 2, 3, 4]
    visitados = []
    nodo_inicial = Nodo(estado_inicial)
    nodo = buscar_solucion_DFS_rec(nodo_inicial, solucion, visitados)
    # Mostrar resultado
    resultado = []
    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()
    resultado.append(estado_inicial)
    resultado.reverse()
    print(resultado)

# [[4, 2, 3, 1], [2, 4, 3, 1], [2, 3, 4, 1], [3, 2, 4, 1], [3, 4, 2, 1], [4, 3, 2, 1], [4, 3, 1, 2],
# [3, 4, 1, 2], [3, 1, 4, 2], [1, 3, 4, 2], [1, 4, 3, 2], [4, 1, 3, 2], [4, 1, 2, 3], [1, 4, 2, 3],
# [1, 2, 4, 3], [2, 1, 4, 3], [2, 1, 3, 4], [1, 2, 3, 4]]


# @app.route('/DFS_rec', methods=['POST'])
# def dfs_rec():
#     body = request.get_json()
#     estado_inicial = body['nodo_inicial']
#     solucion = body['solucion']

#     visitados = []
#     nodo_inicial = Nodo(estado_inicial)
#     nodo = buscar_solucion_DFS_rec(nodo_inicial, solucion, visitados)

#     resultado = []
#     while nodo.get_padre() is not None:
#         resultado.append(nodo.get_datos())
#         nodo = nodo.get_padre()
#     resultado.append(estado_inicial)
#     resultado.reverse()
#     return str(resultado)

# if __name__ == "__main__":
#     app.run()
