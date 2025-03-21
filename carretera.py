from arbol import Nodo

def buscar_solucion_BFS(conexiones, estado_inicial, solucion):
    solucionado = False
    nodos_visitados = []
    nodos_frontera = []

    nodo_inicial = Nodo(estado_inicial)
    nodos_frontera.append(nodo_inicial)

    while (not solucionado) and len(nodos_frontera) != 0:
        nodo = nodos_frontera.pop(0)
        # Extraer nodo y añadirlo a visitados
        nodos_visitados.append(nodo)
        if nodo.get_datos() == solucion:
            # Solución encontrada
            solucion = True
            return nodo
        # Expandir los nodos hijo
        dato_nodo = nodo.get_datos()
        lista_hijos = []
        for un_hijo in conexiones[dato_nodo]:
            hijo = Nodo(un_hijo)
            lista_hijos.append(hijo)
            if not hijo.en_lista(nodos_visitados)\
                and not hijo.en_lista(nodos_frontera):
                nodos_frontera.append(hijo)


        nodo.set_hijos(lista_hijos)

if __name__ == "__main__":
    conexiones = {
        'CDMX': {'SLP','MEXICALI', 'CHIHUAHUA'},
        'SAPOPAN': {'ZACATECAS', 'MEXICALI'},
        'GUADALAJARA':{'CHIAPAS'},
        'CHIAPAS':{'CHIHUAHUA'},
        'MEXICALI':{'SLP', 'SAPOPAN', 'CDMX', 'CHIHUAHUA', 'SONORA'},
        'SLP':{'CDMX', 'MEXICALI'},
        'ZACATECAS':{'SAPOPAN', 'SONORA', 'CHIHUAHUA'},
        'SONORA':{'ZACATECAS', 'MEXICALI'},
        'MICHOACAN':{'CHIHUAHUA'},
        'CHIHUAHUA':{'MICHOACAN', 'ZACATECAS', 'MEXICALI', 'CDMX','CHIAPAS' }
    }

    estado_inicial = 'CDMX'
    solucion = 'ZACATECAS'
    nodo_solucion = buscar_solucion_BFS(conexiones, estado_inicial, solucion)
    # Mostrar Resultado
    resultado = []
    nodo = nodo_solucion
    while nodo.get_padre() is not None:
        resultado.append(nodo.get_datos())
        nodo = nodo.get_padre()

    resultado.append(estado_inicial)
    resultado.reverse()
    print(resultado)
