import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from arbol import Nodo
import matplotlib
import base64
import io
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx


app = Flask(__name__)
CORS(app)

# Ruta para guardar las imágenes generadas
UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def dijkstra(grafo, nodo_inicial, nodo_final):
    nodos = {nodo: Nodo(nodo) for nodo in grafo}

    # Inicializar costos
    for nodo in nodos.values():
        nodo.set_costo(float('inf'))
    nodos[nodo_inicial].set_costo(0)

    nodos_visitados = []
    nodos_no_visitados = list(nodos.values())

    while nodos_no_visitados:
        nodo_actual = min(nodos_no_visitados, key=lambda n: n.get_costo())
        nodos_visitados.append(nodo_actual)
        nodos_no_visitados.remove(nodo_actual)

        if nodo_actual.get_datos() == nodo_final:
            break

        for vecino, peso in grafo[nodo_actual.get_datos()].items():
            if nodos[vecino] in nodos_no_visitados:
                distancia_acumulada = nodo_actual.get_costo() + peso
                if distancia_acumulada < nodos[vecino].get_costo():
                    nodos[vecino].set_costo(distancia_acumulada)
                    nodos[vecino].set_padre(nodo_actual)

    camino = []
    nodo_actual = nodos[nodo_final]
    while nodo_actual is not None:
        camino.append(nodo_actual.get_datos())
        nodo_actual = nodo_actual.get_padre()
    camino.reverse()

    return camino, nodos[nodo_final].get_costo()

def dibujar_grafo(grafo, ruta=None):
    G = nx.Graph()

    for nodo, adyacentes in grafo.items():
        for vecino, peso in adyacentes.items():
            G.add_edge(nodo, vecino, weight=peso)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=700, font_size=10, font_weight='bold')

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if ruta:
        edges = [(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='red', width=2)

    # Guardar la imagen en un buffer de memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.clf()  # Limpiar para evitar superposiciones futuras
    buffer.seek(0)

    # Convertir a base64
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return imagen_base64

@app.route('/dijkstra', methods=['POST'])
def dijkstra_api():
    data = request.get_json()
    grafo = data['grafo']
    nodo_inicial = data['nodo_inicial']
    nodo_final = data['nodo_final']

    try:
        camino, distancia = dijkstra(grafo, nodo_inicial, nodo_final)
        imagenbase64 = dibujar_grafo(grafo, camino)
        image_url = f"data:image/png;base64,{imagenbase64}"

        return jsonify({
            "camino": camino,
            "distancia": distancia,
            "imagen_url": image_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Configuración del puerto
PORT = os.getenv('PORT', 5005)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=True)
