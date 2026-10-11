# Way of the Samurai 4 — Parche al español (PC / Steam)

Traducción **no oficial** al español de *Way of the Samurai 4* para PC (versión de Steam), hecha desde el inglés
oficial. Español neutro latinoamericano, con tuteo.

**Estado: versión 1.0 — texto traducido al 100 %** (menús, objetos, técnicas, historia completa, misiones, diálogos
de vecinos y tiendas; unas 59.000 líneas).

> Este parche **no incluye ningún archivo del juego**. Necesitas tu propia copia original de Steam: el instalador
> lee tus archivos, les aplica la traducción y guarda una copia de seguridad de los originales.

## Qué se traduce y qué no

| | |
|---|---|
| Menús, opciones, tutoriales | Sí |
| Objetos, armas, técnicas, logros, perfiles | Sí |
| Historia (subtítulos y opciones de diálogo), finales, créditos | Sí |
| Misiones, encargos, tiendas, charlas de vecinos, dojo | Sí |
| Letras con acento, ñ, ü, ¿ y ¡ en la fuente del juego | Sí (glifos nuevos) |
| Texto dentro de imágenes (manual, mapa, logo del título) | Todavía no |
| Unas 20 frases sueltas guardadas dentro del `.exe` | No |
| Voces y videos | No (siguen en japonés, como en el original) |

## Instalación (fácil)

1. Ve a la sección **Releases** de esta página (columna derecha) y descarga el archivo
   `WotS4-Espanol-vX.Y.Z.zip` de la última versión.
2. Descomprímelo en cualquier carpeta (por ejemplo, el Escritorio).
3. **Cierra el juego** y haz doble clic en `WotS4-Espanol.exe`.
4. Elige `1) Instalar el parche`. El instalador busca el juego en tus bibliotecas de Steam; si no lo encuentra,
   te pide la carpeta (la que contiene `WayOfTheSamurai4.exe`).
5. Abre el juego. En las opciones del juego el idioma debe estar en **English** (el parche reemplaza los textos
   en inglés; la opción aparecerá como "Español").

El proceso tarda alrededor de un minuto.

### Avisos de Windows o del antivirus
El instalador no está firmado digitalmente (firmar cuesta dinero), así que Windows SmartScreen puede mostrar
"Windows protegió su PC": pulsa **Más información → Ejecutar de todas formas**. Algunos antivirus desconfían de los
programas empaquetados con PyInstaller; si prefieres no ejecutar el `.exe`, usa el método alternativo de abajo, que
ejecuta directamente el código fuente que puedes leer en este repositorio.

### Método alternativo (con Python, sin `.exe`)
1. Instala [Python 3.9 o más nuevo](https://www.python.org/downloads/).
2. Descarga este repositorio (**Code → Download ZIP**) y descomprímelo.
3. En esa carpeta, ejecuta:
   ```
   python parchear.py
   ```
No hace falta instalar ninguna biblioteca adicional.

## Desinstalar
Ejecuta otra vez el instalador y elige `2) Desinstalar`. Restaura todos los archivos originales desde la copia de
seguridad (`_backup_parche_es`, dentro de la carpeta del juego) y la borra.

Plan B: en Steam, clic derecho en el juego → **Propiedades → Archivos instalados → Verificar integridad de los
archivos**. Steam vuelve a descargar los originales.

## Preguntas frecuentes

**¿Modifica mis partidas guardadas o el ejecutable?**
No. Solo reemplaza archivos de texto, guiones de escenas y la fuente dentro de la carpeta `US\` del juego.

**Steam actualizó o verificó el juego y volvió a estar en inglés.**
Vuelve a ejecutar el instalador.

**El instalador dice que mis archivos "no coinciden con la versión del juego".**
Tienes otro mod de texto instalado o una versión distinta del juego. Verifica la integridad de los archivos en
Steam y vuelve a intentarlo.

**¿Funciona con la versión de PS3?**
No. Es solo para la versión de PC.

**Encontré un error, una frase rara o un texto que se sale del cuadro.**
¡Gracias! Abre un aviso en la pestaña **Issues** contando dónde lo viste (una captura ayuda mucho). Más detalles en
[CONTRIBUIR.md](CONTRIBUIR.md).

## Cosas a saber de esta versión
- La traducción se hizo con asistencia de inteligencia artificial (Claude) y un proceso de validación automática
  (códigos de control, anchos de línea, glosario). Todavía no fue revisada en pantalla de principio a fin, así que
  puede haber frases que no encajen con la escena, tratamientos de tú/usted inconsistentes en frases cortas, o
  líneas algo largas para su globo. Los reportes son bienvenidos.
- Los extranjeros que en el original hablan un japonés/inglés "roto" hablan aquí un español roto a propósito.
- El texto que en el original aparece entre `< >` (inglés "hablado" dentro de la historia) se deja en inglés.

## Cómo funciona por dentro
- `parchear.py`: instalador/desinstalador.
- `tools/wos4/`: lectura y reconstrucción de los formatos del juego (tablas de texto, paquetes de diálogos y
  guiones `.sx`).
- `traduccion/`: la traducción, un CSV por archivo del juego (`id`, `contexto`, `texto_es`).
- `datos/`: huellas (SHA-256) de los archivos originales y traducidos, y las diferencias de la fuente.
- `docs/`: documentación de los formatos, por si sirve para traducir el juego a otros idiomas.

## Créditos y aviso legal
- Traducción y herramientas: Diego, con asistencia de Claude (Anthropic).
- *Way of the Samurai 4* © ACQUIRE Corp. / Spike Chunsoft; versión de PC publicada por Ghostlight. Todas las marcas
  pertenecen a sus dueños.
- Proyecto de aficionados, gratuito y sin fines de lucro, sin relación con los titulares de los derechos. Si eres
  titular de los derechos y tienes alguna objeción, abre un aviso en **Issues** y se atenderá.
- Código bajo licencia MIT ([LICENSE](LICENSE)). Textos de la traducción bajo
  CC BY-NC-SA 4.0 ([LICENCIA-TRADUCCION.md](LICENCIA-TRADUCCION.md)).
