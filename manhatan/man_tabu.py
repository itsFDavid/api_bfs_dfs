import random
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from time import time
from copy import deepcopy

class TSPSolver:
    def __init__(self, coord):
        self.coord = coord
        self.ciudades = list(coord.keys())
        self.n = len(self.ciudades)
        self.dist_matrix = self._precompute_distances()

    def _precompute_distances(self):
        """Precalcula la matriz de distancias para mayor eficiencia"""
        matrix = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i+1, self.n):
                dist = abs(self.coord[self.ciudades[i]][0] - self.coord[self.ciudades[j]][0]) + \
                       abs(self.coord[self.ciudades[i]][1] - self.coord[self.ciudades[j]][1])
                matrix[i][j] = dist
                matrix[j][i] = dist
        return matrix

    def distancia_ruta(self, ruta_indices):
        """Calcula la distancia total de una ruta usando la matriz precalculada"""
        total = 0
        for i in range(self.n-1):
            total += self.dist_matrix[ruta_indices[i]][ruta_indices[i+1]]
        total += self.dist_matrix[ruta_indices[-1]][ruta_indices[0]]  # Cierre del ciclo
        return total

    def generar_solucion_inicial(self):
        """Genera una solución inicial usando el algoritmo del vecino más cercano"""
        start = random.randint(0, self.n-1)
        ruta = [start]
        no_visitados = set(range(self.n)) - {start}

        while no_visitados:
            ultimo = ruta[-1]
            proximo = min(no_visitados, key=lambda x: self.dist_matrix[ultimo][x])
            ruta.append(proximo)
            no_visitados.remove(proximo)

        return ruta

    def generar_vecinos_2opt(self, ruta):
        """Genera vecinos usando el operador 2-opt (intercambio de aristas)"""
        vecinos = []
        for i in range(1, self.n-1):
            for j in range(i+1, self.n):
                if j-i == 1: continue  # No considerar swaps consecutivos
                vecino = ruta[:i] + ruta[i:j+1][::-1] + ruta[j+1:]
                vecinos.append((vecino, (i, j)))
        return vecinos

    def generar_vecinos_3opt(self, ruta):
        """Genera vecinos usando el operador 3-opt (más complejo que 2-opt)"""
        vecinos = []
        for i in range(1, self.n-3):
            for j in range(i+1, self.n-2):
                for k in range(j+1, self.n-1):
                    # Variante 1: intercambio simple
                    vecino1 = ruta[:i] + ruta[i:j][::-1] + ruta[j:k][::-1] + ruta[k:]
                    vecinos.append((vecino1, (i,j,k,1)))

                    # Variante 2: reorganización más compleja
                    vecino2 = ruta[:i] + ruta[j:k] + ruta[i:j] + ruta[k:]
                    vecinos.append((vecino2, (i,j,k,2)))
        return vecinos

    def busqueda_tabu_mejorada(self, iteraciones=500, tamaño_tabu=20, max_sin_mejora=50):
        """Algoritmo de búsqueda tabú mejorado con múltiples optimizaciones"""
        # Solución inicial mejorada
        mejor_ruta = self.generar_solucion_inicial()
        mejor_costo = self.distancia_ruta(mejor_ruta)

        actual_ruta = mejor_ruta.copy()
        actual_costo = mejor_costo

        lista_tabu = deque(maxlen=tamaño_tabu)
        historial_costos = [actual_costo]
        iter_sin_mejora = 0

        # Parámetros para estrategia de aspiración
        mejor_global_costo = float('inf')
        mejor_global_ruta = None

        for it in range(iteraciones):
            # Alternar entre operadores 2-opt y 3-opt
            if it % 3 == 0:  # Cada 3 iteraciones usa 3-opt
                vecinos = self.generar_vecinos_3opt(actual_ruta)
            else:
                vecinos = self.generar_vecinos_2opt(actual_ruta)

            # Ordenar vecinos por calidad
            vecinos.sort(key=lambda x: self.distancia_ruta(x[0]))

            encontrado = False
            for vecino, movimiento in vecinos:
                costo_vecino = self.distancia_ruta(vecino)

                # Criterio de aspiración
                if costo_vecino < mejor_global_costo:
                    mejor_global_costo = costo_vecino
                    mejor_global_ruta = vecino.copy()
                    actual_ruta = vecino.copy()
                    actual_costo = costo_vecino
                    encontrado = True
                    break

                # Movimiento no tabú
                if movimiento not in lista_tabu:
                    actual_ruta = vecino.copy()
                    actual_costo = costo_vecino
                    lista_tabu.append(movimiento)
                    encontrado = True
                    break

            # Si no se encontró movimiento válido, reiniciar lista tabú
            if not encontrado:
                lista_tabu.clear()
                actual_ruta = random.sample(actual_ruta, len(actual_ruta))
                actual_costo = self.distancia_ruta(actual_ruta)

            # Actualizar mejor solución
            if actual_costo < mejor_costo:
                mejor_ruta = actual_ruta.copy()
                mejor_costo = actual_costo
                iter_sin_mejora = 0
            else:
                iter_sin_mejora += 1

            # Reinicio estratégico
            if iter_sin_mejora > max_sin_mejora:
                actual_ruta = self.generar_solucion_inicial()
                actual_costo = self.distancia_ruta(actual_ruta)
                lista_tabu.clear()
                iter_sin_mejora = 0

            historial_costos.append(actual_costo)

        # Asegurar que devolvemos la mejor solución global encontrada
        if mejor_global_costo < mejor_costo:
            return mejor_global_ruta, mejor_global_costo, historial_costos
        return mejor_ruta, mejor_costo, historial_costos

    def visualizar_ruta(self, ruta_indices, titulo=""):
        """Visualiza la ruta óptima"""
        ruta_ciudades = [self.ciudades[i] for i in ruta_indices]
        x = [self.coord[ciudad][0] for ciudad in ruta_ciudades]
        y = [self.coord[ciudad][1] for ciudad in ruta_ciudades]
        x.append(x[0])  # Cerrar el ciclo
        y.append(y[0])

        plt.figure(figsize=(12, 6))
        plt.plot(x, y, 'o-', markersize=8, linewidth=2)
        for i, ciudad in enumerate(ruta_ciudades):
            plt.text(x[i], y[i], ciudad, fontsize=9, ha='right')

        distancia = self.distancia_ruta(ruta_indices)
        plt.title(f"{titulo}\nDistancia Manhattan Total: {distancia:.2f}")
        plt.xlabel("Coordenada X")
        plt.ylabel("Coordenada Y")
        plt.grid(alpha=0.3)
        plt.show()

