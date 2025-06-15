from operator import itemgetter

def distancia(c1, c2):
    """Distancia de Manhattan entre dos coordenadas"""
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])

def en_ruta(rutas, ciudad):
    """Verifica si una ciudad ya está en alguna ruta"""
    for r in rutas:
        if ciudad in r:
            return r
    return None

def contiene_secuencia_prohibida(ruta, secuencias_prohibidas):
    """Verifica si la ruta contiene alguna secuencia prohibida"""
    for i in range(len(ruta) - 1):
        par = (ruta[i], ruta[i+1])
        if par in secuencias_prohibidas:
            return True
    return False

def peso_ruta(ruta, pedidos):
    """Calcula el peso total de una ruta según los pedidos"""
    return sum(pedidos[ciudad] for ciudad in ruta)

def tiempo_viaje(c1, c2, coord, velocidad_promedio):
    """Tiempo de viaje entre dos ciudades (en horas)"""
    d = distancia(coord[c1], coord[c2])
    return d / velocidad_promedio

def tiempo_viaje_desde_almacen(ciudad, coord, almacen, velocidad_promedio):
    d = distancia(almacen, coord[ciudad])
    return d / velocidad_promedio

def tiempo_viaje_hasta_almacen(ciudad, coord, almacen, velocidad_promedio):
    d = distancia(coord[ciudad], almacen)
    return d / velocidad_promedio

def tiempo_total_ruta(ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen):
    """Calcula el tiempo total estimado de una ruta completa"""
    tiempo_total = 0
    tiempo_total += tiempo_viaje_desde_almacen(ruta[0], coord, almacen, velocidad_promedio)
    for i in range(len(ruta) - 1):
        tiempo_total += tiempo_viaje(ruta[i], ruta[i + 1], coord, velocidad_promedio)
    tiempo_total += tiempo_viaje_hasta_almacen(ruta[-1], coord, almacen, velocidad_promedio)
    for ciudad in ruta:
        tiempo_total += pedidos.get(ciudad, 0) * tiempo_carga_por_unidad
    return tiempo_total

def vrp_voraz(coord, almacen, max_carga, pedidos, tiempo_maximo, velocidad_promedio, tiempo_carga_por_unidad, restricciones=None):
    """Algoritmo voraz para resolver el VRP (Vehicle Routing Problem)"""

    # Aplicar restricciones de ciudades excluidas
    ciudades_excluidas = set()
    if restricciones and "excluir_ciudades" in restricciones:
        ciudades_excluidas = set(restricciones["excluir_ciudades"])

    # Aplicar restricciones de secuencias prohibidas
    secuencias_prohibidas = set()
    if restricciones and "prohibir_secuencias" in restricciones:
        secuencias_prohibidas = set(tuple(seq) for seq in restricciones["prohibir_secuencias"])

    # Filtrar coordenadas y pedidos desde el inicio
    coord = {k: v for k, v in coord.items() if k in pedidos and k not in ciudades_excluidas}
    pedidos = {k: v for k, v in pedidos.items() if k not in ciudades_excluidas}
        
    # Calcular los ahorros
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2 and (c2, c1) not in s:
                d_c1_c2 = distancia(coord[c1], coord[c2])
                d_c1_almacen = distancia(coord[c1], almacen)
                d_c2_almacen = distancia(coord[c2], almacen)
                s[(c1, c2)] = d_c1_almacen + d_c2_almacen - d_c1_c2

    # Ordenar los ahorros de mayor a menor
    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    rutas = []
    for (c1, c2), _ in s:
        ruta_c1 = en_ruta(rutas, c1)
        ruta_c2 = en_ruta(rutas, c2)

        if ruta_c1 is None and ruta_c2 is None:
            nueva_ruta = [c1, c2]
            if peso_ruta(nueva_ruta, pedidos) <= max_carga and not contiene_secuencia_prohibida(nueva_ruta, secuencias_prohibidas):
                if tiempo_total_ruta(nueva_ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen) <= tiempo_maximo:
                    rutas.append(nueva_ruta)
        elif ruta_c1 is not None and ruta_c2 is None:
            if ruta_c1[0] == c1:
                nueva_ruta = [c2] + ruta_c1
            elif ruta_c1[-1] == c1:
                nueva_ruta = ruta_c1 + [c2]
            else:
                continue
            if peso_ruta(nueva_ruta, pedidos) <= max_carga and not contiene_secuencia_prohibida(nueva_ruta, secuencias_prohibidas) and \
               tiempo_total_ruta(nueva_ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen) <= tiempo_maximo:
                rutas[rutas.index(ruta_c1)] = nueva_ruta
        elif ruta_c1 is None and ruta_c2 is not None:
            if ruta_c2[0] == c2:
                nueva_ruta = [c1] + ruta_c2
            elif ruta_c2[-1] == c2:
                nueva_ruta = ruta_c2 + [c1]
            else:
                continue
            if peso_ruta(nueva_ruta, pedidos) <= max_carga and not contiene_secuencia_prohibida(nueva_ruta, secuencias_prohibidas) and \
               tiempo_total_ruta(nueva_ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen) <= tiempo_maximo:
                rutas[rutas.index(ruta_c2)] = nueva_ruta
        elif ruta_c1 != ruta_c2:
            if ruta_c1[-1] == c1 and ruta_c2[0] == c2:
                nueva_ruta = ruta_c1 + ruta_c2
            elif ruta_c2[-1] == c2 and ruta_c1[0] == c1:
                nueva_ruta = ruta_c2 + ruta_c1
            else:
                continue
            if peso_ruta(nueva_ruta, pedidos) <= max_carga and not contiene_secuencia_prohibida(nueva_ruta, secuencias_prohibidas) and \
               tiempo_total_ruta(nueva_ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen) <= tiempo_maximo:
                rutas[rutas.index(ruta_c1)] = nueva_ruta
                rutas.remove(ruta_c2)

    return rutas

if __name__ == "__main__":
    coord = {
        'CDMX': (19.43, -99.13),
        'QRO': (20.59, -100.39),
        'PUE': (19.06, -98.30),
        'MTY': (25.67, -100.28)
    }
    pedidos = {
        'CDMX': 10,
        'QRO': 15,
        'PUE': 8,
        'MTY': 12
    }
    restricciones = {
        # "excluir_ciudades": ["MTY", "PUE"],
        # "prohibir_secuencias": [("QRO", "MTY")]
    }

    almacen = (19.30, -99.65)
    rutas = vrp_voraz(
        coord=coord,
        almacen=almacen,
        max_carga=30,
        pedidos=pedidos,
        tiempo_maximo=8,
        velocidad_promedio=60,
        tiempo_carga_por_unidad=0.1,
        restricciones=restricciones
    )
    for r in rutas:
        print("Ruta:", r)
        print("Carga:", peso_ruta(r, pedidos))
        print()
        print("Tiempo total:", tiempo_total_ruta(r, coord, 60, pedidos, 0.1, almacen), "horas")
        print("Distancia total:", sum(distancia(coord[r[i]], coord[r[i + 1]]) for i in range(len(r) - 1)), "km")
        print("Tiempo de viaje desde el almacén:", tiempo_viaje_desde_almacen(r[0], coord, almacen, 60), "horas")
        print("Tiempo de viaje hasta el almacén:", tiempo_viaje_hasta_almacen(r[-1], coord, almacen, 60), "horas")
        print()
        print("tiempo_carga_total:", sum(pedidos.get(ciudad, 0) * 0.1 for ciudad in r), "horas")
        print("-" * 40)