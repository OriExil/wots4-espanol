# Diagnóstico técnico (Fase 1)

Convención: **[V]** hecho verificado · **[H]** hipótesis · **[S]** suposición.

## 1. Resumen
- Motor: Gamebryo 20.3.0.9 (port de PC de Ghostlight). El juego elige la carpeta de idioma `US/` o `JP/`
  (opción "Language: English / 日本語" del menú). **El parche reemplaza archivos de `US/`.** [V: rutas `$/GameText/...`
  y `US/Script` en el ejecutable]
- No existen herramientas públicas ni traducciones previas para la versión de PC (búsqueda web 2026-10-11). [V]
- Todo el texto está en UTF-16LE. No hay compresión ni cifrado. [V]
- Volumen: ~21.500 cadenas únicas, ~820.000 caracteres, ~146.000 palabras.

## 2. Dónde está el texto

| Contenedor | Contenido | Formato | Cadenas (únicas) | Viabilidad |
|---|---|---|---:|---|
| `US/GameText/GameText{Main,UI,Item,Weapon,Skill,...}.l` (16 tablas) | menús, objetos, armas, técnicas, misiones, tutoriales, logros, perfiles | tabla A | 6.846 (4.654) | **fácil** |
| `US/GameText/NPCNameText.l` | nombres de PNJ (con género) | tabla N (9 secciones) | 577 | **fácil** (casi todo se mantiene) |
| `US/ActionScript/Script/AsScriptTextPack.l` | diálogos de PNJ, charlas, eventos libres | pack P de 154 tablas B | 9.418 (7.548) | **fácil** |
| `US/ActionScript/UserCommand/AsUserCmdTextPack.l` | misiones/encargos, tiendas, comandos | pack P de 73 tablas B | 2.747 (2.611) | **fácil** |
| `US/Script/**/*.sx` (849 archivos) | subtítulos de la historia, opciones de diálogo | bytecode "TH00" | ~50.500 (~5.300 visibles) | **medio** (resuelto: ver §4) |
| `US/Font/FontDatabase.l` + `FontTexture.nif` | fuente bitmap | tabla de glifos + DXT3 | — | **medio** (ver §5) |
| `US/UI/**.nif` distintos de `JP/` (Manual×5, Map×34, Texture×3, Icon×1, Layout×1) | texto dibujado en imágenes | NIF con texturas | — | **difícil** (Fase 7) |
| `WayOfTheSamurai4.exe` | ~20 cadenas sueltas ("Nameless Samurai", "Press any key", ":Accept", ":Cancel"...) | UTF-16 en el .exe | ~20 | **difícil / opcional** (no se toca el .exe por ahora) |
| `US/Video/*.wmv` | intro y logos | vídeo | — | no se traduce |

Archivos que **no** usa el juego de PC [V: no aparecen en el ejecutable]: `GameTextPack.l` (pack de PS3),
`BACKUP-GameText*.l` (versiones de PS3; las actuales agregan las opciones de PC), `GameText.l` (depuración, en japonés),
`newstring`, y los `*Text.l` sueltos de `ActionScript/` (el ejecutable solo carga los dos packs).
`AccessoryText.l`, `ItemName.l` y `MenuList*.l` son idénticos a los de `JP/` (datos internos/depuración).

## 3. Formatos de tabla (todos con ida y vuelta byte a byte) [V]
- **A** (`GameText*.l`): `u32 n`, `u32 8`, `n × u32 offset` (relativo a 0x8), cadenas terminadas en `00 00`.
  El orden físico de las cadenas no coincide con el índice; se conserva el orden original.
- **B** (tabla de ActionScript): `u32 n`, `n × (u32 id, u32 offset absoluto)`, cadenas. Dentro de los packs va rellena a 4.
- **P** (pack): `u32 n`, `n × (u32 id, u32 offset)`, luego `n` tablas B.
- **N** (`NPCNameText.l`): `9 × u32` offsets de sección; sección = `u32 n`, `n × (u16 id, u16 género, u32 offset rel.)`,
  cadenas, `00 00` extra y relleno a 4.

Implementación: `tools/wos4/tablas.py`.

## 4. Scripts `.sx` [V]
Cabecera de 20 bytes (`"TH00"`, 0, longitud de código, longitud alineada a 4, 0) y bytecode de pila:

