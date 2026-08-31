#!/usr/bin/env python3
"""
sincronizar_ids.py — reconstruye la columna 'id' a partir del nombre del archivo.

Regla: si el archivo se llama  MV-07.4.3.1_li-2026-sust-cities.pdf
       entonces el id es       MV-07.4.3.1

    python3 sincronizar_ids.py           # muestra las diferencias, no cambia nada
    python3 sincronizar_ids.py --apply   # corrige manifest.csv (deja respaldo .bak)

Al final avisa si quedan ids repetidos, que es lo único que hay que resolver a mano.
"""
import csv
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAN = ROOT / "manifest.csv"
apply = "--apply" in sys.argv

rows = list(csv.DictReader(MAN.open(encoding="utf-8")))
campos = list(rows[0].keys())

cambios, sin_archivo = [], []
for r in rows:
    arch = r["archivo"].strip()
    if not arch:
        sin_archivo.append(r["id"])
        continue
    nuevo = Path(arch).name.split("_", 1)[0]        # MV-07.4.3.1
    if nuevo != r["id"].strip():
        cambios.append((r["id"].strip(), nuevo, r["titulo"][:48]))
        r["id"] = nuevo

if apply:
    shutil.copy2(MAN, MAN.with_suffix(".csv.bak2"))
    with MAN.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(rows)

print(f"Filas revisadas      : {len(rows)}")
print(f"Ids corregidos       : {len(cambios)}")
print(f"Filas sin archivo    : {len(sin_archivo)}  (se dejan como están)")

if cambios:
    print("\n  antes            ->  después           documento")
    for viejo, nuevo, tit in cambios[:40]:
        print(f"  {viejo:<16} ->  {nuevo:<16}  {tit}")
    if len(cambios) > 40:
        print(f"  … y {len(cambios)-40} más")

dups = [i for i, n in Counter(r["id"].strip() for r in rows).items() if n > 1]
if dups:
    print(f"\n⚠️  {len(dups)} id(s) repetido(s) — hay que renombrar uno de los archivos:")
    for d in dups:
        for r in rows:
            if r["id"].strip() == d:
                print(f"     {d:<16} {Path(r['archivo']).name}")
else:
    print("\n✅ Sin ids repetidos.")

print("\n" + ("✅ manifest.csv corregido (respaldo en manifest.csv.bak2)"
              if apply else "(simulación: no se cambió nada — repite con --apply)"))