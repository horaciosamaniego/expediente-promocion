#!/usr/bin/env python3
"""
merge_drive_ids.py — agrega la columna 'drive_id' a manifest.csv a partir de
un volcado nombre<TAB>id producido por volcar_ids.gs.

    python3 merge_drive_ids.py drive_ids.tsv           # simulación
    python3 merge_drive_ids.py drive_ids.tsv --apply   # escribe manifest.csv

El emparejamiento es por nombre de archivo exacto (la última parte de la ruta
en la columna 'archivo'), así que no depende de cómo Drive haya organizado las
carpetas al subir.
"""
import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAN = ROOT / "manifest.csv"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tsv = Path(sys.argv[1]).expanduser()
    apply = "--apply" in sys.argv

    if not tsv.exists():
        sys.exit(f"No encuentro {tsv}")

    ids = {}
    for linea in tsv.read_text(encoding="utf-8").splitlines():
        if "\t" not in linea:
            continue
        nombre, fid = linea.split("\t", 1)
        nombre, fid = nombre.strip(), fid.strip()
        if nombre.lower() in ("nombre", "name") or not fid:
            continue
        ids[nombre] = fid
    print(f"IDs leídos del volcado: {len(ids)}")

    rows = list(csv.DictReader(MAN.open(encoding="utf-8")))
    campos = list(rows[0].keys())
    if "drive_id" not in campos:
        campos.append("drive_id")

    hit = miss = 0
    sin_id = []
    for r in rows:
        r.setdefault("drive_id", "")
        nombre = Path(r["archivo"].strip()).name if r["archivo"].strip() else ""
        if nombre and nombre in ids:
            r["drive_id"] = ids[nombre]
            hit += 1
        elif r["estado"].strip().lower() == "ok":
            miss += 1
            sin_id.append((r["id"], nombre))

    # Escribir PRIMERO: si la salida se canaliza a `head`, Python puede morir
    # con BrokenPipe antes de llegar al final y el archivo quedaría sin escribir.
    if apply:
        shutil.copy2(MAN, MAN.with_suffix(".csv.bak"))
        with MAN.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            w.writerows(rows)

    print(f"Filas con ID asignado : {hit}")
    print(f"Filas 'ok' sin ID     : {miss}")
    if sin_id:
        print("\n  Estas filas están marcadas 'ok' pero su archivo no aparece en Drive:")
        for rid, n in sin_id[:15]:
            print(f"    {rid:<20} {n}")
        if len(sin_id) > 15:
            print(f"    … y {len(sin_id)-15} más")

    if apply:
        print("\n✅ manifest.csv actualizado (respaldo en manifest.csv.bak)")
        print("   Ahora: python3 build_index.py")
    else:
        print("\n(simulación: no se escribió nada — repite con --apply)")

    sobrantes = set(ids) - {Path(r["archivo"].strip()).name for r in rows if r["archivo"].strip()}
    if sobrantes:
        print(f"\n  {len(sobrantes)} archivo(s) en Drive que nadie declara en el manifiesto:")
        for n in sorted(sobrantes)[:10]:
            print(f"    {n}")



if __name__ == "__main__":
    main()