| Opcode | Operando | Significado |
|---|---|---|
| `0x22` | `u16 n` + `n` caracteres UTF-16 | cadena (texto visible o identificador) |
| `0x21`, `0x25` | `i32` | entero / cantidad de argumentos |
| `0x24` | `f32` | flotante |
| `0x23` | `u32` | longitud del bloque que sigue (hay que recalcularla) |
| `0x38`, `0x39`, `0x50` | `i16` | nombre ASCII; si es negativo es una **referencia relativa** a un literal anterior (hay que recalcularla) |
| `0x33` | `i16` | 0..3 |
| otros (`0x00 0x20 0x30 0x31 0x32 0x34 0x35 0x36 0x37 0x51 0x52 0x54`) | — | sin operando |

- Los 1.595 `.sx` del juego se desensamblan y reensamblan idénticos. [V]
- Reubicación validada: tomando el `.sx` de `JP/` y poniéndole las cadenas de `US/`, el resultado es **idéntico al
  archivo de `US/`** en los 334 pares comparables (los otros 195 tienen diferencias reales de código). [V]
- El compilador original apunta siempre al último literal igual y repite el literal cuando la distancia pasaría de
  ~-32512; el ensamblador hace lo mismo (límite -0x7F00). [V la regla observada; H que el límite exacto sea ese]
- Las cadenas visibles son los argumentos de `SetTelopTable` (subtítulos), `AddTalkInputChara` y `SetTalkSelect`
  (opciones), `SetSelif` y `SetBalloonTable`. El resto de las cadenas son rutas e identificadores y **no se tocan**.
  [V por inspección de contenidos; H que no haya otra función con texto visible]
- [H] Ningún otro archivo guarda offsets hacia dentro de los `.sx` (las escenas se buscan por nombre). Se confirma con
  la prueba en el juego de la Fase 3.

Implementación: `tools/wos4/sx.py`.

## 5. Fuente [V]
- `FontDatabase.l`: `u16 n=6982`, `u16 544`, `u16 2` (páginas), `u16 0`; luego `n × (u16 código, u16 x, u16 y, u8 ancho,
  u8 página)`. No está ordenada por código (1.830 rupturas de orden), o sea que la búsqueda no es binaria.
  [V los datos; H lo de la búsqueda]
- `FontTexture.nif`: 2 `NiPixelData` DXT3 de 1024×7344. Página 0 = glifos blancos con alfa en filas de 36 px
  (alto útil 32 px: mayúsculas en filas 2–26, altura x desde la fila 8, línea base 26, descendentes hasta 31);
  página 1 = iconos de botones 32×32 (códigos U+FFC0…, y los ①–⑱ del texto).
- **Caracteres españoles: NO están** á é í ó ú ñ ü Á É Í Ó Ú Ñ Ü ¿ ¡ (tampoco º ª « » — ® ©). Sí están … ’ “ ” ×.
- La última fila de la página 0 (y=7310) está libre desde x=432 (592 px): **alcanza para agregar los 16 glifos
  sin cambiar el tamaño de la textura**.
- Plan (Fase 6): componer los glifos nuevos a partir de los existentes (letra + `´`/`¨`/`~`; `¿ ¡` = `? !` girados 180°),
  escribirlos en ese hueco re-codificando solo esos bloques DXT3 y **agregar 16 entradas al final** de `FontDatabase.l`.
- [V] El juego acepta entradas nuevas al final de la tabla (confirmado en el juego).
  Plan B si no: reutilizar entradas existentes de kanji que el texto en español no usa.

Implementación: `tools/wos4/fuente.py`.

## 6. Códigos de control
Ver `docs/codigos_control.md`.

## 7. Límites de longitud
No hay límites de bytes: todas las tablas y scripts se reconstruyen con longitudes libres. El límite real es el
**ancho en pantalla**: los saltos de línea son manuales (`\n` en tablas, `~_` en subtítulos). Como se conocen los
anchos de cada glifo, la validación mide cada línea en píxeles y la compara con el máximo que usa el inglés en el
mismo contexto (`longitud_max` del CSV = ancho máximo en px de una línea).

## 8. Plan técnico
1. Extracción a CSV (`tools/extraer.py`) → `traduccion/`.
2. `build_parche.py` regenera `build/US/...` desde los originales + CSV (sin traducción ⇒ idéntico byte a byte).
3. Fuente: glifos nuevos + tabla ampliada.
4. Traducción por lotes con memoria de traducción (las líneas repetidas entre variantes de escena se traducen una vez).
5. Validación automática y empaquetado (`instalar_parche.bat` copia `build/US` sobre la carpeta de Steam con backup).
