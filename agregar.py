#!/usr/bin/env python3
"""
agregar.py — agrega un documento nuevo al expediente en un solo paso.

    python3 agregar.py ~/Descargas/certificado.pdf

Hace todo esto:
  1. pregunta los datos (numeral, sección, título, …)
  2. copia el PDF a la subcarpeta correcta de mv/ con el nombre MV-…
  3. agrega la fila a manifest.csv
  4. si le das el ID de Drive, lo escribe en manifest.csv y en drive_ids.tsv
  5. te recuerda qué falta

Para adjuntar el ID de Drive más tarde, sin volver a copiar nada:
    python3 agregar.py --drive MV-09.4 129KPO-tBzy8Z3v_4cchRGe9cT1_F38yK
"""
import csv
import shutil
import sys
import unicodedata
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAN = ROOT / "manifest.csv"
TSV = ROOT / "drive_ids.tsv"

# sección -> subcarpeta de mv/   (se compara como prefijo, del más largo al más corto)
CARPETAS = {
    "02":       "02-titulos-grados",
    "05":       "05-acreditaciones",
    "06":       "06-docencia",
    "07.4":     "07-investigacion/publicaciones",
    "07.6":     "07-investigacion/presentaciones",
    "07":       "07-investigacion",
    "09":       "09-vinculacion",
    "10":       "10-gestion",
    "13":       "13-reconocimientos",
    "14":       "14-idiomas",
    "15":       "15-profesional",
}


def base_mv():
    if (ROOT / "mv").is_dir():
        return ROOT
    c = [d for d in ROOT.iterdir() if d.is_dir() and (d / "mv").is_dir()]
    return c[0] if len(c) == 1 else None


def carpeta_de(seccion):
    for pref in sorted(CARPETAS, key=len, reverse=True):
        if seccion.startswith(pref):
            return CARPETAS[pref]
    return None


def slugify(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:45]


def leer_manifiesto():
    rows = list(csv.DictReader(MAN.open(encoding="utf-8-sig")))
    campos = list(rows[0].keys())
    if "drive_id" not in campos:
        campos.append("drive_id")
        for r in rows:
            r.setdefault("drive_id", "")
    return rows, campos


def guardar(rows, campos):
    shutil.copy2(MAN, MAN.with_suffix(".csv.bak_add"))
    with MAN.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(rows)


def anota_tsv(nombre, drive_id):
    lineas = TSV.read_text(encoding="utf-8").splitlines() if TSV.exists() else ["nombre\tid"]
    lineas = [l for l in lineas if not l.startswith(nombre + "\t")]
    lineas.append(f"{nombre}\t{drive_id}")
    TSV.write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ── modo: solo adjuntar un ID de Drive ────────────────────────────────
if "--drive" in sys.argv:
    i = sys.argv.index("--drive")
    try:
        mv_id, drive_id = sys.argv[i + 1], sys.argv[i + 2]
    except IndexError:
        sys.exit("Uso: python3 agregar.py --drive MV-09.4 <ID_de_Drive>")
    rows, campos = leer_manifiesto()
    for r in rows:
        if r["id"].strip() == mv_id:
            r["drive_id"] = drive_id
            guardar(rows, campos)
            anota_tsv(Path(r["archivo"]).name, drive_id)
            print(f"✅ {mv_id} enlazado a Drive.")
            print("   Ahora: python3 build_index.py && quarto render")
            sys.exit()
    sys.exit(f"No encontré la fila {mv_id} en manifest.csv")

# ── modo normal: agregar un documento ─────────────────────────────────
if len(sys.argv) < 2:
    sys.exit(__doc__)

origen = Path(sys.argv[1]).expanduser()
if not origen.is_file():
    sys.exit(f"No existe el archivo {origen}")

BASE = base_mv()
if BASE is None:
    sys.exit("No encuentro la carpeta mv/. Ejecuta el script junto a manifest.csv.")

rows, campos = leer_manifiesto()
usados = {r["id"].strip() for r in rows}
secciones = sorted({r["seccion"].strip() for r in rows if r["seccion"].strip()})

def preg(texto, default=""):
    v = input(f"{texto}{f' [{default}]' if default else ''}: ").strip()
    return v or default

print(f"\nArchivo: {origen.name}")
print(f"Secciones existentes: {', '.join(secciones)}\n")

seccion = preg("Sección (ej. 09, 07.4.3)")
carpeta = carpeta_de(seccion)
if carpeta is None:
    sys.exit(f"No sé en qué subcarpeta va la sección '{seccion}'. Agrégala al diccionario CARPETAS.")

mv_id = preg("Numeral MV- (ej. MV-09.4)")
if not mv_id.startswith("MV-"):
    mv_id = "MV-" + mv_id
if mv_id in usados:
    sys.exit(f"⚠️  El numeral {mv_id} ya está en uso. Elige otro.")

titulo = preg("Título del documento")
slug = preg("Nombre corto para el archivo", slugify(titulo) or slugify(origen.stem))
tipo = preg("Tipo", "Certificado")
fecha = preg("Fecha o año")
emisor = preg("Emisor (quién lo emite)")
notas = preg("Notas (opcional)")
drive_id = preg("ID de Drive (Enter si aún no lo subes)")

nombre = f"{mv_id}_{slug}.pdf"
destino = BASE / "mv" / carpeta / nombre
destino.parent.mkdir(parents=True, exist_ok=True)
if destino.exists():
    sys.exit(f"⚠️  Ya existe {destino.relative_to(BASE)}")
shutil.copy2(origen, destino)

sec_tit = next((r["seccion_titulo"] for r in rows if r["seccion"].strip() == seccion), "")
fila = {c: "" for c in campos}
fila.update({
    "id": mv_id, "seccion": seccion, "seccion_titulo": sec_tit, "titulo": titulo,
    "tipo": tipo, "fecha": fecha, "emisor": emisor,
    "archivo": f"mv/{carpeta}/{nombre}", "estado": "ok",
    "notas": notas, "drive_id": drive_id,
})
rows.append(fila)
guardar(rows, campos)
if drive_id:
    anota_tsv(nombre, drive_id)

print(f"\n✅ Copiado a  mv/{carpeta}/{nombre}")
print(f"✅ Fila {mv_id} agregada a manifest.csv (respaldo en manifest.csv.bak_add)")
print("\nFalta:")
print(f"  1. Subir  {nombre}  a Drive, en la carpeta {carpeta}")
if not drive_id:
    print(f"  2. Cuando tengas el ID:  python3 agregar.py --drive {mv_id} <ID>")
    print("  3. python3 build_index.py && quarto render")
else:
    print("  2. python3 build_index.py && quarto render")