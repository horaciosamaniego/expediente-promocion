#!/usr/bin/env python3
"""parche_encabezados.py — los títulos de sección salen de la Plantilla."""
import pathlib, shutil, sys

p = pathlib.Path("build_index.py")
s = p.read_text(encoding="utf-8")
if "ENCABEZADOS" in s:
    sys.exit("Ya está parcheado.")

bloque = '''# ─────────── ENCABEZADOS (numerales de la Plantilla Única) ───────────
# Clave = valor de la columna 'seccion'.  Valor = título tal como debe salir.
# Si una sección no está aquí, se usa "<seccion>. <seccion_titulo>".
ENCABEZADOS = {
    "02":         "2. Títulos profesionales, grados académicos y postdoctorados",
    "05":         "5. Acreditaciones en programas de postgrado",
    "06":         "6. Docencia en la UACh",
    "07":         "7. Investigación",
    "07.4.2":     "7.4.2 Publicaciones — Capítulos de libro",
    "07.4.3":     "7.4.3 Publicaciones en revistas WoS",
    "07.4.4":     "7.4.4 Publicaciones en revistas Scopus",
    "07.4.6":     "7.4.6 Publicaciones en otras revistas con comité editorial",
    "07.4.7":     "7.4.7 Publicaciones en revistas sin comité editorial (preprints)",
    "07.4.E":     "7.4 Publicaciones — Manuscritos enviados",
    "07.6.INT":   "7.6 Presentaciones a congresos — Internacionales",
    "07.6.NAC":   "7.6 Presentaciones a congresos — Nacionales",
    "07.6.1":     "7.6.1 Conferencista invitado",
    "09":         "9. Vinculación con el medio",
    "10":         "10. Gestión y compromiso institucional",
    "13":         "13. Reconocimientos, premios y becas",
    "15":         "15. Actividades profesionales relevantes",
}
# ─────────────────────────────────────────────────────────────────────

'''
s = s.replace("# ─────────── TEXTO DE LA PÁGINA ───────────", bloque + "# ─────────── TEXTO DE LA PÁGINA ───────────")

# agrupar solo por 'seccion' (une las secciones duplicadas)
s = s.replace(
    '        by_section[(r["seccion"].strip(), r["seccion_titulo"].strip())].append(r)',
    '        by_section[r["seccion"].strip()].append(r)')
s = s.replace(
    '    for (num, titulo), items in sorted(by_section.items(), key=lambda kv: orden_natural(kv[0][0])):\n'
    '        out.append(f"## {num}. {titulo}")',
    '    for num, items in sorted(by_section.items(), key=lambda kv: orden_natural(kv[0])):\n'
    '        titulo = ENCABEZADOS.get(num) or f\'{num}. {items[0]["seccion_titulo"].strip()}\'\n'
    '        out.append(f"## {titulo}")')

shutil.copy2(p, "build_index.py.bak4")
p.write_text(s, encoding="utf-8")
print("✅ parcheado (respaldo en build_index.py.bak4)")