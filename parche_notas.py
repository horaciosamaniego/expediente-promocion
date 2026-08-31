#!/usr/bin/env python3
"""parche_notas.py — controla cómo se muestran las notas."""
import pathlib, shutil, sys
p = pathlib.Path("build_index.py"); s = p.read_text(encoding="utf-8")
if "NOTAS_MODO" in s: sys.exit("Ya está parcheado.")

s = s.replace('MOSTRAR_PENDIENTES = False',
'''MOSTRAR_PENDIENTES = False

# Cómo mostrar la columna 'notas':
#   "inline"  -> al final del título, en letra pequeña (como está hoy)
#   "columna" -> como columna propia, encabezada "Detalle"
#   "ocultar" -> no se muestran
NOTAS_MODO = "inline"''')

s = s.replace(
'        out.append("| ID | Documento | Tipo | Fecha | Emisor | Estado | Archivo |")\n'
'        out.append("|---|---|---|---|---|---|---|")',
'        if NOTAS_MODO == "columna":\n'
'            out.append("| ID | Documento | Detalle | Tipo | Fecha | Emisor | Estado | Archivo |")\n'
'            out.append("|---|---|---|---|---|---|---|---|")\n'
'        else:\n'
'            out.append("| ID | Documento | Tipo | Fecha | Emisor | Estado | Archivo |")\n'
'            out.append("|---|---|---|---|---|---|---|")')

s = s.replace(
'            nota = f"<br><small>{r[\'notas\']}</small>" if r["notas"].strip() else ""\n'
'            out.append(\n'
'                f"| `{r[\'id\']}` | {r[\'titulo\']}{nota} | {r[\'tipo\']} | {r[\'fecha\']} | "\n'
'                f"{r[\'emisor\']} | {BADGE.get(estado, estado)} | {link} |"\n'
'            )',
'            n = r["notas"].strip()\n'
'            if NOTAS_MODO == "columna":\n'
'                out.append(\n'
'                    f"| `{r[\'id\']}` | {r[\'titulo\']} | {n} | {r[\'tipo\']} | {r[\'fecha\']} | "\n'
'                    f"{r[\'emisor\']} | {BADGE.get(estado, estado)} | {link} |"\n'
'                )\n'
'            else:\n'
'                nota = f"<br><small>{n}</small>" if (n and NOTAS_MODO == "inline") else ""\n'
'                out.append(\n'
'                    f"| `{r[\'id\']}` | {r[\'titulo\']}{nota} | {r[\'tipo\']} | {r[\'fecha\']} | "\n'
'                    f"{r[\'emisor\']} | {BADGE.get(estado, estado)} | {link} |"\n'
'                )')

shutil.copy2(p, "build_index.py.bak5")
p.write_text(s, encoding="utf-8")
print("✅ parcheado (respaldo en build_index.py.bak5). Edita NOTAS_MODO arriba del script.")