import os
from flask_cors import CORSfrom flask import Flask, request, jsonify

from arbol import Nodo
from DFS_rec import buscar_solucion_DFS_rec
from puzzle_lineal import buscar_solucion_BFS
from puzzle_lineal_LIFO import buscar_solucion_DFS

app = Flask(__name__)
CORS(app)

@app.route('/DFS_rec', methods=['POST'])
def DFS_rec():
    body = request.get_json()
    estado_inicial = body['nodo_inicial']
    solucion = body['solucion']


    visitados = []
    nodo_inicial = Nodo(estado_inicial)
    nodo = buscar_solucion_DFS_rec(nodo_inicial, solucion, visitados)
    resultado = []
    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()
    resultado.append(estado_inicial)
    resultado.reverse()
    return jsonify(resultado)

@app.route('/BFS', methods=['POST'])
def BFS():
    body = request.get_json()
    estado_inicial = body['nodo_inicial']
    solucion = body['solucion']

    nodo_solucion = buscar_solucion_BFS(estado_inicial, solucion)

    resultado = []
    nodo = nodo_solucion
    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()

    resultado.append(estado_inicial)
    resultado.reverse()
    return jsonify(resultado)

@app.route('/DFS', methods=['POST'])
def DFS():
    body = request.get_json()
    estado_inicial = body['nodo_inicial']
    solucion = body['solucion']

    nodo_solucion = buscar_solucion_DFS(estado_inicial, solucion)

    resultado = []
    nodo = nodo_solucion
    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()

    resultado.append(estado_inicial)
    resultado.reverse()
    return jsonify(resultado)

# get port of .env
PORT= os.getenv('PORT')
if PORT is None:
    PORT = 6000

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0")
