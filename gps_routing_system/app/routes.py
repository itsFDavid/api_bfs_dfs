from flask import Blueprint, request, jsonify
from app.models import tabu, simulated_annealing, hill_climbing, vrp_voraz, peso_ruta, tiempo_total_ruta, tabu_search_ors

bp = Blueprint('api', __name__)

# Ruta ya creada para tabu (ejemplo)
@bp.route('/api/tabu', methods=['POST'])
def resolver_tabu():
    data = request.get_json(force=True)
    coord = data.get('coord', {})
    iteraciones = data.get('iteraciones', 100)
    tamaño_tabu = data.get('tamaño_tabu', 10)
    restricciones = data.get('restricciones', None)

    if not coord:
        return jsonify({"error": "No se enviaron coordenadas"}), 400

    try:
        resultado = tabu.tabu_search(coord, iteraciones, tamaño_tabu, restricciones)
        return jsonify(resultado)

    except ValueError as ve:
        print(f"Error de validación: {ve}")
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500


# Nueva ruta para simulated annealing
@bp.route('/api/simulated-annealing', methods=['POST'])
def resolver_simulated_annealing():
    data = request.get_json(force=True)
    coord = data.get('coord', {})
    iteraciones = data.get('iteraciones', 1000)
    temperatura_inicial = data.get('temperatura_inicial', 100)
    enfriamiento = data.get('enfriamiento', 0.95)
    restricciones = data.get('restricciones', None)

    if not coord:
        return jsonify({"error": "No se enviaron coordenadas"}), 400

    try:
        ruta, distancia_total = simulated_annealing(
            coord,
            iteraciones=iteraciones,
            temp_inicial=temperatura_inicial,
            enfriamiento=enfriamiento,
            restricciones=restricciones
        )
        return jsonify({"ruta": ruta, "distancia": distancia_total})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/hill-climbing', methods=['POST'])
def resolver_hill_climbing():
    data = request.get_json(force=True)
    coord = data.get('coord', {})
    restricciones = data.get('restricciones', None)

    if not coord:
        return jsonify({"error": "No se enviaron coordenadas"}), 400

    try:
        ruta, distancia_total = hill_climbing(coord, restricciones)
        return jsonify({"ruta": ruta, "distancia": distancia_total})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @bp.route('/api/vrp-voraz', methods=['POST'])
# def resolver_vrp_voraz():
    data = request.get_json(force=True)

    coord = data.get('coord', {})
    pedidos = data.get('pedidos', {})
    almacen = tuple(data.get('almacen', ()))
    max_carga = data.get('max_carga', 30)
    tiempo_maximo = data.get('tiempo_maximo', 8)
    velocidad_promedio = data.get('velocidad_promedio', 60)
    tiempo_carga_por_unidad = data.get('tiempo_carga_por_unidad', 0.1)
    restricciones = data.get('restricciones', {})

    if not coord or not pedidos or not almacen:
        return jsonify({"error": "Faltan datos esenciales (coord, pedidos o almacen)"}), 400

    try:
        rutas = vrp_voraz(
            coord=coord,
            almacen=almacen,
            max_carga=max_carga,
            pedidos=pedidos,
            tiempo_maximo=tiempo_maximo,
            velocidad_promedio=velocidad_promedio,
            tiempo_carga_por_unidad=tiempo_carga_por_unidad,
            restricciones=restricciones
        )

        # Información adicional por ruta
        resultados = []
        for ruta in rutas:
            resultados.append({
                "ruta": ruta,
                "carga": peso_ruta(ruta, pedidos),
                "tiempo_total": tiempo_total_ruta(ruta, coord, velocidad_promedio, pedidos, tiempo_carga_por_unidad, almacen),
                "tiempo_carga_total": sum(pedidos[ciudad] * tiempo_carga_por_unidad for ciudad in ruta)
            })

        return jsonify({"rutas": resultados})
    except Exception as e:
        return jsonify({"error": str(e)}), 500