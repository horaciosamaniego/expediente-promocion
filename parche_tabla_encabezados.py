#!/usr/bin/env python3
"""
parche_TABLA_ENCABEZADOS.py — agrega la tabla ENCABEZADOS a build_index.py
para que los títulos de sección usen los numerales de la Plantilla Única,
y une las secciones duplicadas (agrupa solo por 'seccion').

    python3 parche_TABLA_ENCABEZADOS.py
"""
import pathlib, shutil, sys

p = pathlib.Path("build_index.py")
if not p.exists():
    sys.exit("No encuentro build_index.py en esta carpeta.")
s = p.read_text(encoding="utf-8")
if "ENCABEZADOS" in s:
    sys.exit("Ya está parcheado: la tabla ENCABEZADOS ya existe.")

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

ancla = "# ─────────── TEXTO DE LA PÁGINA ───────────"
if ancla in s:
    s = s.replace(ancla, bloque + ancla, 1)
else:
    ancla2 = 'ESTADOS = {'
    if ancla2 not in s:
        sys.exit("No encontré dónde insertar la tabla. Avísame y te mando el archivo completo.")
    s = s.replace(ancla2, bloque + ancla2, 1)

viejo_group = '        by_section[(r["seccion"].strip(), r["seccion_titulo"].strip())].append(r)'
if viejo_group in s:
    s = s.replace(viejo_group, '        by_section[r["seccion"].strip()].append(r)')

viejo_loop = ('    for (num, titulo), items in sorted(by_section.items(), key=lambda kv: orden_natural(kv[0][0])):\n'
              '        out.append(f"## {num}. {titulo}")')
nuevo_loop = ('    for num, items in sorted(by_section.items(), key=lambda kv: orden_natural(kv[0])):\n'
              '        titulo = ENCABEZADOS.get(num) or f\'{num}. {items[0]["seccion_titulo"].strip()}\'\n'
              '        out.append(f"## {titulo}")')
if viejo_loop in s:
    s = s.replace(viejo_loop, nuevo_loop)
else:
    print("⚠️  No pude cambiar el bucle de secciones; revisa a mano la línea que arma '## ...'")

shutil.copy2(p, "build_index.py.bak_encabezados")
p.write_text(s, encoding="utf-8")
print("✅ Tabla ENCABEZADOS agregada (respaldo en build_index.py.bak_encabezados)")
print("   Comprueba con:  grep -c ENCABEZADOS build_index.py     (debe dar 2)")
print("   Ahora: python3 build_index.py && quarto render")