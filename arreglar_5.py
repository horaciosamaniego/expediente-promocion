#!/usr/bin/env python3
"""
arreglar_5.py — corrige los 5 problemas que reporta build_index.py tras el renombrado.

    python3 arreglar_5.py           # simulación
    python3 arreglar_5.py --apply   # aplica

Corrige:
  1. MV-07.3.2 duplicado  -> el FONDEF D10I1038 pasa a MV-07.3.4
  2. MV-07.6.NAC.7 sin archivo + huérfano NAC.8_socecol-2012-a
                          -> el archivo "-a" vuelve a ser NAC.7
  3. MV-07.7.1 duplicado  -> el GST-FONDECYT pasa a MV-07.7.4
  4. huérfano MV-07.4.7.1_samaniego-2025-biorxiv -> se le crea su fila
"""
import csv, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAN, TSV = ROOT / "manifest.csv", ROOT / "drive_ids.tsv"
apply = "--apply" in sys.argv

BASE = ROOT if (ROOT / "mv").is_dir() else None
if BASE is None:
    c = [d for d in ROOT.iterdir() if d.is_dir() and (d / "mv").is_dir()]
    BASE = c[0] if len(c) == 1 else None

RENOMBRES = {
    "MV-07.6.NAC.8_socecol-2012-a.pdf": "MV-07.6.NAC.7_socecol-2012-a.pdf",
    "MV-07.7_GST-FONDECYT.pdf":         "MV-07.7.4_gst-fondecyt.pdf",
}

rows = list(csv.DictReader(MAN.open(encoding="utf-8-sig")))
campos = list(rows[0].keys())
if "drive_id" not in campos:
    campos.append("drive_id")
    for r in rows: r.setdefault("drive_id", "")

def nom(r): return Path(r["archivo"].strip()).name if r["archivo"].strip() else ""

# 1. FONDEF D10I1038 -> MV-07.3.4
for r in rows:
    if "fondef-d10i1038" in nom(r).lower():
        r["id"] = "MV-07.3.4"
        r["archivo"] = "mv/07-investigacion/MV-07.3.4_fondef-d10i1038.pdf"
        print(f"1. FONDEF D10I1038 -> MV-07.3.4  (estado: {r['estado']})")

# 2 y 3. renombres
for r in rows:
    n = nom(r)
    if n in RENOMBRES:
        nuevo = RENOMBRES[n]
        r["archivo"] = str(Path(r["archivo"]).parent / nuevo)
        r["id"] = nuevo.split("_", 1)[0]
        print(f"   fila -> {r['id']}  ({nuevo})")
# la fila NAC.7 apunta a un archivo que ya no existe: reapuntarla
for r in rows:
    if nom(r) == "MV-07.6.NAC.7_socecol-2012.pdf":
        r["archivo"] = "mv/07-investigacion/presentaciones/MV-07.6.NAC.7_socecol-2012-a.pdf"
        r["id"] = "MV-07.6.NAC.7"
        print("2. MV-07.6.NAC.7 reapuntada a socecol-2012-a")
# la fila con id MV-07.7.1 que NO es publons
for r in rows:
    if r["id"].strip() == "MV-07.7.1" and "publons" not in nom(r).lower():
        r["id"] = "MV-07.7.4"
        r["archivo"] = "mv/07-investigacion/MV-07.7.4_gst-fondecyt.pdf"
        print("3. GST-FONDECYT -> MV-07.7.4")

# 4. fila del preprint bioRxiv
if not any("biorxiv" in nom(r).lower() for r in rows):
    sec = "07.4.7"
    st = next((r["seccion_titulo"] for r in rows if r["seccion"].strip() == sec), "Publicaciones — Preprints")
    fila = {c: "" for c in campos}
    fila.update({
        "id": "MV-07.4.7.1", "seccion": sec, "seccion_titulo": st,
        "titulo": "[AUTOR CORRESPONDIENTE] Socioeconomic Segregation and Park Greenness: Insights Across a Strong Latitudinal Gradient",
        "tipo": "Preprint", "fecha": "2025", "emisor": "bioRxiv",
        "archivo": "mv/07-investigacion/publicaciones/MV-07.4.7.1_samaniego-2025-biorxiv.pdf",
        "estado": "ok", "notas": "doi 10.1101/2025.03.03.640840",
        "drive_id": "1arBoyb6MzXDMeBi8xPX1qmq9rMNI1lRz",
    })
    rows.append(fila)
    print("4. Fila MV-07.4.7.1 (bioRxiv) creada")

if apply:
    shutil.copy2(MAN, MAN.with_suffix(".csv.bak_fix5"))
    with MAN.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos); w.writeheader(); w.writerows(rows)
    if TSV.exists():
        out = []
        for l in TSV.read_text(encoding="utf-8").splitlines():
            if "\t" in l:
                n, i = l.split("\t", 1)
                if n.strip() in RENOMBRES: n = RENOMBRES[n.strip()]
                out.append(f"{n.strip()}\t{i.strip()}")
            else: out.append(l)
        shutil.copy2(TSV, TSV.with_suffix(".tsv.bak_fix5"))
        TSV.write_text("\n".join(out) + "\n", encoding="utf-8")
    if BASE:
        for p in (BASE / "mv").rglob("*.pdf"):
            if p.name in RENOMBRES:
                d = p.with_name(RENOMBRES[p.name])
                if not d.exists(): p.rename(d); print(f"   archivo renombrado: {d.name}")

print("\nPENDIENTE EN DRIVE (a mano):")
for v, n in RENOMBRES.items(): print(f"  RENOMBRAR {v}\n            -> {n}")
print("\n" + ("✅ Aplicado. Ahora: python3 build_index.py" if apply
              else "(simulación — repite con --apply)"))