"""Modelo comun de extraccion/reconstruccion: cada `Fuente` es un archivo del juego con texto traducible."""
import csv, re
from . import tablas as T, sx
from .config import JUEGO, TRADUCCION

COLUMNAS = ["id", "archivo_origen", "contexto", "texto_en", "texto_es", "longitud_max", "notas"]
JAPONES = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
FUNC_VISIBLES = {"SetTelopTable": "subtítulo", "AddTalkInputChara": "opción de diálogo", "SetTalkSelect": "opción de diálogo",
                 "SetSelif": "frase de tienda", "SetBalloonTable": "globo de texto"}
CONTEXTO_GT = {"Main": "menú principal/sistema", "UI": "interfaz", "Item": "objeto", "Weapon": "arma", "Skill": "técnica",
               "SkillSheet": "hoja de técnicas", "Accessory": "accesorio", "Achievement": "logro",
               "CharacterModel": "creación de personaje", "Event": "evento/tutorial", "Mission": "misión", "Network": "red",
               "Record": "registro/estadísticas", "SaveData": "guardado", "Sect": "estilo/escuela", "Unlock": "desbloqueable"}


def traducible(s):
    return bool(s.strip()) and not JAPONES.search(s)


def a_csv(s):
    return s.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")


def de_csv(s):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "r": "\r", "\\": "\\"}.get(m.group(1), m.group(0)), s)


class Fuente:
    rel = None          # ruta relativa a la carpeta del juego

    def entradas(self):         # [(id, csv_rel, contexto, texto_en)]
        raise NotImplementedError

    def construir(self, es):    # es: {id: texto_es} -> bytes
        raise NotImplementedError

    def original(self):
        return (JUEGO / self.rel).read_bytes()


class FuenteA(Fuente):
    def __init__(self, nombre):
        self.nombre = nombre
        self.rel = f"US/GameText/GameText{nombre}.l"

    def entradas(self):
        t = T.leer_a(self.original())
        return [(f"GT:{self.nombre}:{i:04d}", f"gametext/GameText{self.nombre}.csv", CONTEXTO_GT[self.nombre], s)
                for i, s in enumerate(t["textos"]) if traducible(s)]

    def construir(self, es):
        t = T.leer_a(self.original())
        t["textos"] = [es.get(f"GT:{self.nombre}:{i:04d}", s) for i, s in enumerate(t["textos"])]
        return T.escribir_a(t)


class FuenteN(Fuente):
    rel = "US/GameText/NPCNameText.l"
    SEC = ["personaje", "genérico pueblo", "genérico yakuza", "genérico rebelde", "genérico funcionario",
           "genérico extranjero", "genérico independiente", "nombre al azar A", "nombre al azar B"]

    @staticmethod
    def _id(k, i):
        return f"NPC:{k}:{i:04d}"

    def entradas(self):
        t = T.leer_n(self.original())
        out = []
        for k, s in enumerate(t["secciones"]):
            for i, (x, g) in enumerate(zip(s["textos"], s["genero"])):
                if traducible(x):
                    gen = {1: "masc.", 2: "fem."}.get(g, str(g))
                    out.append((self._id(k, i), "gametext/NPCNameText.csv", f"nombre de PNJ: {self.SEC[k]} ({gen})", x))
        return out

    def construir(self, es):
        t = T.leer_n(self.original())
        for k, s in enumerate(t["secciones"]):
            s["textos"] = [es.get(self._id(k, i), x) for i, x in enumerate(s["textos"])]
        return T.escribir_n(t)


