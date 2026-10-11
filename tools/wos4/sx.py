"""Desensamblador / reensamblador de scripts compilados .sx ("TH00") de Way of the Samurai 4.

Formato (verificado sobre los 1595 .sx del juego):
  cabecera 20 bytes: "TH00", u32 0, u32 len_codigo, u32 len_codigo alineado a 4, u32 0
  codigo: secuencia de instrucciones de 1 byte de opcode + operando:
    0x21 i32            entero
    0x24 f32            flotante
    0x25 i32            cantidad de argumentos
    0x22 u16 n + n*2    cadena UTF-16LE (texto visible)
    0x23 u32            longitud en bytes del bloque que sigue (salto relativo hacia adelante)
    0x33 i16
    0x38/0x39/0x50 i16  nombre ASCII: si >=0 es la longitud y sigue el literal;
                        si <0 es una referencia relativa (desde el final del operando) al
                        primer caracter de un literal anterior.
    resto               sin operando
"""
import struct
from dataclasses import dataclass

CABECERA = 20
SIN_OPERANDO = {0x00, 0x20, 0x30, 0x31, 0x32, 0x34, 0x35, 0x36, 0x37, 0x51, 0x52, 0x54}
NOMBRE = {0x38, 0x39, 0x50}
OP_TEXTO, OP_BLOQUE = 0x22, 0x23


class ErrorSx(Exception):
    pass


@dataclass
class Ins:
    op: int
    val: object = None      # int / bytes crudos (float) / str (texto) / bytes (nombre literal)
    ref: int = -1           # indice de instruccion destino (backref de nombre o fin de bloque)


def desensamblar(d):
    if d[:4] != b"TH00":
        raise ErrorSx("magic")
    cero, lcod, lpad, cero2 = struct.unpack_from("<4I", d, 4)
    if cero or cero2 or len(d) != CABECERA + lpad or not 0 <= lpad - lcod < 4 or lpad % 4:
        raise ErrorSx("cabecera inesperada")
    fin = CABECERA + lcod
    if any(d[fin:]):
        raise ErrorSx("relleno no nulo")
    ins, pos_ins, lit_en, pend = [], {}, {}, []
    p = CABECERA
    while p < fin:
        op = d[p]; i = len(ins); pos_ins[p] = i; q = p + 1
        if op in SIN_OPERANDO:
            ins.append(Ins(op))
        elif op in (0x21, 0x25):
            ins.append(Ins(op, struct.unpack_from("<i", d, q)[0])); q += 4
        elif op == 0x24:
            ins.append(Ins(op, d[q:q + 4])); q += 4
        elif op == 0x33:
            ins.append(Ins(op, struct.unpack_from("<h", d, q)[0])); q += 2
        elif op == OP_BLOQUE:
            v = struct.unpack_from("<I", d, q)[0]; q += 4
            ins.append(Ins(op)); pend.append((i, q + v))
        elif op == OP_TEXTO:
            n = struct.unpack_from("<H", d, q)[0]; q += 2
            if n >= 0x8000:
                raise ErrorSx("texto con longitud negativa en %x" % p)
            ins.append(Ins(op, d[q:q + 2 * n].decode("utf-16le", "surrogatepass"))); q += 2 * n
        elif op in NOMBRE:
            n = struct.unpack_from("<h", d, q)[0]; q += 2
            if n >= 0:
                lit_en[q] = i
                ins.append(Ins(op, d[q:q + n])); q += n
            else:
                if q + n not in lit_en:
                    raise ErrorSx("backref a algo que no es un literal en %x" % p)
                ins.append(Ins(op, None, lit_en[q + n]))
        else:
            raise ErrorSx("opcode desconocido %02x en %x" % (op, p))
        p = q
    if p != fin:
        raise ErrorSx("el codigo no termina en limite de instruccion")
    pos_ins[fin] = len(ins)
    for i, dest in pend:
        if dest not in pos_ins:
            raise ErrorSx("bloque que no termina en limite de instruccion")
        ins[i].ref = pos_ins[dest]
    return ins


def _tam(x):
    op = x.op
    if op in SIN_OPERANDO: return 1
    if op in (0x21, 0x24, 0x25, OP_BLOQUE): return 5
    if op == 0x33: return 3
    if op == OP_TEXTO: return 3 + 2 * len(x.val.encode("utf-16le", "surrogatepass")) // 2
    return 3 + (len(x.val) if x.val is not None else 0)


def ensamblar(ins):
    """Devuelve los bytes del .sx. Recalcula bloques y backrefs; si un backref ya no entra
    en i16 se convierte en literal (se modifica una copia, no `ins`)."""
    ins = [Ins(x.op, x.val, x.ref) for x in ins]
    while True:
        pos, p = [], CABECERA
        for x in ins:
            pos.append(p); p += _tam(x)
        pos.append(p)
        cambio = False
        for i, x in enumerate(ins):
            if x.op in NOMBRE and x.val is None:
                if (pos[x.ref] + 3) - (pos[i] + 3) < -0x8000:
                    t = ins[x.ref]
                    while t.val is None:
                        t = ins[t.ref]
                    x.val, x.ref, cambio = t.val, -1, True
        if not cambio:
            break
    out = bytearray()
    for i, x in enumerate(ins):
        op = x.op; out.append(op)
        if op in SIN_OPERANDO: pass
        elif op in (0x21, 0x25): out += struct.pack("<i", x.val)
        elif op == 0x24: out += x.val
        elif op == 0x33: out += struct.pack("<h", x.val)
        elif op == OP_BLOQUE: out += struct.pack("<I", pos[x.ref] - (pos[i] + 5))
        elif op == OP_TEXTO:
            b = x.val.encode("utf-16le", "surrogatepass")
            if len(b) // 2 >= 0x8000: raise ErrorSx("texto demasiado largo")
            out += struct.pack("<H", len(b) // 2) + b
        elif x.val is not None: out += struct.pack("<h", len(x.val)) + x.val
        else: out += struct.pack("<h", (pos[x.ref] + 3) - (pos[i] + 3))
    lcod = len(out); out += b"\0" * (-lcod % 4)
    return b"TH00" + struct.pack("<4I", 0, lcod, len(out), 0) + bytes(out)


def textos(ins):
    """Indices de las instrucciones de texto visible."""
    return [i for i, x in enumerate(ins) if x.op == OP_TEXTO]
