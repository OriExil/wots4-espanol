# Cómo ayudar

## Reportar un error (lo más útil)
Abre un aviso en la pestaña **Issues** con:
- **Dónde** lo viste: menú, misión, escena, personaje que habla.
- **Qué dice** el texto (copiado o en una captura de pantalla).
- **Qué está mal**: falta de ortografía, frase sin sentido, texto que se sale del cuadro, letra que no se ve,
  trato de tú/usted que no corresponde, etc.

No hace falta saber programar ni usar Git para reportar.

## Corregir una línea tú mismo
1. Busca la frase en la carpeta `traduccion/` (el buscador de GitHub, arriba a la izquierda, busca dentro de los
   archivos).
2. Abre el CSV, pulsa el lápiz (**Edit**) y cambia solo la columna `texto_es`.
3. Pulsa **Commit changes → Propose changes**. GitHub crea por ti una propuesta (*pull request*) para revisarla.

### Reglas al editar
- No cambies la columna `id`.
- Conserva tal cual los códigos especiales: `\n` y `~_` (saltos de línea), `%s` `%d` `%PNAME%` y parecidos, los
  números en círculo `①②③…` (botones), y lo que esté entre `<…>`, `^…^` o `[…]` cuando sea un nombre interno.
- En los textos con varias líneas que son **listas de opciones** (una respuesta por línea), no cambies la cantidad
  de líneas.
- Solo se pueden usar estas letras especiales: `á é í ó ú ü ñ Á É Í Ó Ú Ü Ñ ¿ ¡`. No uses `« » — – º ª` ni otros
  acentos: la fuente del juego no los tiene.
- Mantén las líneas de un largo parecido al de las vecinas (unos 30–36 caracteres en diálogos de vecinos).
- Estilo: español neutro latinoamericano, tuteo (tú/ustedes), sin voseo ni "vosotros". Ver
  `traduccion/guia_estilo.md` y `traduccion/glosario.csv`.

## Probar un cambio en tu juego
Con Python instalado, desde la carpeta del repositorio:
```
python parchear.py instalar
```
(Avisará de que los archivos generados difieren de la versión publicada: es normal si editaste la traducción.)

## Generar el instalador `.exe`
```
python -m pip install pyinstaller
empaquetar.bat
```
El resultado queda en `dist\`.
