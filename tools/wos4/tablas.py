"""Tablas de cadenas UTF-16LE de Way of the Samurai 4 (archivos .l de texto).

Cuatro contenedores (todos verificados con ida y vuelta byte a byte):
  A  GameText*.l        u32 n, u32 8, n*u32 offset (relativo a 0x8), cadenas
  B  *Text.l (AS)       u32 n, n*(u32 id, u32 offset absoluto), cadenas
  P  As*TextPack.l      u32 n, n*(u32 id, u32 offset absoluto), n tablas tipo B
  N  NPCNameText.l      9*u32 offsets de seccion; cada seccion: u32 n, n*(u16 id, u16 genero, u32 offset
                        relativo a la seccion), cadenas; secciones alineadas a 4

Cada `leer_*` devuelve una estructura con las cadenas; cada `escribir_*` recibe la misma estructura
(con las cadenas posiblemente cambiadas) y regenera el archivo conservando el orden fisico original.
"""
import struct


def _z(d, o):
    e = o
    while d[e:e + 2] != b"\0\0":
        e += 2
    return d[o:e].decode("utf-16le", "surrogatepass")


def _pool(offs_orig, textos, base):
    """Emite las cadenas en el orden fisico original. Los indices que compartian offset siguen
    compartiendo cadena mientras su texto siga siendo igual. Devuelve (offsets nuevos, bytes)."""
    out = bytearray(); nuevos = [0] * len(textos); hecho = {}
    for i in sorted(range(len(textos)), key=lambda i: (offs_orig[i], i)):
        k = (offs_orig[i], textos[i])
        if k not in hecho:
            hecho[k] = base + len(out)
            out += textos[i].encode("utf-16le", "surrogatepass") + b"\0\0"
        nuevos[i] = hecho[k]
    return nuevos, bytes(out)


# ---- A ----
def leer_a(d):
    n, ocho = struct.unpack_from("<II", d, 0)
    if ocho != 8:
        raise ValueError("no es tabla A")
    offs = list(struct.unpack_from("<%dI" % n, d, 8))
    return {"offs": offs, "textos": [_z(d, o + 8) for o in offs]}


def escribir_a(t):
    n = len(t["textos"])
    offs, pool = _pool(t["offs"], t["textos"], 4 * n)
    return struct.pack("<II", n, 8) + struct.pack("<%dI" % n, *offs) + pool


# ---- B ----
def leer_b(d):
    n = struct.unpack_from("<I", d, 0)[0]
    ids, offs = [], []
    for i in range(n):
        a, o = struct.unpack_from("<II", d, 4 + 8 * i)
        ids.append(a); offs.append(o)
    return {"ids": ids, "offs": offs, "textos": [_z(d, o) for o in offs], "cola": len(d)}


def escribir_b(t, alinear=False):
    """`alinear=True` dentro de los packs (cada tabla se rellena a multiplo de 4)."""
    n = len(t["textos"])
    offs, pool = _pool(t["offs"], t["textos"], 4 + 8 * n)
    out = struct.pack("<I", n) + b"".join(struct.pack("<II", a, o) for a, o in zip(t["ids"], offs)) + pool
    return out + b"\0" * (-len(out) % 4) if alinear else out


# ---- P ----
def leer_p(d):
    n = struct.unpack_from("<I", d, 0)[0]
    ent = [struct.unpack_from("<II", d, 4 + 8 * i) for i in range(n)]
    fin = [o for _, o in ent[1:]] + [len(d)]
    return {"ids": [a for a, _ in ent], "tablas": [leer_b(d[o:f]) for (_, o), f in zip(ent, fin)]}


def escribir_p(t):
    n = len(t["ids"]); cuerpos = [escribir_b(x, True) for x in t["tablas"]]
    pos = 4 + 8 * n; cab = struct.pack("<I", n)
    for a, c in zip(t["ids"], cuerpos):
        cab += struct.pack("<II", a, pos); pos += len(c)
    return cab + b"".join(cuerpos)


# ---- N ----
def leer_n(d):
    ini = struct.unpack_from("<I", d, 0)[0]
    secs = list(struct.unpack_from("<%dI" % (ini // 4), d, 0))
    out = []
    for s in secs:
        n = struct.unpack_from("<I", d, s)[0]
        ent = [struct.unpack_from("<HHI", d, s + 4 + 8 * i) for i in range(n)]
        out.append({"ids": [e[0] for e in ent], "genero": [e[1] for e in ent], "offs": [e[2] for e in ent],
                    "textos": [_z(d, s + e[2]) for e in ent]})
    return {"secciones": out}


def escribir_n(t):
    secs = t["secciones"]; cab = 4 * len(secs); cuerpos = []; pos = cab; ini = []
    for s in secs:
        n = len(s["textos"])
        offs, pool = _pool(s["offs"], s["textos"], 4 + 8 * n)
        c = struct.pack("<I", n) + b"".join(struct.pack("<HHI", a, g, o) for a, g, o in zip(s["ids"], s["genero"], offs)) + pool
        c += b"\0\0"                      # terminador extra de seccion
        c += b"\0" * (-len(c) % 4)
        ini.append(pos); pos += len(c); cuerpos.append(c)
    return struct.pack("<%dI" % len(secs), *ini) + b"".join(cuerpos)
