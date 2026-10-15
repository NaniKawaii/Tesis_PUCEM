// =============================================================================
//  Montura altacimutal de un brazo · piezas imprimibles en 3D (PETG)
//  Tesis PUCEM · Sistema de posicionamiento telescópico con IA y control web
//
//  Uso:
//    - Abrir en OpenSCAD (gratis, openscad.org) y elegir la pieza en `pieza`.
//    - O desde la terminal:  openscad -D 'pieza="polea_altitud"' -o polea.stl montura.scad
//    - `pieza = "ensamble"` muestra el conjunto completo (no imprimible).
//
//  Todas las medidas están en milímetros. Las medidas marcadas con (MEDIR)
//  dependen de lo que compres: verifícalas con un calibrador antes de imprimir.
//
//  Perfil de diente GT2 basado en "Parametric Pulley" de droftarts
//  (Thingiverse 16627, licencia CC BY-SA 3.0).
// =============================================================================

pieza = "ensamble";  // ["ensamble", "base_fija", "soporte_motor_azimut", "plato_giratorio", "zocalo_brazo", "cabezal_altitud", "polea_altitud", "soporte_motor_altitud", "montura_vixen", "barra_vixen", "caja_control", "tapa_caja", "panel_energia", "tapa_panel", "prueba_gt2"]

$fn = 72;
detalle = true;   // false = sin agujeros del tablero (más rápido para revisar interferencias)
e = 0.01;  // épsilon para que las restas no dejen caras fantasma

// --------------------------------------------------------------- Holguras
holgura_agujero = 0.3;   // agujeros para tornillos y ejes

// --------------------------------------------------------------- Compras (MEDIR)
// Motor NEMA 23 (JK57HS76)
nema_lado        = 56.4;
nema_entre_ag    = 47.14;          // distancia entre agujeros de la brida
nema_resalte_d   = 38.1 + 0.6;     // resalte central de la brida
nema_resalte_h   = 1.6;
nema_largo       = 76;
nema_eje_largo   = 21;             // (MEDIR) largo del eje desde la brida
// Polea GT2 de 20 dientes comprada (agujero 8 mm, correa 6 mm)
polea20_largo    = 16;             // (MEDIR) largo total
polea20_cubo     = 7;              // (MEDIR) largo del cubo con prisioneros
// Rodamiento 608ZZ y eje de altitud
rod_d            = 22 + 0.15;
rod_h            = 7;
eje_d            = 8;
// Perfil de aluminio 2040
perfil_x         = 40;
perfil_y         = 20;
perfil_ajuste    = 0.4;
perfil_largo     = 300;            // 300 mm para tubos de hasta ~40 cm; ver tabla en LEEME.md
// Rodamiento giratorio "lazy susan" de 4" (≈ 102 mm, cuadrado)
lazy_lado        = 102;            // (MEDIR)
lazy_alto        = 8;              // (MEDIR) alto total del rodamiento
// Tuerca hexagonal 5/8"-11 UNC (rosca del trípode de topografía)
tuerca58_ac      = 23.81 + 0.5;    // entre caras (15/16")
tuerca58_alto    = 13.9 + 0.5;
// Tornillería
m5               = 5 + holgura_agujero;
m5_cabeza_d      = 9.5;
m5_tuerca_ac     = 8 + 0.4;
m3               = 3 + 0.2;
m3_tuerca_ac     = 5.5 + 0.3;
m3_tuerca_h      = 2.6;
w14              = 6.35 + holgura_agujero;   // tornillo 1/4"-20 del pie del telescopio
w14_cabeza_d     = 11;

// --------------------------------------------------------------- Transmisión
dientes_corona_az   = 280;   // corona del plato giratorio → 280/20 = 14:1
dientes_polea_alt   = 100;   // polea de altitud           → 100/20 = 5:1
ancho_correa        = 6;

// Distancia entre ejes del motor de azimut al centro (ajustable con ranuras)
c_az_min = 116;
c_az_max = 133;

// --------------------------------------------------------------- GT2
// Diámetro exterior de una polea GT2 de n dientes (paso 2 mm)
function gt2_d_ext(n) = 2 * (n * 2 / (2 * PI) - 0.254);

module diente_gt2() {
    polygon([[0.747183,-0.5],[0.747183,0],[0.647876,0.037218],[0.598311,0.130528],
             [0.578556,0.238423],[0.547158,0.343077],[0.504649,0.443762],[0.451556,0.53975],
             [0.358229,0.636924],[0.2484,0.707276],[0.127259,0.750044],[0,0.76447],
             [-0.127259,0.750044],[-0.2484,0.707276],[-0.358229,0.636924],[-0.451556,0.53975],
             [-0.504649,0.443762],[-0.547158,0.343077],[-0.578556,0.238423],[-0.598311,0.130528],
             [-0.647876,0.037218],[-0.747183,0],[-0.747183,-0.5]]);
}

// Silueta 2D de una polea GT2 de n dientes
module perfil_gt2(n) {
    d = gt2_d_ext(n);
    ancho = 1.494; extra = 0.2;
    dist = sqrt(pow(d / 2, 2) - pow((ancho + extra) / 2, 2));
    difference() {
        circle(d = d, $fn = n * 4);
        for (i = [0 : n - 1])
            rotate(i * 360 / n) translate([0, -dist]) scale([(ancho + extra) / ancho, 1]) diente_gt2();
    }
}

