#!/usr/bin/env python3
import csv, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
man = ROOT / "manifest.csv"; tsv = ROOT / "drive_ids.tsv"

print("== drive_ids.tsv ==")
if not tsv.exists():
    print("  NO EXISTE en", ROOT, " <-- ese es el problema")
else:
    txt = tsv.read_text(encoding="utf-8", errors="replace").splitlines()
    con_tab = sum(1 for l in txt if "\t" in l)
    print(f"  lineas: {len(txt)}   con tabulador: {con_tab}")
    if con_tab < 5:
        print("  <-- PROBLEMA: los tabuladores se perdieron al guardar.")
        print("      Primera linea tal cual:", repr(txt[1] if len(txt)>1 else txt[0])[:90])

print("\n== manifest.csv ==")
rows = list(csv.DictReader(man.open(encoding="utf-8-sig")))
cols = list(rows[0].keys())
print("  columnas:", cols)
if "drive_id" not in cols:
    print("  <-- PROBLEMA: no existe la columna drive_id. merge no escribio.")
else:
    llenos = sum(1 for r in rows if (r.get("drive_id") or "").strip())
    print(f"  filas con drive_id: {llenos} de {len(rows)}")

print("\n== build_index.py ==")
b = (ROOT / "build_index.py").read_text(encoding="utf-8")
print("  tiene celda_archivo:", "celda_archivo" in b)
for l in b.splitlines():
    if l.startswith("DRIVE_BASE"):
        print("  " + l[:80])