# Códigos de control y caracteres especiales

Todos deben quedar **idénticos** en `texto_es` (los comprueba `tools/validar.py`).

En los CSV los saltos de línea reales de las tablas se escriben como `\n` (barra + n) para que cada cadena ocupe
una sola línea del archivo; la herramienta los convierte al reconstruir.

| Código | Dónde | Significado | Regla |
|---|---|---|---|
| `\n` | tablas GameText y ActionScript | salto de línea manual | se puede cambiar la cantidad/posición para que el texto entre |
| `~_` | subtítulos de `.sx` (`SetTelopTable`) | salto de línea | ídem; evitar más líneas que el original |
| `%s`, `%d`, `%x`, `%c`, `%5.1f`, `%%` | todas | formato estilo printf | mismos códigos y **en el mismo orden** |
| `%e1` (`%e` + dígito) | GameText | valor numérico insertado por el juego | conservar tal cual |
| `%PNAME%` | ActionScript | nombre del jugador | conservar |
| `%MONEY%`, `%PUPILNUM%` | (en el ejecutable) | dinero / n.º de discípulos | conservar si aparecen |
| `①`–`⑱` (U+2460–U+2471) | todas | iconos de botones del mando | conservar el mismo carácter |
| `←` `→` `↑` `↓` `▲` `▼` `○` `×` `☆` | menús | símbolos/iconos | conservar |
| `<...>` | diálogos | palabras dichas en inglés por extranjeros (o "en idioma extranjero") | se conservan `<` `>`; el contenido se deja en inglés (ver guía de estilo) |
| `^...^` | subtítulos | [hipotesis] resalta el texto encerrado (aparece rodeando nombres clave, p. ej. `^Disciples of Prajna^`) | conservar los dos `^` alrededor del término traducido |
| `[...]` | tutoriales, misiones | títulos de sección / nombres de misión | conservar los corchetes; el contenido se traduce |
| `文` | `SetSelif` (`"That'll be %d文."`) | símbolo de moneda (mon) | conservar |
| `…` `’` `“` `”` `％` `：` | varias | puntuación presente en la fuente | se pueden usar |

Caracteres que **no** existen en la fuente original y agrega el parche: `á é í ó ú ñ ü Á É Í Ó Ú Ñ Ü ¿ ¡`.
No usar: `« » — – º ª` ni otras letras acentuadas (à, ç, etc.); usar `"` o `“ ”`, `-` / `...` y reformular.

## Cadenas que no se traducen
- Las que contienen japonés (restos de depuración que la versión inglesa nunca tradujo).
- En los `.sx`, todo argumento que no sea de `SetTelopTable`, `AddTalkInputChara`, `SetTalkSelect`, `SetSelif`
  o `SetBalloonTable` (rutas de escenas, nombres de eventos, archivos).
