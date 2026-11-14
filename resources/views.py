from flask import Blueprint, current_app, render_template, request

import grafo as g
from . import graph


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def index():
    path = None
    route_nodes = []
    route_lines = []
    time = None
    transfers = 0
    origin = ""
    destination = ""
    error = None
    stations = g.estaciones_publicas()

    if request.method == "POST":
        origin = request.form.get("origin", "").strip()
        destination = request.form.get("destination", "").strip()

        if not origin or not destination:
            error = "Selecciona origen y destino."
        else:
            try:
                route_nodes, weight = g.obtener_ruta(graph, origin, destination)
                path = g.limpiar_estaciones(route_nodes)
                path = [station for i, station in enumerate(path)
                        if i == 0 or station != path[i - 1]]
                transfers = g.calcular_transbordos(route_nodes)
                route_lines = [
                    g.linea(first) if g.linea(first) == g.linea(second)
                    else "transfer"
                    for first, second in zip(route_nodes, route_nodes[1:])
                ]

                # El peso equivale a metros; a 6 m/s se convierte a minutos.
                time = round(weight / 360)
            except ValueError as exc:
                error = str(exc)
            except Exception:
                current_app.logger.exception("Error calculando la ruta")
                error = "Ha ocurrido un error al calcular la ruta."

    return render_template(
        "index.html",
        stations=stations,
        path=path,
        route_nodes=route_nodes,
        route_lines=route_lines,
        time=time,
        transfers=transfers,
        origin=origin,
        destination=destination,
        error=error,
    )
