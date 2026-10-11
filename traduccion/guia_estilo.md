# Guía de estilo de la traducción

## Variedad y registro
- **Español neutro latinoamericano con tuteo.** Segunda persona singular: *tú* (nunca voseo, nunca *vosotros*);
  plural: *ustedes*. Sin regionalismos fuertes (ni "tío/vale/coger" peninsulares ni "che/boludo" rioplatenses).
  Vocabulario preferido cuando hay alternativas: *computadora*, *agregar*, *costo*, *carnada*, *enojarse*, *apurarse*,
  *auto*; "saltar" (no "brincar"), "pelear/luchar", "lindo/bonito" indistintos.
- Se traduce **desde el inglés oficial**, que ya es una localización muy libre y humorística: se conserva ese tono
  (chistes, dobles sentidos picantes, exageraciones), adaptando el chiste cuando la traducción literal no funciona.

## Tratamiento (tú / usted)
Japón de 1855: la jerarquía importa. Regla general:
- **Usted**: subordinados a superiores (guardias a Kotobuki, hijas al ministro, sirvientes), comerciantes al cliente,
  desconocidos corteses, personajes ceremoniosos (Laura Lita, diplomáticos, el ministro en público).
- **Tú**: superiores a subordinados, matones, yakuza, niños, amigos, rivales en pelea, y el narrador/interfaz al jugador.
- El protagonista (opciones de diálogo) usa **tú** por defecto; en las opciones "corteses" puede usar usted.
- Los menús, tutoriales y mensajes del sistema tutean al jugador ("Elige un arma", "No tienes fichas").

## Registro por facción / personaje
| Quién | Voz |
|---|---|
| Discípulos de Prajna (Akagi, Kogure) | patriotas exaltados, solemnes y agresivos; "bárbaros", "perros del shogunato" |
| Shogunato / magistratura (Kotobuki, Moro, las hermanas Kinugawa) | burocrático y altanero; Moro es servil y pomposo; las hermanas son sádicas y juguetonas |
| Británicos (Laura, J.J., Melinda) | corteses y formales; Melinda marcial; cuando "hablan inglés" el texto va entre `<...>` y **se deja en inglés** |
| Pueblo, comerciantes | coloquial sencillo, contracciones del inglés (ain't, y'all) → habla popular sin marcar dialecto |
| Yakuza / matones | amenazante, vulgar moderado ("maldito", "idiota", "desgraciado") |
| Sensei Dojima (herrero), ancianos | sentencioso |

Insultos y vulgaridad: mantener la intensidad del inglés sin subirla. "Damn" → "Maldición"; "bastard" →
"desgraciado/bastardo"; "shit" → "mierda" solo si el inglés es igual de fuerte.

## Nombres y términos
- **Nombres japoneses y de personajes: se mantienen** (Akagi, Kogure, Kotobuki, Moro, Mayu, Chika, Yuri, Laura Lita,
  Melinda Megamelons, Jet Jenkins / J.J.). Sin macrones (la fuente no los tiene): *ronin*, *shogun*, *daimyo*.
- Términos de época que se mantienen: samurái (pl. samuráis), ronin, katana, shinobi, sensei, dojo, shogun, yakuza,
  harakiri, soba, sushi, onigiri, sake, mon. Ver `glosario.csv`.
- Títulos y cargos se traducen: *Chief Minister* → ministro principal; *Magistrate* → magistrado;
  *Ambassador* → embajadora; *Count* → conde; *Commander* → comandante.
- Los nombres genéricos de PNJ con chiste (Townie/Townette, Mafioso/Mafiette) se adaptan (Vecino/Vecina, etc.).
- Nombres de armas, técnicas y estilos japoneses romanizados se mantienen; los descriptivos en inglés se traducen.

## Ortotipografía
- Signos de apertura **¿ ¡** siempre. Tildes en mayúsculas.
- Mayúsculas a la española: solo la primera palabra y los nombres propios en títulos, menús y nombres de objeto
  ("Bolsa de armas", no "Bolsa De Armas"). Nombres de lugar del mapa: primera palabra con mayúscula.
- Comillas: `"` rectas o `“ ”`. **No usar** « » ni rayas — (no existen en la fuente): para incisos usar comas,
  paréntesis o `...`; para diálogo interrumpido, `-` o `...`.
- Ordinales sin º/ª: "2.o piso", "1.er piso" o reformular ("segundo piso").
- Puntos suspensivos: `...` (tres puntos), como en el inglés. Tartamudeos: "N-No...", "¿P-Por qué...?".
- Porcentajes: se conserva el signo que traiga el original (`%%` o `％`).
- Números y unidades como en el original (km, pts.).

## Códigos y longitudes
- Conservar todos los códigos de `docs/codigos_control.md`.
- Los saltos de línea son manuales: repartir el texto en líneas de largo parecido al inglés. La columna
  `longitud_max` es el ancho (px) de la línea más larga del inglés en ese contexto; no superarla.
- Subtítulos (`~_`): máximo 2 líneas salvo que el original tenga más.
- Fragmentos que el juego concatena (empiezan o terminan con espacio, p. ej. `" has been bested."`): conservar el
  espacio y redactar para que funcione pegado a un nombre (por eso no llevan ¡ ni ¿ de apertura).
