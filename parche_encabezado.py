#!/usr/bin/env python3
"""parche_encabezado.py — hace que build_index.py use TITULO, SUBTITULO e INTRO."""
import pathlib, re, shutil, sys

p = pathlib.Path("build_index.py")
s = p.read_text(encoding="utf-8")

ini = s.find('    out.append("---")')
fin = s.find('    if pendientes')
if ini == -1 or fin == -1 or fin < ini:
    sys.exit("No encontré el bloque a reemplazar. Avísame y te mando el archivo completo.")

nuevo = '''    out.append("---")
    out.append(f\'title: "{TITULO}"\')
    if SUBTITULO:
        out.append(f\'subtitle: "{SUBTITULO}"\')
    out.append("toc: true")
    out.append("toc-depth: 2")
    out.append("---")
    out.append("")
    if INTRO.strip():
        out.append(INTRO.strip())
        out.append("")
    if MOSTRAR_NOTA_GENERADO:
        out.append("> Índice generado automáticamente desde `manifest.csv`.")
        out.append("")
    if MOSTRAR_AVANCE:
        out.append(f"**Avance:** {listos} de {total} documentos en carpeta "
                   f"({100 * listos // total if total else 0} %).")
        out.append("")

'''
shutil.copy2(p, "build_index.py.bak3")
s = s[:ini] + nuevo + s[fin:]
s = s.replace("    if pendientes:\n", "    if pendientes and MOSTRAR_PENDIENTES:\n")
p.write_text(s, encoding="utf-8")
print("✅ build_index.py parcheado (respaldo en build_index.py.bak3)")
print("   Ahora: python3 build_index.py && quarto render")