// --------------------------------------------------------------- Utilidades
module ranura(largo, d, h) {  // agujero alargado a lo largo de X, centrado en el origen
    hull() for (x = [-largo / 2, largo / 2]) translate([x, 0, 0]) cylinder(d = d, h = h);
}

module hexagono(ac, h) { cylinder(d = ac / cos(30), h = h, $fn = 6); }

module patron_nema() {  // centros de los 4 agujeros de la brida
    for (x = [-1, 1], y = [-1, 1]) translate([x * nema_entre_ag / 2, y * nema_entre_ag / 2, 0]) children();
}

// Agujero radial para prisionero M3 con tuerca cautiva (en un cubo de diámetro cubo_d)
module prisionero_m3(cubo_d, z) {
    translate([0, 0, z]) rotate([-90, 0, 0]) {
        cylinder(d = m3, h = cubo_d);
        translate([0, 0, eje_d / 2 + 2]) rotate([0, 0, 30])
            hull() { hexagono(m3_tuerca_ac, m3_tuerca_h); translate([0, 20, 0]) hexagono(m3_tuerca_ac, m3_tuerca_h); }
    }
}

// ============================================================================
//  1. BASE FIJA (se atornilla al trípode con la tuerca 5/8")
//     Origen: centro, cara superior en z = 0.
// ============================================================================
base_d = 160;
base_h = 10;
base_cubo_d = 45;
base_cubo_h = 12;   // bajo la placa
agujeros_soporte_az = [[52, 0], [70, 18], [70, -18]];
agujeros_caja = [for (p = agujeros_soporte_az) [-p[0], p[1]]];   // caja de control, lado −X

module base_fija() {
    difference() {
        union() {
            translate([0, 0, -base_h]) cylinder(d = base_d, h = base_h, $fn = 180);
            translate([0, 0, -base_h - base_cubo_h]) cylinder(d = base_cubo_d, h = base_cubo_h);
        }
        // tuerca 5/8" insertada desde arriba; el tornillo del trípode entra por abajo
        translate([0, 0, -tuerca58_alto + e]) hexagono(tuerca58_ac, tuerca58_alto);
        translate([0, 0, -50]) cylinder(d = 16.5, h = 60);
        // paso de cables
        translate([0, 30, -50]) cylinder(d = 14, h = 60);
        // tornillos del soporte del motor de azimut (cabeza embutida arriba)
        // tornillos del soporte del motor (+X) y de la caja de control (−X), cabeza embutida arriba
        for (p = concat(agujeros_soporte_az, agujeros_caja)) translate([p[0], p[1], 0]) {
            translate([0, 0, -50]) cylinder(d = m5, h = 60);
            translate([0, 0, -5.5]) cylinder(d = m5_cabeza_d, h = 6);
        }
    }
}

// ============================================================================
//  2. SOPORTE DEL MOTOR DE AZIMUT (cuelga bajo la base, motor con eje hacia arriba)
// ============================================================================
saz_ancho = nema_lado + 16;
saz_x_fin = c_az_max + nema_lado / 2 + 8;
saz_placa_h = 6;

module soporte_motor_azimut() {
    difference() {
        union() {
            // lengüeta bajo la base fija
            translate([44, -saz_ancho / 2, -base_h - 6]) cube([base_d / 2 - 44 + 0.5, saz_ancho, 6]);
            // escalón
            translate([base_d / 2 + 0.5, -saz_ancho / 2, -base_h - 6]) cube([5.5, saz_ancho, base_h + 6]);
            // placa del motor, a ras con la cara superior de la base
            translate([base_d / 2 + 0.5, -saz_ancho / 2, -saz_placa_h]) cube([saz_x_fin - base_d / 2 - 0.5, saz_ancho, saz_placa_h]);
            // nervios de refuerzo (arriba quedan por debajo de la correa; abajo, fuera de la brida)
            for (s = [-1, 1]) {
                y = s > 0 ? saz_ancho / 2 - 6 : -saz_ancho / 2;
                // arriba: empiezan fuera del alcance de la corona (r > 95 mm)
                translate([95, s > 0 ? saz_ancho / 2 - 5 : -saz_ancho / 2, 0]) cube([saz_x_fin - 95, 5, 5]);
                // abajo: bajo la lengüeta y unidos a la placa del motor
                translate([44, y, -base_h - 22]) cube([base_d / 2 + 6 - 44, 6, 16]);
                translate([base_d / 2 + 0.5, y, -base_h - 22]) cube([saz_x_fin - base_d / 2 - 0.5, 6, base_h + 22 - saz_placa_h + e]);
            }
        }
        // tornillos hacia la base fija, con tuerca embutida abajo
        for (p = agujeros_soporte_az) translate([p[0], p[1], -40]) {
            cylinder(d = m5, h = 60);
            translate([0, 0, 40 - base_h - 6 - 30 - e]) hexagono(m5_tuerca_ac, 30 - 2);
        }
        // ranuras del motor para ajustar la tensión de la correa
        c_med = (c_az_min + c_az_max) / 2;
        c_rec = c_az_max - c_az_min;
        translate([c_med, 0, -20]) ranura(c_rec, 10, 40);                                   // eje
        translate([c_med, 0, -saz_placa_h - e]) ranura(c_rec, nema_resalte_d, nema_resalte_h + e);  // resalte
        translate([c_med, 0, -20]) patron_nema() ranura(c_rec, m5, 40);
    }
}

