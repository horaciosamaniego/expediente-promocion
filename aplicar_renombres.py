#!/usr/bin/env python3
"""
aplicar_renombres.py — aplica los 10 renombres acordados en:
  · manifest.csv    (columnas 'archivo', 'id' y 'seccion')
  · drive_ids.tsv   (columna del nombre, y el ID nuevo del ILUS)
  · los archivos dentro de mv/   (renombra en disco)

    python3 aplicar_renombres.py            # simulación, no cambia nada
    python3 aplicar_renombres.py --apply    # aplica

NO toca Google Drive: eso lo haces tú a mano. Al final el script imprime
la lista exacta de renombres pendientes en Drive.
"""
import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAN = ROOT / "manifest.csv"
TSV = ROOT / "drive_ids.tsv"
apply = "--apply" in sys.argv

# nombre actual -> nombre nuevo
RENOMBRES = {
    "MV-05.1_claustro-MgsInf-2018.pdf":                  "MV-05.2_claustro-MgsInf-2018.pdf",
    "MV-07.7.2_anid-evaluador.pdf":                      "MV-07.7.3_anid-evaluador.pdf",
    "MV-07.8.1a_DiscoreCities.pdf":                      "MV-07.8.3_discover-cities.pdf",
    "MV-07.6.NAC.0_socecol-2023-.pdf":                   "MV-07.6.NAC.13_socecol-2023-olmue.pdf",
    "MV-07.6.NAC.7a_socecol-2012.pdf":                   "MV-07.6.NAC.8_socecol-2012-b.pdf",
    "MV-07.4.9.1_wolff-espol-enviado.pdf":               "MV-07.4.E.1_wolff-espol-enviado.pdf",
    "MV-07.4.9.2_samaniego-rybski-pnasnexus-enviado.pdf":"MV-07.4.E.2_samaniego-rybski-pnasnexus-enviado.pdf",
    "MV-07.4.9.3_calbucheo-ufug-enviado.pdf":            "MV-07.4.E.3_calbucheo-ufug-enviado.pdf",
    "MV-07.4.9.4_bruning-scientometrics-enviado.pdf":    "MV-07.4.E.4_bruning-scientometrics-enviado.pdf",
    "MV-07.6.1.2_ilus-2025.pdf":                         "MV-07.6.INT.12_ilus-2025.pdf",
}

# nombre nuevo -> sección nueva (solo donde cambia de sección)
SECCION_NUEVA = {
    "MV-07.4.E.1_wolff-espol-enviado.pdf":                "07.4.E",
    "MV-07.4.E.2_samaniego-rybski-pnasnexus-enviado.pdf": "07.4.E",
    "MV-07.4.E.3_calbucheo-ufug-enviado.pdf":             "07.4.E",
    "MV-07.4.E.4_bruning-scientometrics-enviado.pdf":     "07.4.E",
    "MV-07.6.INT.12_ilus-2025.pdf":                       "07.6.INT",
}

# archivos ya subidos a Drive con nombre nuevo: su ID nuevo
IDS_NUEVOS = {
    "MV-07.6.INT.12_ilus-2025.pdf": "1NLftrvJGSxRXrOJICZ4jGH08q2XxCYVU",
}

# --------------------------------------------------------------------
print("═══ 1. manifest.csv ═══")
rows = list(csv.DictReader(MAN.open(encoding="utf-8-sig")))
campos = list(rows[0].keys())
tocadas = 0
for r in rows:
    arch = r["archivo"].strip()
    if not arch:
        continue
    nombre = Path(arch).name
    if nombre in RENOMBRES:
        nuevo = RENOMBRES[nombre]
        r["archivo"] = str(Path(arch).parent / nuevo)
        r["id"] = nuevo.split("_", 1)[0]
        if nuevo in SECCION_NUEVA:
            r["seccion"] = SECCION_NUEVA[nuevo]
        print(f"  {nombre}\n     -> {nuevo}   (id={r['id']}, seccion={r['seccion']})")
        tocadas += 1
print(f"  filas modificadas: {tocadas}")

if apply:
    shutil.copy2(MAN, MAN.with_suffix(".csv.bak_ren"))
    with MAN.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader(); w.writerows(rows)

# --------------------------------------------------------------------
print("\n═══ 2. drive_ids.tsv ═══")
if not TSV.exists():
    print("  no existe; se omite")
else:
    salida, n = [], 0
    for linea in TSV.read_text(encoding="utf-8").splitlines():
        if "\t" not in linea:
            salida.append(linea); continue
        nombre, fid = linea.split("\t", 1)
        nombre, fid = nombre.strip(), fid.strip()
        if nombre in RENOMBRES:
            nuevo = RENOMBRES[nombre]
            fid = IDS_NUEVOS.get(nuevo, fid)
            print(f"  {nombre} -> {nuevo}" + ("   [ID nuevo]" if nuevo in IDS_NUEVOS else ""))
            nombre = nuevo; n += 1
        salida.append(f"{nombre}\t{fid}")
    print(f"  líneas modificadas: {n}")
    if apply:
        shutil.copy2(TSV, TSV.with_suffix(".tsv.bak_ren"))
        TSV.write_text("\n".join(salida) + "\n", encoding="utf-8")

# --------------------------------------------------------------------
print("\n═══ 3. archivos en mv/ ═══")
base = ROOT if (ROOT / "mv").is_dir() else None
if base is None:
    cands = [d for d in ROOT.iterdir() if d.is_dir() and (d / "mv").is_dir()]
    base = cands[0] if len(cands) == 1 else None
if base is None:
    print("  no encontré la carpeta mv/; renombra los archivos a mano")
else:
    n = 0
    for p in sorted((base / "mv").rglob("*.pdf")):
        if p.name in RENOMBRES:
            destino = p.with_name(RENOMBRES[p.name])
            if destino.exists():
                print(f"  ya existe, se omite: {destino.name}")
                continue
            print(f"  {p.name} -> {destino.name}")
            if apply:
                p.rename(destino)
            n += 1
    print(f"  archivos renombrados: {n}")

# --------------------------------------------------------------------
print("\n═══ 4. PENDIENTE EN GOOGLE DRIVE (hazlo a mano) ═══")
for viejo, nuevo in RENOMBRES.items():
    if nuevo in IDS_NUEVOS:
        print(f"  BORRAR   {viejo}   (ya subiste {nuevo})")
    else:
        print(f"  RENOMBRAR {viejo}\n            -> {nuevo}")

print("\n" + ("✅ Aplicado. Respaldos: manifest.csv.bak_ren, drive_ids.tsv.bak_ren\n"
              "   Ahora: python3 merge_drive_ids.py drive_ids.tsv --apply && python3 build_index.py"
              if apply else "(simulación: no se cambió nada — repite con --apply)"))