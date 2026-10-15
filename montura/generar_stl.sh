#!/usr/bin/env bash
# Regenera todos los STL desde montura.scad (requiere OpenSCAD en el PATH).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stl
piezas=(base_fija soporte_motor_azimut plato_giratorio zocalo_brazo cabezal_altitud
        polea_altitud soporte_motor_altitud montura_vixen barra_vixen
        caja_control tapa_caja panel_energia tapa_panel prueba_gt2)
for p in "${piezas[@]}"; do
  echo "→ $p"
  openscad -q -D "pieza=\"$p\"" -o "stl/$p.stl" montura.scad
done
echo "Listo: ${#piezas[@]} piezas en stl/"