// ============================================================================
//  3. PLATO GIRATORIO con corona GT2 de 280 dientes (azimut 14:1)
//     Origen: centro, cara superior de la base fija en z = 0.
//     Imprimir BOCA ABAJO (la cara superior sobre la cama).
// ============================================================================
corona_d = gt2_d_ext(dientes_corona_az);
plato_z0 = 3;                  // borde inferior de la corona (3 mm sobre la base)
plato_disco_z = lazy_alto;     // el disco apoya sobre el lazy susan
plato_top = lazy_alto + 9.5;
plato_pared = 4;
brazo_y = 40;                  // posición del brazo (perfil 2040) sobre el plato
zocalo_h = 25;
zocalo_pared = 6;
zocalo_ala = 10;   // ala de la base con los 4 tornillos
zocalo_ext_x = perfil_x + perfil_ajuste + 2 * (zocalo_pared + zocalo_ala);
zocalo_ext_y = perfil_y + perfil_ajuste + 2 * (zocalo_pared + zocalo_ala);
zocalo_agujeros = [for (sx = [-1, 1], sy = [-1, 1]) [sx * (zocalo_ext_x / 2 - 5.5), sy * (zocalo_ext_y / 2 - 5.5)]];

module plato_giratorio() {
    r_int = corona_d / 2 - 0.8 - plato_pared;
    difference() {
        union() {
            // corona dentada (aro + disco)
            translate([0, 0, plato_z0]) linear_extrude(plato_top - 1.5 - plato_z0) perfil_gt2(dientes_corona_az);
            // ala superior que guía la correa
            translate([0, 0, plato_top - 1.5]) cylinder(d = corona_d + 3, h = 1.5, $fn = 360);
            // ala inferior achaflanada (45°, imprimible boca abajo)
            translate([0, 0, plato_z0]) cylinder(d1 = corona_d + 3, d2 = corona_d - 1.6, h = 2.3, $fn = 360);
        }
        // hueco para el lazy susan
        translate([0, 0, plato_z0 - e]) cylinder(r = r_int, h = plato_disco_z - plato_z0 + e, $fn = 180);
        // paso de cables
        translate([0, 0, -1]) cylinder(d = 25, h = 50);
        // 4 tornillos M5 del zócalo, con la tuerca embutida por debajo del disco
        for (p = zocalo_agujeros) translate([p[0], brazo_y + p[1], 0]) {
            cylinder(d = m5, h = 40);
            translate([0, 0, plato_disco_z - e]) hexagono(m5_tuerca_ac, 4.5);
        }
        // 2 tornillos M5 desde abajo a los agujeros centrales del perfil (roscar con macho M5)
        for (x = [-10, 10]) translate([x, brazo_y, 0]) {
            cylinder(d = m5, h = 40);
            translate([0, 0, plato_disco_z - e]) cylinder(d = m5_cabeza_d, h = 5);
        }
    }
}

// ============================================================================
//  3b. ZÓCALO DEL BRAZO (sujeta el pie del perfil 2040 sobre el plato giratorio)
//      Origen: cara del plato en z = 0. Imprimir así.
// ============================================================================
module zocalo_brazo() {
    px = perfil_x + perfil_ajuste; py = perfil_y + perfil_ajuste;
    difference() {
        union() {
            translate([-zocalo_ext_x / 2, -zocalo_ext_y / 2, 0]) cube([zocalo_ext_x, zocalo_ext_y, 5]);
            hull() {
                translate([-px / 2 - zocalo_pared - 4, -py / 2 - zocalo_pared - 4, 0]) cube([px + 2 * zocalo_pared + 8, py + 2 * zocalo_pared + 8, 5]);
                translate([-px / 2 - zocalo_pared, -py / 2 - zocalo_pared, 0]) cube([px + 2 * zocalo_pared, py + 2 * zocalo_pared, zocalo_h]);
            }
        }
        translate([-px / 2, -py / 2, -1]) cube([px, py, zocalo_h + 2]);
        for (p = zocalo_agujeros) translate([p[0], p[1], -1]) cylinder(d = m5, h = 10);
        // tornillos laterales a tuercas en T del perfil
        for (x = [-10, 10]) translate([x, -30, zocalo_h - 9]) rotate([-90, 0, 0]) cylinder(d = m5, h = 60);
    }
}

// ============================================================================
//  4. CABEZAL DE ALTITUD (se encaja arriba del perfil 2040; 2 × 608ZZ)
//     Origen: tope del perfil en z = 0, centrado en el perfil. Eje a lo largo de Y.
//     Imprimir de costado (cara Y sobre la cama).
// ============================================================================
cab_funda = 30;                     // profundidad que abraza al perfil
cab_pared = 4;
cab_x = perfil_x + perfil_ajuste + 2 * cab_pared;
cab_y = 40;                         // distancia exterior entre caras de los rodamientos
cab_eje_z = 17;                     // altura del eje sobre el tope del perfil
cab_alto = cab_eje_z + rod_d / 2 + 6;

