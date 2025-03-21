# Puzzle lineal con busqueda en amplitud
from arbol import Nodo

def buscar_solucion_BFS(estado_inicial, solucion):
    solucionado = False
    nodos_visitados = []
    nodo_frontera = []

    nodo_inicial = Nodo(estado_inicial)
    nodo_frontera.append(nodo_inicial)
    while (not solucionado) and len(nodo_frontera) != 0:
        nodo = nodo_frontera.pop(0)
        # Extraer el nodo y añadirlo a visitados
        nodos_visitados.append(nodo)
        if nodo.get_datos() == solucion:
            # Solucion encontrada
            solucionado = True
            return nodo

        # Expandir los nodos hijos
        dato_nodo = nodo.get_datos()

        # Operador izquierdo
        hijo = [dato_nodo[1], dato_nodo[0], dato_nodo[2], dato_nodo[3]]
        hijo_izquierdo = Nodo(hijo)
        hijo_izquierdo.padre = nodo

        if not hijo_izquierdo.en_lista(nodos_visitados) \
            and not hijo_izquierdo.en_lista(nodo_frontera):
            nodo_frontera.append(hijo_izquierdo)

        # Operador medio
        hijo = [dato_nodo[0], dato_nodo[2], dato_nodo[1], dato_nodo[3]]
        hijo_mid = Nodo(hijo)
        hijo_mid.padre = nodo

        if not hijo_mid.en_lista(nodos_visitados) \
            and not hijo_mid.en_lista(nodo_frontera):
            nodo_frontera.append(hijo_mid)

        # Operador derecho
        hijo = [dato_nodo[0], dato_nodo[1], dato_nodo[3], dato_nodo[2]]
        hijo_derecho = Nodo(hijo)
        hijo_derecho.padre = nodo

        if not hijo_derecho.en_lista(nodos_visitados) \
            and not hijo_derecho.en_lista(nodo_frontera):
            nodo_frontera.append(hijo_derecho)

if __name__ == "__main__":
    estado_inicial = [4, 2, 3, 1]
    solucion = [1, 2, 3, 4]
    nodo_solucion = buscar_solucion_BFS(estado_inicial, solucion)

    # Mostrar resultado
    resultado = []
    nodo = nodo_solucion
    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()

    resultado.append(estado_inicial)
    resultado.reverse()
    print(resultado)

    #[[4, 2, 3, 1], [2, 4, 3, 1], [2, 3, 4, 1], [2, 3, 1, 4], [2, 1, 3, 4], [1, 2, 3, 4]]
