# VRP - Vehicle Routing Problem
import math
from operator import itemgetter

def distancia(cordenada1, cordenada2):
    """
      Distancia
    """
    lat1 = cordenada1[0]
    lon1 = cordenada1[1]
    lat2 = cordenada2[0]
    lon2 = cordenada2[1]

    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


def en_ruta(rutas, ciudades):
    """
      En ruta
    """
    ruta = None
    for r in rutas:
        if ciudades in r:
            ruta = r
    return ruta


def peso_ruta(ruta, pedidos):
    """
      Peso ruta
    """
    total = 0
    for c in ruta:
        total += pedidos[c]
    return total

def tiempo_viaje(c1, c2, coord, velocidad_promedio):
    """Tiempo de viaje entre dos ciudades (en horas)"""
    d = distancia(coord[c1], coord[c2])
    return d / velocidad_promedio

def tiempo_total_ruta(ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad):
    """Calcula el tiempo total estimado de la ruta"""
    tiempo_total = 0
    # del almacén al primer cliente
    tiempo_total += tiempo_viaje_desde_almacen(ruta[0], coord, velocidad_promedio)
    for i in range(len(ruta) - 1):
        tiempo_total += tiempo_viaje(ruta[i], ruta[i+1], coord, velocidad_promedio)
    # regresamos al almacén
    tiempo_total += tiempo_viaje_hasta_almacen(ruta[-1], coord, velocidad_promedio)
    # tiempo de carga/descarga
    for ciudad in ruta:
        tiempo_total += pedidos[ciudad] * tiempo_carga_por_unidad
    return tiempo_total

def tiempo_viaje_desde_almacen(ciudad, coord, velocidad_promedio):
    d = distancia(almacen, coord[ciudad])
    return d / velocidad_promedio

def tiempo_viaje_hasta_almacen(ciudad, coord, velocidad_promedio):
    d = distancia(coord[ciudad], almacen)
    return d / velocidad_promedio


def vrp_voraz(coord, almacen, max_carga, pedidos, tiempo_maximo, velocidad_promedio, tiempo_carga_por_unidad):
    """
      VRP Voraz
    """
    # Calcular los ahorros
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2:
                if (c2, c1) not in s:
                    d_c1_c2 = distancia(coord[c1], coord[c2])
                    d_c1_almacen = distancia(coord[c1], almacen)
                    d_c2_almacen = distancia(coord[c2], almacen)
                    s[c1, c2] = d_c1_almacen + d_c2_almacen - d_c1_c2
    # Ordenar los ahorros
    s = sorted(s.items(), key = itemgetter(1), reverse=True)
    # Construir las rutas
    rutas = []
    for k,v in s:
        ruta_c1 = en_ruta(rutas, k[0])
        ruta_c2 = en_ruta(rutas, k[1])
        if ruta_c1 == None and ruta_c2 == None:
            # No estan en ninguna ruta, la creamos
            if peso_ruta([k[0], k[1]], pedidos) <= max_carga:
                rutas.append([k[0], k[1]])
        elif ruta_c1 != None and ruta_c2 == None:
            # cliente 1 ya cuenta con una ruta, agregamos el cliente 2
            if ruta_c1[0] == k[0]:
                if peso_ruta(ruta_c1, pedidos) + peso_ruta([k[1]], pedidos) <= max_carga:
                    # rutas[rutas.index(ruta_c1)].append(k[1])
                    rutas[rutas.index(ruta_c1)].insert(0, k[1])
            elif ruta_c1[len(ruta_c1) - 1] == k[0]:
                if peso_ruta(ruta_c1, pedidos) + peso_ruta([k[1]], pedidos) <= max_carga:
                    rutas[rutas.index(ruta_c1)].append(k[1])
        elif ruta_c1 == None and ruta_c2 != None:
            # cliente 2 ya cuenta con una ruta, agregamos el cliente 1
            if ruta_c2[0] == k[1]:
                if peso_ruta(ruta_c2, pedidos) + peso_ruta([k[0]], pedidos) <= max_carga:
                    rutas[rutas.index(ruta_c2)].insert(0, k[0])
            elif ruta_c2[len(ruta_c2) - 1] == k[1]:
                if peso_ruta(ruta_c2, pedidos) + peso_ruta([k[0]], pedidos) <= max_carga:
                    rutas[rutas.index(ruta_c2)].append(k[0])
        elif ruta_c1 != None and ruta_c2 != None and ruta_c1 != ruta_c2:
            # cliente 1 y 2 ya cuentan con rutas, tratamos de unir las rutas
            if ruta_c1[0] == k[0] and ruta_c2[len(ruta_c2) - 1] == k[1]:
                # if peso_ruta(ruta_c1, pedidos) + peso_ruta(ruta_c2, pedidos) <= max_carga:
                #     rutas[rutas.index(ruta_c2)].extend(ruta_c1)
                #     rutas.remove(ruta_c1)
                nueva_ruta = ruta_c1 + ruta_c2
                if tiempo_total_ruta(nueva_ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad) <= tiempo_maximo:
                    rutas[rutas.index(ruta_c1)] = nueva_ruta
                    rutas.remove(ruta_c2)
            elif ruta_c1[len(ruta_c1) - 1] == k[0] and ruta_c2[0] == k[1]:
                if peso_ruta(ruta_c1, pedidos) + peso_ruta(ruta_c2, pedidos) <= max_carga:
                    rutas[rutas.index(ruta_c1)].extend(ruta_c2)
                    rutas.remove(ruta_c2)
    return rutas


if __name__ == "__main__":
    coord = {
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
    pedidos = {
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

    almacen = [19.29370432359307, -99.65371080401178]
    max_carga = 40
    tiempo_maximo = 8 # jornada laboral de 8 horas
    velocidad_promedio = 60  # km/h
    tiempo_carga_por_unidad = 0.15  # 3 minutos por unidad
    # (min*horas/60 minutos = tiempo carga por unidad)
    rutas = []
    rutas = vrp_voraz(
        coord,
        almacen,
        max_carga,
        pedidos,
        tiempo_maximo,
        velocidad_promedio,
        tiempo_carga_por_unidad)

    print("Almacen: ", almacen)
    print("Max carga: ", max_carga)
    print("Tiempo maximo: ", tiempo_maximo, "hrs")
    print("Velocidad promedio: ", velocidad_promedio, "km/h")
    print("Tiempo carga por unidad: ", tiempo_carga_por_unidad, "hrs")
    # print("Rutas: ", rutas)
    print('\n\n')
    # total de carga por ruta
    for r in rutas:
        print("Ruta: ", r)
        print("Carga: ", peso_ruta(r, pedidos))
        print("Tiempo estimado: ", round(
            tiempo_total_ruta(r, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad), 2),
            "hrs\n")

# Convertir e una dimension escalar
# 2 restricciones mas
# 1.- Tiempo de entrega
# 2.- Tiempo de carga y descarga
# 3.- Tiempo de espera
# 4.- Tiempo de viaje

# API y frontend