module cabezal_altitud() {
    difference() {
        union() {
            translate([-cab_x / 2, -(perfil_y + perfil_ajuste) / 2 - cab_pared, -cab_funda]) cube([cab_x, perfil_y + perfil_ajuste + 2 * cab_pared, cab_funda]);
            hull() {
                translate([-cab_x / 2, -cab_y / 2, 0]) cube([cab_x, cab_y, 1]);
                translate([0, -cab_y / 2, cab_eje_z]) rotate([-90, 0, 0]) cylinder(d = rod_d + 12, h = cab_y);
                translate([-cab_x / 2, -cab_y / 2, cab_eje_z - 5]) cube([cab_x, cab_y, 10]);
            }
        }
        // funda del perfil
        translate([-(perfil_x + perfil_ajuste) / 2, -(perfil_y + perfil_ajuste) / 2, -cab_funda - e]) cube([perfil_x + perfil_ajuste, perfil_y + perfil_ajuste, cab_funda + e]);
        // eje y rodamientos
        translate([0, -cab_y, cab_eje_z]) rotate([-90, 0, 0]) cylinder(d = eje_d + 1, h = 2 * cab_y);
        for (s = [-1, 1]) translate([0, s * (cab_y / 2 - rod_h / 2 + e), cab_eje_z]) rotate([90, 0, 0]) cylinder(d = rod_d, h = rod_h + e, center = true);
        // 2 tornillos M5 verticales a los agujeros centrales del perfil (roscar con macho M5)
        for (x = [-10, 10]) translate([x, 0, -5]) {
            cylinder(d = m5, h = 60);
            translate([0, 0, cab_alto - 2]) cylinder(d = m5_cabeza_d, h = 20);
        }
        // tornillos laterales a tuercas en T
        for (x = [-10, 10]) translate([x, -30, -cab_funda / 2]) rotate([-90, 0, 0]) cylinder(d = m5, h = 60);
    }
}

// ============================================================================
//  5. POLEA DE ALTITUD GT2 de 100 dientes (5:1), agujero 8 mm, 2 prisioneros M3
//     Origen: cara de la ala inferior en z = 0. Imprimir así (ala sobre la cama).
// ============================================================================
polea_d = gt2_d_ext(dientes_polea_alt);
polea_ala = 1.5;
polea_dientes_h = ancho_correa + 2;
polea_cubo_d = 24;
polea_cubo_h = 10;
polea_alto = polea_ala + polea_dientes_h + 3.6 + polea_cubo_h;

module polea_altitud() {
    difference() {
        union() {
            cylinder(d = polea_d + 4, h = polea_ala);
            translate([0, 0, polea_ala]) linear_extrude(polea_dientes_h) perfil_gt2(dientes_polea_alt);
            translate([0, 0, polea_ala + polea_dientes_h]) {
                cylinder(d1 = polea_d - 1.6, d2 = polea_d + 4, h = 2.8);
                translate([0, 0, 2.8]) cylinder(d = polea_d + 4, h = 0.8);
            }
            translate([0, 0, polea_alto - polea_cubo_h - e]) cylinder(d = polea_cubo_d, h = polea_cubo_h + e);
        }
        translate([0, 0, -1]) cylinder(d = eje_d + 0.25, h = polea_alto + 2);
        for (a = [0, 90]) rotate(a) prisionero_m3(polea_cubo_d, polea_alto - polea_cubo_h / 2);
        // agujeros M3 cada 15° para el tornillo-leva de los fines de carrera
        for (a = [0 : 15 : 345]) rotate(a) translate([polea_d / 2 - 5, 0, -1]) cylinder(d = 2.8, h = polea_alto - polea_cubo_h + 1);
    }
}

// ============================================================================
//  6. SOPORTE DEL MOTOR DE ALTITUD (se atornilla a la cara +Y del perfil 2040)
//     Origen: cara del perfil en y = 0, centro del motor en x = z = 0.
//     La tensión de la correa se ajusta deslizando el soporte por el perfil.
// ============================================================================
salt_ancho = nema_lado + 16;
salt_respaldo = 6;
salt_placa = 6;
// Alineación: centro de los dientes de la polea de altitud respecto de la cara del perfil
polea_alt_centro_y = (cab_y / 2 - perfil_y / 2) + 0.5 + polea_cubo_h + 3.6 + polea_dientes_h / 2;
// La polea de 20T se monta con el cubo hacia la placa del motor
salt_placa_y = polea_alt_centro_y + 0.5 + polea20_cubo + (polea20_largo - polea20_cubo) / 2;