if __name__ == "__main__":
    coord = {
        'Jiloyork': (19.916012, -99.580580),
        'Toluca': (19.289165, -99.655697),
        'Atlacomulco': (19.799520, -99.873844),
        'Guadalajara': (20.677754472859146, -103.34625354877137),
        'Monterrey': (25.69161110159454, -100.321838480256),
        'QuintanaRoo': (21.163111924844458, -86.80231502121464),
        'Michohacan': (19.701400113725654, -101.20829680213464),
        'Aguascalientes': (21.87641043660486, -102.26438663286967),
        'CDMX': (19.432713075976878, -99.13318344772986),
        'QRO': (20.59719437542255, -100.38667040246602)
    }

    # Crear solver y ejecutar
    solver = TSPSolver(coord)

    print("Ejecutando búsqueda tabú mejorada...")
    start_time = time()
    mejor_ruta, mejor_costo, historial = solver.busqueda_tabu_mejorada(
        iteraciones=1000,
        tamaño_tabu=25,
        max_sin_mejora=100
    )
    end_time = time()

    # Resultados
    print("\nResultados:")
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
    print(f"Mejor distancia encontrada: {mejor_costo:.2f}")
    print("Ruta óptima:")
    print(" -> ".join([solver.ciudades[i] for i in mejor_ruta]))

    # Visualización
    solver.visualizar_ruta(mejor_ruta, "Mejor Ruta Encontrada")

    # Gráfico de convergencia
    plt.figure(figsize=(12, 4))
    plt.plot(historial)
    plt.title("Convergencia del Algoritmo")
    plt.xlabel("Iteración")
    plt.ylabel("Distancia de Ruta")
    plt.grid(alpha=0.3)
    plt.show()
