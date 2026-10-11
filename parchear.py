"""Parche al español de Way of the Samurai 4 (PC/Steam): instalador y desinstalador.

No incluye ningún archivo del juego. Lee los archivos originales de TU instalación, les aplica la traducción
(carpeta traduccion/) y los glifos nuevos de la fuente (datos/fuente.json), y guarda antes una copia de cada
original en <juego>/_backup_parche_es/.

Uso:
    parchear.py                         menú interactivo
    parchear.py instalar   ["carpeta del juego"]
    parchear.py desinstalar ["carpeta del juego"]
"""
import base64, csv, hashlib, json, os, shutil, sys
from pathlib import Path

VERSION = "1.0.0"
CONGELADO = getattr(sys, "frozen", False)
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
EXE = "WayOfTheSamurai4.exe"
CARPETA_STEAM = "Way of the Samurai 4"
BACKUP = "_backup_parche_es"


class Problema(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------------------------------------------
# Localizar el juego
# ---------------------------------------------------------------------------------------------------------------
def bibliotecas_steam():
    raices = []
    try:
        import winreg
        for hive, clave in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")):
            for valor in ("SteamPath", "InstallPath"):
                try:
                    with winreg.OpenKey(hive, clave) as k:
                        raices.append(Path(winreg.QueryValueEx(k, valor)[0]))
                except OSError:
                    pass
    except ImportError:
        pass
    for var in ("ProgramFiles(x86)", "ProgramFiles"):
        if os.environ.get(var):
            raices.append(Path(os.environ[var]) / "Steam")
    libs = []
    for r in raices:
        libs.append(r)
        vdf = r / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            for linea in vdf.read_text(encoding="utf-8", errors="replace").splitlines():
                partes = linea.strip().split('"')
                if len(partes) >= 4 and partes[1] == "path":
                    libs.append(Path(partes[3].replace("\\\\", "\\")))
    return libs


def buscar_juego():
    vistos = set()
    for lib in bibliotecas_steam():
        j = lib / "steamapps" / "common" / CARPETA_STEAM
        if str(j).lower() not in vistos and (j / EXE).exists():
            return j
        vistos.add(str(j).lower())
    return None


def pedir_juego(arg=None):
    if arg:
        j = Path(arg.strip().strip('"'))
    else:
        j = buscar_juego()
        if j:
            print(f"Juego encontrado: {j}")
        else:
            print("No encontré el juego en las bibliotecas de Steam.")
            print(f"Escribe o pega la carpeta del juego (la que contiene {EXE}):")
            j = Path(input("> ").strip().strip('"'))
    if not (j / EXE).exists():
        raise Problema(f"No encuentro {EXE} en \"{j}\".")
    if (j.parent / "build_parche.py").exists():
        raise Problema("Esa es la copia de trabajo del proyecto de traducción, no la instalación del juego.")
    return j


# ---------------------------------------------------------------------------------------------------------------
# Datos del parche
# ---------------------------------------------------------------------------------------------------------------
def cargar_traduccion():
    es = {}
    archivos = sorted(p for p in (BASE / "traduccion").rglob("*.csv") if p.name != "glosario.csv")
    if not archivos:
        raise Problema("Falta la carpeta traduccion/ junto al parcheador.")
    escapes = {"n": "\n", "r": "\r", "\\": "\\"}
    for p in archivos:
        with open(p, encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f):
                t = fila["texto_es"]
                if not t:
                    continue
                if "\\" in t:
                    out, i = [], 0
                    while i < len(t):
                        if t[i] == "\\" and i + 1 < len(t):
                            out.append(escapes.get(t[i + 1], "\\" + t[i + 1]))
                            i += 2
                        else:
                            out.append(t[i])
                            i += 1
                    t = "".join(out)
                es[fila["id"]] = t
    return es


def aplicar_trozos(orig, info):
    nuevo = bytearray(orig[:info["largo"]].ljust(info["largo"], b"\0"))
    for pos, b64 in info["trozos"]:
        datos = base64.b64decode(b64)
        nuevo[pos:pos + len(datos)] = datos
    return bytes(nuevo)


# ---------------------------------------------------------------------------------------------------------------
# Instalar / desinstalar
# ---------------------------------------------------------------------------------------------------------------
def instalar(juego):
    manifiesto = json.loads((BASE / "datos" / "manifiesto.json").read_text(encoding="utf-8"))
    fuente = json.loads((BASE / "datos" / "fuente.json").read_text(encoding="utf-8"))
    backup = juego / BACKUP

    def original(rel):
        """El archivo original: el del backup si ya hay un parche instalado, si no el del juego."""
        p = backup / rel
        return (p if p.exists() else juego / rel).read_bytes()

    print("\n[1/4] Comprobando los archivos originales del juego...")
    originales, raros = {}, []
    for rel, (sha_orig, _) in manifiesto.items():
        try:
            d = original(rel)
        except OSError:
            raros.append(rel + "  (no existe)")
            continue
        if sha(d) != sha_orig:
            raros.append(rel)
        originales[rel] = d
    if raros:
        for r in raros[:10]:
            print("   distinto:", r)
        if len(raros) > 10:
            print(f"   ... y {len(raros) - 10} más")
        raise Problema(
            f"{len(raros)} archivos no coinciden con la versión del juego para la que se hizo este parche.\n"
            "Si tenías otro parche o mod de texto instalado, quítalo. En Steam: clic derecho en el juego >\n"
            "Propiedades > Archivos instalados > Verificar integridad de los archivos, y vuelve a intentarlo.")

    print("[2/4] Cargando la traducción...")
    es = cargar_traduccion()
    print(f"      {len(es)} textos en español")

    print("[3/4] Generando los archivos traducidos (puede tardar un minuto)...")
    os.environ["WOS4_JUEGO"] = str(juego)
    sys.path.insert(0, str(BASE / "tools"))
    from wos4 import proyecto as P
    P.Fuente.original = lambda self: originales[self.rel]
    nuevos = {}
    for f in P.fuentes():
        if f.rel in manifiesto:
            nuevos[f.rel] = f.construir(es)
    for rel, info in fuente.items():
        nuevos[rel] = aplicar_trozos(originales[rel], info)
    faltan = sorted(set(manifiesto) - set(nuevos))
    if faltan:
        raise Problema(f"No pude generar {len(faltan)} archivos (por ejemplo {faltan[0]}).")
    distintos = [rel for rel, d in nuevos.items() if sha(d) != manifiesto[rel][1]]
    if distintos:
        msg = f"{len(distintos)} archivos generados difieren de la versión publicada (por ejemplo {distintos[0]})."
        if CONGELADO:
            raise Problema(msg + "\nNo se modificó nada. Por favor avisa en la página del proyecto.")
        print("      AVISO:", msg, "Es normal si editaste la traducción.")

    print("[4/4] Guardando copia de seguridad e instalando...")
    for rel, d in nuevos.items():
        b = backup / rel
        if not b.exists():
            b.parent.mkdir(parents=True, exist_ok=True)
            b.write_bytes(originales[rel])
    for rel, d in nuevos.items():
        (juego / rel).write_bytes(d)
    (backup / "LEEME.txt").write_text(
        f"Copia de seguridad de los archivos originales (parche al español v{VERSION}).\n"
        "No borres esta carpeta: el desinstalador la necesita.\n", encoding="utf-8")
    print(f"\nListo: {len(nuevos)} archivos instalados. Originales guardados en:\n   {backup}")
    print("Ya puedes abrir el juego. ¡Que lo disfrutes!")


def desinstalar(juego):
    backup = juego / BACKUP
    if not backup.exists():
        raise Problema("No hay copia de seguridad en esta carpeta: el parche no está instalado (o se instaló de otra forma).\n"
                       "Puedes restaurar el juego desde Steam con \"Verificar integridad de los archivos\".")
    n = 0
    for p in sorted(backup.rglob("*")):
        if p.is_file() and p.name != "LEEME.txt":
            destino = juego / p.relative_to(backup)
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, destino)
            n += 1
    shutil.rmtree(backup)
    print(f"\nListo: {n} archivos originales restaurados. El juego vuelve a estar en inglés.")


