/*
  Low profile Keycap for MX stems inspired by the ZSA Voyager and Taihao THTs.
  Units: mm

  This has been tested with an FDM 3D-Printer (Bambulab A1 mini) with PLA Matte.
  Requires no supports if you print with a brim and place it on one of its fillets 
  (at an angle)
  0.12mm layer-height (incl. initial layer).

  Notes / modeling choices:
  - Outer body is a two-stage extrusion: straight walls up to `side_fillet_start_z`,
    then a gentle taper toward the top “inset” footprint.
  - The “touch surface” concavity is approximated by subtracting a cylinder-shaped dish,
    with ~`dish_depth` sag at the center.
  - MX cross hole is a 2D plus that gets filleted using offset(r) then offset(-r)
*/

$fn = 96;

// -------------------------
// Parameters (grouped)
// -------------------------
/* Keycap footprint */
cap_w            = 18;     // X (use different values for oblong)
cap_h            = 18;     // Y
cap_corner_r     = 1.2;    // outer corner radius

/* Vertical dimensions */
cap_thickness        = 4.0;   // total height of cap body (cap bottom to top exterior)
wall_thickness       = 1.2;   // keycap underside cavity walls
underside_pocket_z   = 1.9;   // cavity depth from bottom (inside hollow depth)
side_fillet_start_z  = 2.2;   // z where outer “inset/taper” begins

/* Top inset / touch surface shaping */
inset_lr         = 2.0;   // inset on left/right at the very top (X border)
inset_tb_top     = 1.0;   // inset on top/bottom at the very top (Y border) (your 2mm->1mm feel)
dish_depth       = 1.0;   // concavity depth at center (approx)
dish_span_scale  = 0.95;  // how wide the dish influences (0..1), smaller = more localized

/* Stem (outer post) */
stem_outer_d     = 5.5;   // outer cylinder diameter
stem_total_len   = 3.8;   // total stem length up to the internal “roof” it attaches to
stem_protrude    = 1.9;   // how much stem sticks out below the keycap bottom (also equals pocket depth)

/* MX cross hole - these values are not to spec, but rather to print nicely. */
mx_plus_size     = 4.1;   // overall height/width of plus (across opposite ends)
mx_leg_thick     = 1.25;  // thickness of each leg
mx_inner_fillet  = 0.3;   // fillet radius for inside corners

/* Homing indicator (optional) */
enable_homing    = false;  // set true for F/J
homing_len       = 5.0;   // bar length (X)
homing_w         = 0.7;   // bar width (Y)
homing_h         = 0.5;   // bar height (Z)
homing_offset_x  = -2;    // move bump toward you (negative X) like typical F/J
homing_offset_z  = 1.1;   // move bump into/away from the keycap

// -------------------------
// Helpers
// -------------------------
module rounded_rect_2d(w, h, r) {
  r2 = min(r, min(w,h)/2);
  offset(r=r2) square([w-2*r2, h-2*r2], center=true);
}

module mx_plus_2d(size, leg, fillet_r) {
  // Sharp plus first
  union() {
    union() {
      square([leg, size], center=true);
      square([size, leg], center=true);
    }

    // Add material only in the 4 re-entrant (inside) corners
    // (these are at ±leg/2, ±leg/2). This won’t touch the 8 outer corners.
    for (sx = [-1, 1], sy = [-1, 1]) {
      translate([sx*leg/2, sy*leg/2]) 
        rotate([0,0,45])
          square(fillet_r, center=true);
    }
  }
}


// capsule-ish bar for homing (2D), then extrude
module capsule_2d(len, w) {
  // hull of two circles to make a capsule
  hull() {
    translate([-(len/2 - w/2), 0]) circle(d=w);
    translate([ +(len/2 - w/2), 0]) circle(d=w);
  }
}

// -------------------------
// Main model
// -------------------------
module keycap_body() {
  // bottom footprint
  base_w = cap_w;
  base_h = cap_h;

  // top footprint (inset)
  top_w  = max(0.1, cap_w - 2*inset_lr);
  top_h  = max(0.1, cap_h - 2*inset_tb_top);

  // scale factors for the upper taper
  sx = top_w / base_w;
  sy = top_h / base_h;

  lower_h = min(side_fillet_start_z, cap_thickness);
  upper_h = max(0, cap_thickness - lower_h);

  union() {
    // lower straight section
    linear_extrude(height=lower_h)
      rounded_rect_2d(base_w, base_h, cap_corner_r);

    // upper tapered section
    if (upper_h > 0.0001)
      translate([0,0,lower_h])
        linear_extrude(height=upper_h, scale=[sx, sy])
          rounded_rect_2d(base_w, base_h, cap_corner_r);
  }
}

module underside_pocket() {
  // cavity is a rounded rectangle inset by wall thickness
  inner_w = cap_w - 2*wall_thickness;
  inner_h = cap_h - 2*wall_thickness;
  inner_r = max(0, cap_corner_r - wall_thickness);

  // pocket cut from the bottom upward
  translate([0,0,0])
    linear_extrude(height=underside_pocket_z + 0.02)  // tiny extra to avoid z-fighting
      rounded_rect_2d(inner_w, inner_h, inner_r);
}

// concave dish made with a cylinder (axis along X)
module concave_dish_cut() {
  // cylinder gives curvature in Y, leaving X mostly "flat" — matches your 2mm LR / curved TB feel.
  top_h = max(0.1, cap_h - 2*inset_tb_top);

  a = dish_span_scale * top_h / 2; // half-chord in Y
  h = dish_depth;                  // sagitta (depth)

  // R = (a^2 + h^2)/(2h)
  R = (a*a + h*h) / (2*h);

  // place cylinder so that it cuts depth ~h at center on the top surface.
  // for a cylinder, the surface at y=0 sits at z = zc - R, so set that to cap_thickness - h.
  zc = (cap_thickness - h) + R;

  intersection() {
    translate([0,0,zc])
      rotate([0,90,0])  // axis along X
        cylinder(r=R, h=cap_w*3, center=true);

    // bounding box around the top region
    translate([0,0,cap_thickness - 3*h])
      cube([cap_w*2, cap_h*2, 6*h], center=true);
  }
}


// stem placement and extrude it to connect to keycap hull
module stem_post_with_mx_hole() {
  // force stem top to meet the "roof" (top of the underside pocket) at z = underside_pocket_z
  z1 = underside_pocket_z;
  z0 = z1 - stem_total_len;

  difference() {
    translate([0,0,z0])
      cylinder(d=stem_outer_d, h=stem_total_len);

    translate([0,0,z0 - 0.2])
      linear_extrude(height=stem_total_len + 0.4)
        mx_plus_2d(mx_plus_size, mx_leg_thick, mx_inner_fillet);
  }
}


module homing_bump() {
  if (enable_homing) {
    // put it on the top surface, slightly sunk into the dish cut region.
    translate([homing_offset_x, 0, cap_thickness - homing_offset_z])
      rotate([0, 0, 90])
      linear_extrude(height=homing_h)
        capsule_2d(homing_len, homing_w);
  }
}

module low_profile_xm_keycap() {
    union() {
      difference() {
        // main cap shell (solid, then we hollow it)
        keycap_body();
        
        // underside hollow pocket
        underside_pocket();

        // concave touch dish (top shaping)
        concave_dish_cut();
      }
      // stem post attached to the inside roof (top of pocket)
      stem_post_with_mx_hole();

      // optional homing bump 
      homing_bump();
    }
  
}

// -------------------------
// Render
// -------------------------
low_profile_xm_keycap();