class FuenteP(Fuente):
    def __init__(self, carpeta, pack, pref):
        self.carpeta, self.pref = carpeta, pref
        self.rel = f"US/ActionScript/{carpeta}/{pack}"
        self._nombres = None

    def nombres(self):
        """Nombre de cada tabla del pack, deducido de los *Text.l sueltos con el mismo contenido."""
        if self._nombres is None:
            sueltos = {}
            for f in sorted((JUEGO / "US/ActionScript" / self.carpeta).glob("*Text.l")):
                if not f.name.endswith("TextPack.l"):
                    sueltos.setdefault(f.read_bytes(), f.name[:-len("Text.l")])
            t = T.leer_p(self.original())
            self._nombres = {tid: sueltos.get(T.escribir_b(tab), "tabla") for tid, tab in zip(t["ids"], t["tablas"])}
        return self._nombres

    def entradas(self):
        t = T.leer_p(self.original())
        nom = self.nombres()
        out = []
        for tid, tab in zip(t["ids"], t["tablas"]):
            csvrel = f"actionscript/{self.carpeta}/{tid:03d}_{nom[tid]}.csv"
            for sid, s in zip(tab["ids"], tab["textos"]):
                if traducible(s):
                    out.append((f"{self.pref}:{tid:03d}:{sid:05d}", csvrel, f"diálogo ({nom[tid]})", s))
        return out

    def construir(self, es):
        t = T.leer_p(self.original())
        for tid, tab in zip(t["ids"], t["tablas"]):
            tab["textos"] = [es.get(f"{self.pref}:{tid:03d}:{sid:05d}", s) for sid, s in zip(tab["ids"], tab["textos"])]
        return T.escribir_p(t)


class FuenteSx(Fuente):
    def __init__(self, ruta):
        self.rel = ruta.relative_to(JUEGO).as_posix()
        self.clave = self.rel[len("US/Script/"):-3]

    @staticmethod
    def _visibles(ins):
        """[(indice de instruccion, funcion)] de las cadenas visibles."""
        out = []
        for i, x in enumerate(ins):
            if x.op != sx.OP_TEXTO or not traducible(x.val):
                continue
            for j in range(i + 1, len(ins)):
                if ins[j].op == 0x50:
                    y = ins[j]
                    while y.val is None:
                        y = ins[y.ref]
                    fn = y.val.decode("latin1")
                    if fn in FUNC_VISIBLES:
                        out.append((i, fn))
                    break
        return out

    def _ids(self, ins):
        """Un id por texto distinto del archivo: {texto_en: [id, funcion, repeticiones]}."""
        d = {}
        for i, fn in self._visibles(ins):
            s = ins[i].val
            if s not in d:
                d[s] = [f"SX:{self.clave}:{len(d):04d}", fn, 0]
            d[s][2] += 1
        return d

    def entradas(self):
        ins = sx.desensamblar(self.original())
        return [(v[0], f"script/{self.clave}.csv", FUNC_VISIBLES[v[1]], s) for s, v in self._ids(ins).items()]

    def construir(self, es):
        d = self.original()
        ins = sx.desensamblar(d)
        ids = self._ids(ins)
        if not any(v[0] in es for v in ids.values()):
            return d
        for i, fn in self._visibles(ins):
            ins[i].val = es.get(ids[ins[i].val][0], ins[i].val)
        return sx.ensamblar(ins)


def fuentes():
    out = [FuenteA(n) for n in CONTEXTO_GT]
    out += [FuenteN(), FuenteP("Script", "AsScriptTextPack.l", "ASS"), FuenteP("UserCommand", "AsUserCmdTextPack.l", "ASU")]
    out += [FuenteSx(p) for p in sorted((JUEGO / "US/Script").rglob("*.sx"))]
    return out


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def escribir_csv(ruta, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, COLUMNAS, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def todos_los_csv():
    return sorted(p for p in TRADUCCION.rglob("*.csv") if p.name != "glosario.csv" and "lotes" not in p.parts)


def cargar_traducciones():
    """{id: texto_es real (sin escapes)} de todas las filas con texto_es no vacio."""
    es = {}
    for p in todos_los_csv():
        for f in leer_csv(p):
            if f["texto_es"]:
                es[f["id"]] = de_csv(f["texto_es"])
    return es