module soporte_motor_altitud() {
    z0 = -40; z1 = 36;
    z1_respaldo = 20;  // el respaldo queda bajo la funda del cabezal aun con la correa de 280 mm
    difference() {
        union() {
            translate([-salt_ancho / 2, 0, z0]) cube([salt_ancho, salt_respaldo, z1_respaldo - z0]);
            for (s = [-1, 1]) translate([s > 0 ? salt_ancho / 2 - 6 : -salt_ancho / 2, 0, z0]) cube([6, salt_placa_y, z1 - z0]);
            translate([-salt_ancho / 2, salt_placa_y, z0]) cube([salt_ancho, salt_placa, z1 - z0]);
        }
        // tornillos al perfil (ranuras de las caras de 40 mm en x = ±10)
        for (x = [-10, 10], z = [-28, 10]) translate([x, -1, z]) rotate([-90, 0, 0]) {
            cylinder(d = m5, h = 20);
            translate([0, 0, salt_respaldo + 1 - e]) cylinder(d = m5_cabeza_d, h = 30);
        }
        // motor
        translate([0, salt_placa_y - 1, 0]) rotate([-90, 0, 0]) cylinder(d = 10, h = 20);
        translate([0, salt_placa_y + salt_placa - nema_resalte_h, 0]) rotate([-90, 0, 0]) cylinder(d = nema_resalte_d, h = 5);
        translate([0, salt_placa_y - 1, 0]) rotate([-90, 0, 0]) patron_nema() cylinder(d = m5, h = 20);
    }
}

// ============================================================================
//  7. MONTURA COLA DE MILANO VIXEN (va al eje de altitud, del lado opuesto a la polea)
//     Interfaz estándar: sirve para cualquier telescopio liviano con barra tipo
//     Vixen (o con anillas/pie de 1/4" sobre la barra impresa de la pieza 8).
//     Origen: centro, puntas de las mordazas en z = 0, cubo hacia +Z.
//     Imprimir así (mordazas sobre la cama, cubo hacia arriba).
// ============================================================================
vx_base   = 44 + 0.6;     // (MEDIR) ancho mayor de la barra Vixen + holgura
vx_flanco = atan(4.5 / 15);  // inclinación de los flancos (44 → 35 mm en 15 mm de alto)
vx_mordaza_h = 13;        // menor que el alto de la barra (15 mm)
vx_largo  = 100;
vx_fija   = 10;           // espesor de la mordaza fija
vx_movil  = 14;           // mordaza con 2 tornillos M5 de apriete
vx_placa  = 10;
vx_ancho  = vx_base + vx_fija + vx_movil;
vx_cubo_d = 26;
vx_cubo_h = 15;
vx_alto   = vx_mordaza_h + vx_placa + vx_cubo_h;

module montura_vixen() {
    abre = vx_mordaza_h * tan(vx_flanco);        // cuánto se cierra el canal hacia las puntas
    y0 = -vx_base / 2 - vx_fija;                 // borde exterior de la mordaza fija
    difference() {
        union() {
            translate([-vx_largo / 2, y0, 0]) cube([vx_largo, vx_ancho, vx_mordaza_h + vx_placa]);
            translate([0, 0, vx_mordaza_h + vx_placa - e]) cylinder(d = vx_cubo_d, h = vx_cubo_h + e);
        }
        // canal en cola de milano (ancho vx_base contra la placa, más angosto en las puntas)
        rotate([90, 0, 90]) translate([0, 0, -vx_largo / 2 - 1]) linear_extrude(vx_largo + 2)
            polygon([[-vx_base / 2 + abre, -e], [vx_base / 2 - abre, -e], [vx_base / 2, vx_mordaza_h], [-vx_base / 2, vx_mordaza_h]]);
        // eje de altitud (no debe sobresalir dentro del canal)
        translate([0, 0, vx_mordaza_h + 1]) cylinder(d = eje_d + 0.25, h = 50);
        for (a = [0, 90]) rotate(a + 45) prisionero_m3(vx_cubo_d, vx_alto - vx_cubo_h / 2);
        // 2 tornillos M5 de apriete en la mordaza móvil, con tuerca cautiva
        for (x = [-vx_largo / 4, vx_largo / 4]) translate([x, vx_base / 2 - 2, vx_mordaza_h / 2]) rotate([-90, 0, 0]) {
            cylinder(d = m5, h = vx_movil + 5);
            translate([0, 0, 6]) rotate([0, 0, 30]) hull() { hexagono(m5_tuerca_ac, 4.2); translate([0, -20, 0]) hexagono(m5_tuerca_ac, 4.2); }
        }
    }
}

// ============================================================================
//  8. BARRA COLA DE MILANO VIXEN impresa (para telescopios con pie de 1/4"-20
//     o con anillas). Ranura central para tornillos de 1/4"-20 o M6.
//     Origen: cara ancha (lado de la montura) en z = 0. Imprimir así.
// ============================================================================
barra_largo = 200;
barra_alto  = 15;
barra_sup   = 35;

module barra_vixen() {
    difference() {
        rotate([90, 0, 90]) translate([0, 0, -barra_largo / 2]) linear_extrude(barra_largo)
            polygon([[-44 / 2, 0], [44 / 2, 0], [barra_sup / 2, barra_alto], [-barra_sup / 2, barra_alto]]);
        // ranura para los tornillos del telescopio, con las cabezas embutidas del lado de la montura
        translate([0, 0, -1]) ranura(barra_largo - 40, w14 + 0.3, barra_alto + 2);
        translate([0, 0, -1]) ranura(barra_largo - 40, 12.5, 6.5 + 1);
        // topes de seguridad: un tornillo M5 en cada extremo evita que la barra se salga
        for (x = [-1, 1]) translate([x * (barra_largo / 2 - 9), 0, -1]) cylinder(d = 4.2, h = barra_alto + 2);
    }
}

