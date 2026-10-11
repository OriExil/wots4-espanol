# Documentación técnica

Notas de trabajo de la ingeniería inversa de los formatos de texto del juego. Se publican tal cual por si le sirven
a quien quiera traducir el juego a otro idioma.

- `diagnostico.md`: dónde está el texto y cómo es cada formato (tablas, paquetes de diálogos, guiones `.sx`, fuente).
- `codigos_control.md`: códigos especiales dentro de los textos que hay que conservar.

Mencionan "fases" y algunas herramientas de desarrollo (extracción, validación, composición de glifos) que no están
en este repositorio porque trabajan con los archivos y textos originales del juego. El núcleo que lee y reconstruye
los formatos sí está: `tools/wos4/tablas.py` y `tools/wos4/sx.py`.
