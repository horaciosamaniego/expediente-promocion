#!/usr/bin/env bash
# renombrar_papers.sh v2 — copia los PDFs de papers/ a su ruta MV- en el expediente.
#
#   ./renombrar_papers.sh            # simulación
#   ./renombrar_papers.sh --apply    # copia de verdad
#
# Usa patrones (globs), no nombres literales: así no importa si tu archivo tiene
# comillas curvas, guiones largos u otros caracteres que no se copian bien.
# Copia (no mueve) y nunca sobreescribe.

set -uo pipefail
shopt -s nullglob

SRC="${SRC:-papers}"
DST="${DST:-mv/07-investigacion/publicaciones}"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

declare -a ASIGNADOS=()

copiar() {                       # copiar <patrón> <nombre-destino>
  local d="$DST/$2"
  local -a m=()
  mapfile -t m < <(find "$SRC" -maxdepth 1 -type f -name "$1" | sort)
  if (( ${#m[@]} == 0 )); then
    printf 'FALTA       %-52s  <- ningun archivo coincide con: %s\n' "$2" "$1"; return
  fi
  if (( ${#m[@]} > 1 )); then
    printf 'AMBIGUO     %-52s  <- %d archivos coinciden con: %s\n' "$2" "${#m[@]}" "$1"; return
  fi
  ASIGNADOS+=( "${m[0]}" )
  if [[ -f "$d" ]]; then printf 'YA EXISTE   %s\n' "$2"; return; fi
  if (( APPLY )); then
    cp -p "${m[0]}" "$d" && printf 'COPIADO     %s\n' "$2"
  else
    printf 'copiaria    %s\n' "$2"
  fi
}

mkdir -p "$DST"

echo "-- 07.4.2  Capitulos de libro e informes --"
copiar 'Maturana+Samaniego*'                  'MV-07.4.2.1_maturana-2022-geografia-contemporanea.pdf'
copiar '*biodiversidad-datos-maass*'          'MV-07.4.2.2_maass-2020-cop25-datos.pdf'
copiar '*biodiversidad-restauracion-marquet*' 'MV-07.4.2.3_marquet-2020-cop25-areas.pdf'
copiar 'Samaniego et al_2020_The Topology*'   'MV-07.4.2.5_samaniego-2020-springer-topology.pdf'

echo "-- 07.4.3  Revistas WoS --"
copiar 'Li et al. - 2026 -*'                     'MV-07.4.3.1_li-2026-sust-cities.pdf'
copiar 'Br*ning-Gonz*lez et al. - 2026 -*'       'MV-07.4.3.2_bruning-2026-wrm.pdf'
copiar '*Alencar et al. - 2026 -*'               'MV-07.4.3.3_alencar-2026-cus.pdf'
copiar 'Acevedo et al. - 2026 -*'                'MV-07.4.3.4_acevedo-2026-epb.pdf'
copiar 'Castillo et al. - 2026 -*'               'MV-07.4.3.5_castillo-2026-jvp.pdf'
copiar 'Pizarro et al. - 2024 -*'                'MV-07.4.3.6_pizarro-2024-ecoinf.pdf'
copiar 'Lenormand_Samaniego_2023_*'              'MV-07.4.3.7_lenormand-2023-urbansci.pdf'
copiar 'Br*ning-Gonz*lez et al_2023_*'           'MV-07.4.3.8_bruning-2023-sustainability.pdf'
copiar 'Al* et al_2020_The macroecology*'        'MV-07.4.3.9_alo-2020-geb.pdf'
copiar 'Youn et al_2016_*'                       'MV-07.4.3.10_youn-2016-jrsi.pdf'
copiar 'Bettencourt et al_201*_Professional*'    'MV-07.4.3.11_bettencourt-2014-scirep.pdf'
copiar 'Sotomayor-G*mez_Samaniego_2020_*'        'MV-07.4.3.12_sotomayor-2020-ceus.pdf'
copiar 'Lenormand et al_2020_Entropy*'           'MV-07.4.3.13_lenormand-2020-entropy.pdf'
copiar 'Al* et al_2020_Low-cost*'                'MV-07.4.3.14_alo-2020-ijse.pdf'
copiar 'Ortega-Sol*s et al_2020_*'               'MV-07.4.3.15_ortega-2020-iforest.pdf'
copiar 'Al* et al_2019_Otolith*'                 'MV-07.4.3.16_alo-2019-peerj.pdf'
copiar 'Dannemann et al_2018_*'                  'MV-07.4.3.17_dannemann-2018-rsos.pdf'
copiar 'Castillo et al_2018_Change of niche*'    'MV-07.4.3.18_castillo-2018-peerj.pdf'
copiar 'Molina et al. - 2018 -*'                 'MV-07.4.3.19_molina-2018-gayana.pdf'
copiar 'Gonz*lez et al. - 2013 - Unveiling*'     'MV-07.4.3.20_gonzalez-2013-plosone.pdf'
copiar 'Correa et al. - 2013 -*'                 'MV-07.4.3.21_correa-2013-behavproc.pdf'
copiar 'Samaniego and Marquet - 2013 -*'         'MV-07.4.3.22_samaniego-2013-theorecol.pdf'
copiar 'Silva et al. - 2012 -*'                  'MV-07.4.3.23_silva-2012-plosone.pdf'
copiar 'Population Ecology - 201*'               'MV-07.4.3.24_samaniego-2012-popecol.pdf'

echo "-- 07.4.4  Scopus --"
copiar 'Aburto_Samaniego_2020_*'                 'MV-07.4.4.1_seguel-2020-cuadgeo.pdf'

echo "-- 07.4.6  Otras con comite editorial --"
copiar 'Mu*oz Vel*squez et al_2019_*'            'MV-07.4.6.1_munoz-2019-ctv.pdf'
copiar 'Henr*quez et al_2017_*'                  'MV-07.4.6.2_henriquez-2017-invgeo.pdf'

echo
echo "-- Archivos en $SRC/ sin destino asignado --"
n=0
for f in "$SRC"/*; do
  hit=0
  for a in "${ASIGNADOS[@]}"; do [[ "$f" == "$a" ]] && { hit=1; break; }; done
  (( hit )) || { printf '  %s\n' "$(basename "$f")"; n=$((n+1)); }
done
(( n == 0 )) && echo "  (ninguno)"

exit 0