// ============================================================================
//  10. CAJA DE CONTROL (Raspberry Pi 4, 2 × TB6600, step-down, GPS y GY-91)
//      Va fija a la base, del lado opuesto al motor de azimut (−X, hacia el sur):
//      no gira con la montura, así que sus cables no se enredan. El GY-91 queda
//      solidario con la base (mide la nivelación) y el GPS recibe señal a través
//      de la tapa de PETG.
//      Coordenadas locales: u = hacia afuera (0 = pared junto a la base),
//      v = a lo ancho, z = altura (0 = fondo). Imprimir con el fondo sobre la cama.
// ============================================================================
caja_r0    = 95;      // distancia del eje de azimut a la pared interior (libra la corona: r = 90,4)
caja_prof  = 140;     // hacia afuera
caja_ancho = 200;
caja_alto  = 60;      // sin la tapa
caja_z0    = -20;     // fondo de la caja respecto de la cara superior de la base (sobre el trípode)
caja_pared = 3;
caja_piso  = 3;
pg7        = 12.7;    // agujero para prensaestopas PG7 (cables de 3–6,5 mm)
// Ubicación sugerida de las placas (u, v de la esquina; largo en u, ancho en v)
rpi        = [48, 33, 85, 56];            // Raspberry Pi 4: agujeros 58 × 49 mm, M2.5
tb6600_a   = [40, -97, 96, 56];           // (MEDIR) tamaño de tu TB6600 (≈ 96 × 56 × 33 mm)
tb6600_b   = [40, -38, 96, 56];

module caja_control() {
    W = caja_ancho; P = caja_prof; H = caja_alto; t = caja_pared;
    difference() {
        union() {
            translate([0, -W / 2, 0]) cube([P, W, H]);
            // lengüeta maciza bajo la base fija (3 tornillos M5, como el soporte del motor);
            // llega hasta el piso para imprimirse sin soportes
            translate([-(caja_r0 - 44), -36, 0]) cube([caja_r0 - 44 + t, 72, -caja_z0 - base_h]);
        }
        // interior
        translate([t, -W / 2 + t, caja_piso]) cube([P - 2 * t, W - 2 * t, H]);
        // tornillos hacia la base (cabeza arriba en la base, tuerca abajo)
        for (p = agujeros_caja) translate([-(-p[0] - caja_r0), p[1], -1]) {
            cylinder(d = m5, h = 50);
            hexagono(m5_tuerca_ac, 1 + 5);   // tuerca embutida por debajo
        }
        // prensaestopas: 4 en la pared junto a la base (motores, AS5600, fines de carrera)
        // y 1 en la pared exterior (alimentación desde el panel de energía)
        for (v = [-66, -22, 22, 66]) translate([-1, v, 14]) rotate([0, 90, 0]) cylinder(d = pg7, h = t + 2);
        translate([P - t - 1, 0, 14]) rotate([0, 90, 0]) cylinder(d = pg7, h = t + 2);
        // ventilación en los costados (zona de los TB6600 y de la Raspberry Pi)
        for (s = [-1, 1], u = [45 : 12 : 129]) translate([u, s * W / 2 - 5, 22]) cube([4, 10, 28]);
        // tablero perforado del piso: agujeros de 2,8 mm cada 10 mm para fijar las placas
        // con tornillos autorroscantes M3 (sirve para cualquier medida de TB6600 o step-down)
        if (detalle) for (u = [10 : 10 : P - 10], v = [-W / 2 + 10 : 10 : W / 2 - 10])
            if (!(u > rpi[0] - 2 && u < rpi[0] + rpi[2] + 2 && v > rpi[1] - 2 && v < rpi[1] + rpi[3] + 2))
                translate([u, v, -1]) cylinder(d = 2.8, h = caja_piso + 2, $fn = 12);
    }
    // postes para la Raspberry Pi (M2.5 autorroscante)
    for (du = [3.5, 61.5], dv = [3.5, 52.5]) translate([rpi[0] + du, rpi[1] + dv, caja_piso - e])
        difference() { cylinder(d = 6.5, h = 6); cylinder(d = 2.2, h = 7); }
    // columnas de las esquinas para los tornillos de la tapa (M3 autorroscante)
    for (u = [t, P - t - 8], v = [-W / 2 + t, W / 2 - t - 8]) translate([u, v, caja_piso - e])
        difference() { cube([8, 8, H - caja_piso + e]); translate([4, 4, H - caja_piso - 14]) cylinder(d = 2.8, h = 15); }
}