def confirmar(pregunta):
    return input(f"{pregunta} [s/n] ").strip().lower().startswith("s")


def main():
    print("=" * 66)
    print(f"  Way of the Samurai 4 - Parche al español (no oficial)  v{VERSION}")
    print("=" * 66)
    args = sys.argv[1:]
    interactivo = not args
    try:
        if interactivo:
            print("\n  1) Instalar el parche\n  2) Desinstalar (volver al juego original)\n  3) Salir\n")
            op = input("Elige una opción [1-3]: ").strip()
            accion = {"1": "instalar", "2": "desinstalar"}.get(op)
            if not accion:
                return 0
            juego = pedir_juego()
            print("\nCierra el juego antes de continuar.")
            if not confirmar(f"¿{accion.capitalize()} en \"{juego}\"?"):
                return 0
        else:
            accion = args[0].lower()
            if accion not in ("instalar", "desinstalar"):
                print(__doc__)
                return 2
            juego = pedir_juego(args[1] if len(args) > 1 else None)
        (instalar if accion == "instalar" else desinstalar)(juego)
        return 0
    except Problema as e:
        print(f"\n[ERROR] {e}")
        return 1
    except PermissionError as e:
        print(f"\n[ERROR] Sin permiso para escribir: {e}\nCierra el juego y prueba otra vez (o ejecuta como administrador).")
        return 1
    finally:
        if interactivo:
            input("\nPulsa Enter para cerrar...")


if __name__ == "__main__":
    sys.exit(main())
