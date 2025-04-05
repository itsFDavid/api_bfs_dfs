from arbol import Nodo
import matplotlib.pyplot as plt
import networkx as nx



def dijkstra(grafo, nodo_inicial, nodo_final):
    # Use Nodo class to represent the graph
    nodos = {nodo: Nodo(nodo) for nodo in grafo}

    # Inicializar costos
    for nodo in nodos.values():
        nodo.set_costo(float('inf'))  # Inicializar todos los costos como infinito
        # print('nodo', nodo.get_costo())
    nodos[nodo_inicial].set_costo(0)  # El nodo inicial tiene costo 0

    nodos_visitados = []
    nodos_no_visitados = list(nodos.values())

    # Mientras haya nodos no visitados
    while nodos_no_visitados:
        # Seleccionar el nodo no visitado con menor distancia acumulada
        nodo_actual = min(nodos_no_visitados, key=lambda n: n.get_costo())
        nodos_visitados.append(nodo_actual)
        nodos_no_visitados.remove(nodo_actual)
        # print('nodo actual inicio: ', nodo_actual.get_datos())
        # for n in nodos_no_visitados:
        #     print('nodo no visitado', n.get_datos(), 'costo', n.get_costo())
        # for n in nodos_visitados:
        #     print('nodo visitado', n.get_datos(), 'costo', n.get_costo())

        # Si hemos llegado al nodo final, salir del bucle
        if nodo_actual.get_datos() == nodo_final:
            break

        # Actualizar la distancia acumulada de los nodos adyacentes
        for vecino, peso in grafo[nodo_actual.get_datos()].items():
            if nodos[vecino] in nodos_no_visitados:
                distancia_acumulada = nodo_actual.get_costo() + peso
                # print('nodo actual: ', nodo_actual.get_datos())
                # print('nodo vecino', nodos[vecino].get_datos())
                # print(distancia_acumulada, nodos[vecino].get_costo())
                # print(distancia_acumulada < nodos[vecino].get_costo())
                if distancia_acumulada < nodos[vecino].get_costo():
                    nodos[vecino].set_costo(distancia_acumulada)
                    nodos[vecino].set_padre(nodo_actual)

    # Reconstruir el camino desde el nodo final al nodo inicial
    camino = []
    nodo_actual = nodos[nodo_final]
    while nodo_actual is not None:
        camino.append(nodo_actual.get_datos())
        nodo_actual = nodo_actual.get_padre()
    camino.reverse()

    # Retornar el camino y la distancia acumulada al nodo final
    return camino, nodos[nodo_final].get_costo()

# Representar todo el grafo con matplotlib y la ruta correcta
def dibujar_grafo(grafo, ruta=None):
    G = nx.Graph()

    # Añadir nodos y aristas al grafo
    for nodo, adyacentes in grafo.items():
        for vecino, peso in adyacentes.items():
            G.add_edge(nodo, vecino, weight=peso)

    # Dibujar el grafo
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=700, font_size=10, font_weight='bold')

    # Dibujar las aristas con sus pesos
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Resaltar la ruta si se proporciona
    if ruta:
        edges = [(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='red', width=2)

    # guardar grafica
    plt.savefig('grafo.png')


if __name__ == "__main__":
    nodo_inicial = "nodo1"
    nodo_final = "nodo6"
    grafo = {
        "nodo1": {"nodo2": 3, "nodo3": 6},
        "nodo2": {"nodo1": 3, "nodo3": 2, "nodo4": 1},
        "nodo3": {"nodo1": 6, "nodo2": 2, "nodo4": 4, "nodo5": 2},
        "nodo4": {"nodo2": 1, "nodo3": 4, "nodo5": 6},
        "nodo5": {"nodo3": 2, "nodo4": 6, "nodo6": 2, "nodo7": 2},
        "nodo6": {"nodo5": 2, "nodo7": 3},
        "nodo7": {"nodo5": 2, "nodo6": 3}
    }
    camino, distancia = dijkstra(grafo, nodo_inicial, nodo_final)
    print(f"Camino: {camino}")
    print(f"Distancia: {distancia}")
    dibujar_grafo(grafo, camino)