// Vista del interior con las placas ubicadas (referencia, no se imprime)
module placa(pos, alto, col, etiqueta, tam = 5) {
    color(col) translate([pos[0], pos[1], caja_piso]) cube([pos[2], pos[3], alto]);
    color("white") translate([pos[0] + pos[2] / 2, pos[1] + pos[3] / 2, caja_piso + alto]) linear_extrude(0.6)
        rotate(pos[3] > pos[2] ? 90 : 0) text(etiqueta, size = tam, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
}
module caja_vista() {
    color("#aeb6bf") caja_control();
    color("#1e8449") for (du = [3.5, 61.5], dv = [3.5, 52.5]) translate([rpi[0] + du, rpi[1] + dv, caja_piso]) cylinder(d = 6.5, h = 6);
    translate([0, 0, 6]) placa(rpi, 16, "#1e8449", "Raspberry Pi 4");
    placa(tb6600_a, 33, "#2471a3", "TB6600 azimut");
    placa(tb6600_b, 33, "#2471a3", "TB6600 altitud");
    placa([8, -95, 24, 54], 18, "#b9770e", "Step-down", 4);
    placa([8, -30, 24, 40], 14, "#7f8c8d", "Borneras", 4);
    placa([10, 18, 20, 16], 4, "#117a65", "GY-91", 3.5);
    placa([5, 48, 30, 38], 8, "#7d3c98", "GPS", 6);
}

module tapa_caja() {
    W = caja_ancho; P = caja_prof; t = caja_pared;
    difference() {
        union() {
            translate([0, -W / 2, 0]) cube([P, W, 3]);
            // reborde que encaja dentro de la caja
            difference() {
                translate([t + 0.4, -W / 2 + t + 0.4, -2]) cube([P - 2 * t - 0.8, W - 2 * t - 0.8, 2 + e]);
                translate([t + 2.4, -W / 2 + t + 2.4, -3]) cube([P - 2 * t - 4.8, W - 2 * t - 4.8, 4]);
                for (u = [t, P - t - 8], v = [-W / 2 + t, W / 2 - t - 8]) translate([u - 1, v - 1, -3]) cube([10, 10, 4]);
            }
        }
        for (u = [t + 4, P - t - 4], v = [-W / 2 + t + 4, W / 2 - t - 4]) translate([u, v, -5]) {
            cylinder(d = 3.4, h = 10);
            translate([0, 0, 5 + 3 - 1.8]) cylinder(d1 = 3.4, d2 = 6.6, h = 1.8 + e);
        }
        // hueco para pegar la antena cerámica del GPS por debajo (25 × 25 mm)
        translate([rpi[0] + 30 - 13.5, -60 - 13.5, -1]) cube([27, 27, 2]);
        // flecha "N": la montura se orienta con esta flecha (y el motor de azimut) hacia el norte
        translate([20, 0, 3 - 1]) linear_extrude(1.5) {
            polygon([[-14, 0], [0, 9], [0, 4], [14, 4], [14, -4], [0, -4], [0, -9]]);
            translate([-30, 0]) rotate(90) text("N", size = 12, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
        }
    }
}

// ============================================================================
//  11. PANEL DE ENERGÍA (va junto a la batería, colgado de una pata del trípode)
//      Frente: paro de emergencia, interruptor general y voltímetro.
//      El fusible va en línea, dentro, junto al borne positivo.
//      Imprimir con el frente sobre la cama; la tapa trasera tiene ranuras para
//      una correa de velcro.
// ============================================================================
panel = [120, 80, 60];               // ancho, alto, profundidad
paro_d = 22.5;                        // pulsador de 22 mm (estándar)
interruptor = [19.2, 12.9];           // (MEDIR) basculante KCD1 típico
voltimetro = [45.5, 26.5];            // (MEDIR) voltímetro de panel de 0,56"

module panel_energia() {
    A = panel[0]; B = panel[1]; D = panel[2]; t = 3;
    difference() {
        translate([-A / 2, -B / 2, 0]) cube([A, B, D]);
        translate([-A / 2 + t, -B / 2 + t, t]) cube([A - 2 * t, B - 2 * t, D]);
        translate([-30, 8, -1]) cylinder(d = paro_d, h = t + 2);
        translate([18, 18, -1]) translate([-interruptor[0] / 2, -interruptor[1] / 2, 0]) cube([interruptor[0], interruptor[1], t + 2]);
        translate([18, -14, -1]) translate([-voltimetro[0] / 2, -voltimetro[1] / 2, 0]) cube([voltimetro[0], voltimetro[1], t + 2]);
        // prensaestopas abajo: entrada de la batería y salidas (12 V lógica, 12 V motores)
        for (x = [-35, 0, 35]) translate([x, -B / 2 - 1, D / 2]) rotate([-90, 0, 0]) cylinder(d = pg7, h = t + 2);
    }
    for (x = [-A / 2 + t, A / 2 - t - 8], y = [-B / 2 + t, B / 2 - t - 8]) translate([x, y, t - e])
        difference() { cube([8, 8, D - t + e]); translate([4, 4, D - t - 14]) cylinder(d = 2.8, h = 15); }
}

module tapa_panel() {
    A = panel[0]; B = panel[1]; t = 3;
    difference() {
        translate([-A / 2, -B / 2, 0]) cube([A, B, 4]);
        for (x = [-A / 2 + t + 4, A / 2 - t - 4], y = [-B / 2 + t + 4, B / 2 - t - 4]) translate([x, y, -1]) cylinder(d = 3.4, h = 6);
        // ranuras para la correa de velcro (25 mm)
        for (x = [-30, 30]) translate([x - 2.5, -14, -1]) cube([5, 28, 6]);
    }
}

// ============================================================================
//  9. PIEZA DE PRUEBA: imprimir primero para comprobar que la correa engrana
// ============================================================================
module prueba_gt2() {
    difference() {
        linear_extrude(5) perfil_gt2(dientes_polea_alt);
        translate([0, 0, -1]) cylinder(d = polea_d - 12, h = 10);
    }
    // segmento de la corona de 280 dientes (con el borde dentado hacia +Y)
    translate([polea_d / 2 + 35, 0, 0]) intersection() {
        translate([0, -corona_d / 2 + 10, 0]) linear_extrude(5) perfil_gt2(dientes_corona_az);
        translate([-25, -10, -1]) cube([50, 22, 7]);
    }
}

// ============================================================================
//  ENSAMBLE (vista de referencia; motores, perfil, tubo y lazy susan simplificados)
// ============================================================================
module motor_nema() {
    color("#4a5563") translate([-nema_lado / 2, -nema_lado / 2, -nema_largo]) cube([nema_lado, nema_lado, nema_largo]);
    color("silver") cylinder(d = eje_d, h = nema_eje_largo);
}

module ensamble() {
    c_az = 124;
    eje_z = plato_top + perfil_largo + cab_eje_z;
    color("#7f8c8d") base_fija();
    color("#95a5a6") soporte_motor_azimut();
    translate([c_az, 0, -saz_placa_h]) motor_nema();
    color("#c0392b") translate([c_az, 0, 0.5]) linear_extrude(polea20_largo) perfil_gt2(20);
    color("#bdc3c7", 0.6) translate([-lazy_lado / 2, -lazy_lado / 2, 0]) cube([lazy_lado, lazy_lado, lazy_alto]);
    color("#2e86c1") plato_giratorio();
    // caja de control en el lado −X (u → −X): espejo de las coordenadas locales
    translate([-caja_r0, 0, caja_z0]) mirror([1, 0, 0]) {
        caja_vista();
        color("#aab7b8", 0.3) translate([0, 0, caja_alto + 30]) tapa_caja();   // tapa levantada para ver el interior
    }
    color("#1b4f72") translate([0, brazo_y, plato_top]) zocalo_brazo();
    color("#d0d3d4") translate([-perfil_x / 2, brazo_y - perfil_y / 2, plato_top]) cube([perfil_x, perfil_y, perfil_largo]);
    translate([0, brazo_y, plato_top + perfil_largo]) {
        color("#2e86c1") cabezal_altitud();
        color("silver") translate([0, -110, cab_eje_z]) rotate([-90, 0, 0]) cylinder(d = eje_d, h = 190);
        color("#c0392b") translate([0, cab_y / 2 + 0.5 + polea_alto, cab_eje_z]) rotate([90, 0, 0]) polea_altitud();
        color("#2e86c1") translate([0, -cab_y / 2 - 0.5 - vx_alto, cab_eje_z]) rotate([-90, 0, 0]) montura_vixen();
        color("#f5b041") translate([0, -cab_y / 2 - 0.5 - vx_alto + vx_mordaza_h, cab_eje_z]) rotate([90, 0, 0]) barra_vixen();
        // telescopio genérico con dos anillas (aquí, un Maksutov de 90 mm)
        y_tubo = -cab_y / 2 - 0.5 - vx_alto + vx_mordaza_h - barra_alto - 12 - 52;
        color("#1f2d3a") translate([-140, y_tubo, cab_eje_z]) rotate([0, 90, 0]) cylinder(d = 104, h = 280);
        for (x = [-50, 50]) color("#7d8a96") translate([x - 8, y_tubo, cab_eje_z]) rotate([0, 90, 0]) difference() {
            cylinder(d = 104 + 16, h = 16);
            translate([0, 0, -1]) cylinder(d = 104, h = 18);
        }
        // motor de altitud (C ≈ 76 mm bajo el eje con la correa de 280 mm)
        translate([0, perfil_y / 2, cab_eje_z - 76]) {
            color("#95a5a6") soporte_motor_altitud();
            translate([0, salt_placa_y + salt_placa, 0]) rotate([-90, 0, 0]) rotate([180, 0, 0]) motor_nema();
        }
    }
}

// --------------------------------------------------------------- Selector
if (pieza == "ensamble") ensamble();
else if (pieza == "base_fija") rotate([180, 0, 0]) base_fija();
else if (pieza == "soporte_motor_azimut") translate([0, 0, saz_ancho / 2]) rotate([90, 0, 0]) soporte_motor_azimut();  // de costado
else if (pieza == "plato_giratorio") translate([0, 0, plato_top]) rotate([180, 0, 0]) plato_giratorio();       // boca abajo
else if (pieza == "zocalo_brazo") zocalo_brazo();
else if (pieza == "cabezal_altitud") translate([0, 0, cab_y / 2]) rotate([90, 0, 0]) cabezal_altitud();       // de costado
else if (pieza == "polea_altitud") polea_altitud();
else if (pieza == "soporte_motor_altitud") translate([0, 0, 40]) soporte_motor_altitud();                  // de pie
else if (pieza == "montura_vixen") montura_vixen();
else if (pieza == "barra_vixen") barra_vixen();
else if (pieza == "prueba_gt2") prueba_gt2();
else if (pieza == "caja_control") caja_control();
else if (pieza == "caja_vista") caja_vista();
else if (pieza == "tapa_caja") translate([0, 0, 3]) rotate([180, 0, 0]) tapa_caja();
else if (pieza == "panel_energia") panel_energia();
else if (pieza == "tapa_panel") tapa_panel();
