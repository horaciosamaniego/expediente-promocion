#!/usr/bin/env python3
"""
diagnostico.py — dice exactamente por qué un documento no aparece enlazado.
Ejecutar desde la misma carpeta que manifest.csv:  python3 diagnostico.py
"""
import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
MAN = ROOT / "manifest.csv"

print(f"Carpeta actual : {ROOT}")
print(f"manifest.csv   : {'SÍ' if MAN.exists() else 'NO ← problema grave'}")

mv = ROOT / "mv"
print(f"carpeta mv/    : {'SÍ' if mv.is_dir() else 'NO ← problema grave'}")
if mv.is_dir():
    pdfs = [p for p in mv.rglob("*.pdf")]
    print(f"PDFs bajo mv/  : {len(pdfs)}")
    pub = mv / "07-investigacion" / "publicaciones"
    print(f"  en publicaciones/: {len(list(pub.glob('*.pdf'))) if pub.is_dir() else 'la carpeta no existe'}")

if not MAN.exists():
    raise SystemExit("\nSin manifest.csv no puedo seguir.")

rows = list(csv.DictReader(MAN.open(encoding="utf-8")))
print(f"\nFilas en el manifiesto: {len(rows)}")

diag = Counter()
arreglables, rotas = [], []
for r in rows:
    arch = r["archivo"].strip()
    est = r["estado"].strip().lower()
    existe = (ROOT / arch).exists() if arch else False
    if est == "ok" and existe:
        diag["✅ ok y el archivo está (se enlaza)"] += 1
    elif est == "ok" and not existe:
        diag["❌ ok pero NO está el archivo"] += 1
        rotas.append((r["id"], arch))
    elif existe:
        diag["⚠️  el archivo ESTÁ pero el estado no es 'ok' (no se enlaza)"] += 1
        arreglables.append(r["id"])
    else:
        diag["·  pendiente y sin archivo (normal)"] += 1

print()
for k, v in diag.most_common():
    print(f"  {v:>3}  {k}")

if arreglables:
    print(f"\n→ {len(arreglables)} filas se arreglan marcándolas 'ok'. Ejecuta:")
    print("   python3 diagnostico.py --fix")

if rotas:
    print(f"\n→ {len(rotas)} filas apuntan a un archivo inexistente:")
    for rid, a in rotas[:12]:
        print(f"     {rid:<16} {a}")
    if len(rotas) > 12:
        print(f"     … y {len(rotas)-12} más")

import sys
if "--fix" in sys.argv and arreglables:
    txt = MAN.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    for line in txt:
        rid = line.split(",", 1)[0]
        if rid in arreglables:
            line = line.replace(",pendiente,", ",ok,").replace(",solicitado,", ",ok,")
        out.append(line)
    MAN.write_text("".join(out), encoding="utf-8")
    print(f"\n✅ {len(arreglables)} filas marcadas 'ok'. Ahora: python3 build_index.py && quarto render")