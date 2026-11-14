# Metrorrey

Para abrir la web, ejecuta `main.py`. Se abrirá una pestaña en el navegador. Para cerrar el servidor, pulsa `Ctrl+C` en la terminal.

## Cómo calcula la ruta

A* elige cada paso con `f = g + h`. `g` suma las distancias por las vías y los costes de transbordo (coste real). `h` estima lo que falta con las distancias en línea recta del Excel y orienta la búsqueda; el coste final se calcula con `g`.

## Dependencias

Flask, NetworkX, pandas y openpyxl.
