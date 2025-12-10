from solid import *
from solid.utils import *

# ==========================================
# 1. CONFIGURATION
# ==========================================
CONFIG = {
    # General Tubing Dimensions
    'tubing_radius': 36.5,  # OD ~73mm
    'bore_radius': 31.0,  # ID ~62mm

    # Housing Dimensions
    'body_radius': 68.0,
    'inner_sleeve_radius': 64.0,
    'inner_core_radius': 62.0,

    # Slot Cutter Dimensions
    'slot_cutter_radius': 8.0,
    'slot_cutter_length': 180.0,  # Length of the cutting cylinder

    # Colors
    'c_metal': "DimGray",
    'c_body': "FireBrick",
    'c_rubber': "darkslategray",
    'c_sleeve': "lightgray",
    'c_core': "Black"
}


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def create_slot_hull(z_center, span_offset):
    """
    Creates the 'hull' shape for the slot cutouts.
    z_center: Vertical center of the slot relative to component origin
    span_offset: +/- distance from z_center for the rounded ends
    """
    # Create the two cylinders that define the top and bottom of the slot
    top_cyl = translate([0, 0, span_offset])(
        rotate(a=90, v=[1, 0, 0])(
            cylinder(center=True, h=CONFIG['slot_cutter_length'], r=CONFIG['slot_cutter_radius'])
        )
    )

    bottom_cyl = translate([0, 0, -span_offset])(
        rotate(a=90, v=[1, 0, 0])(
            cylinder(center=True, h=CONFIG['slot_cutter_length'], r=CONFIG['slot_cutter_radius'])
        )
    )

    # Hull them together and move to specific Z height
    return translate([0, 0, z_center])(
        hull()(top_cyl, bottom_cyl)
    )


def create_tubing(length):
    return color(CONFIG['c_metal'])(
        cylinder(h=length, r=CONFIG['tubing_radius'])
    )


# ==========================================
# 3. COMPONENTS
# ==========================================

def create_lower_slip_housing():
    """
    Section 2: The bottom red housing.
    Features: 120mm height, Bull nose taper, 2 Slots (0, 180).
    """
    # 1. Red Outer Body (Main + Bull Nose Taper)
    main_cyl = cylinder(h=120, r=CONFIG['body_radius'])

    taper = translate([0, 0, -70])(
        cylinder(h=70, r1=40.0, r2=CONFIG['body_radius'])
    )
    lip = translate([0, 0, -80])(
        cylinder(h=10, r=40.0)
    )

    outer_body = color(CONFIG['c_body'])(
        union()(main_cyl, taper, lip)
    )

    # 2. Cutouts (0 and 180 degrees only)
    # Slot Params: Center=60, Span=+/-35
    slot_shape = create_slot_hull(z_center=60, span_offset=35)

    cutouts = union()(
        rotate(a=0, v=[0, 0, 1])(slot_shape),
        rotate(a=180, v=[0, 0, 1])(slot_shape)
    )

    # 3. Inner Cores (Visible through slots)
    inner_sleeve = color(CONFIG['c_sleeve'])(
        cylinder(h=120, r=CONFIG['inner_sleeve_radius'])
    )
    inner_core = color(CONFIG['c_core'])(
        cylinder(h=120, r=CONFIG['inner_core_radius'])
    )

    # Assemble
    return union()(
        difference()(outer_body, cutouts),
        inner_sleeve,
        inner_core
    )


def create_sealing_stack():
    """
    Section 3: The 5-part sealing element with gauge rings.
    """
    # 1. Internal Stack (Rubber elements and spacers)
    stack_parts = union()(
        cylinder(h=25, r=80.0),  # Element 1
        translate([0, 0, 25])(cylinder(h=12, r=72.0)),  # Spacer 1
        translate([0, 0, 37])(cylinder(h=25, r=80.0)),  # Element 2
        translate([0, 0, 62])(cylinder(h=12, r=72.0)),  # Spacer 2
        translate([0, 0, 74])(cylinder(h=25, r=80.0))  # Element 3
    )
    internal_stack = color(CONFIG['c_rubber'])(stack_parts)

    # 2. Gauge Rings (Metal)
    bottom_ring = color(CONFIG['c_metal'])(
        cylinder(h=20, r1=68.0, r2=76.0)
    )
    top_ring = color(CONFIG['c_metal'])(
        translate([0, 0, 119])(
            cylinder(h=20, r1=76.0, r2=68.0)
        )
    )

    # Assemble: Bottom Ring + (Stack shifted up 20) + Top Ring
    return union()(
        bottom_ring,
        translate([0, 0, 20])(internal_stack),
        top_ring
    )


def create_upper_bypass_housing():
    """
    Section 4: The top red housing.
    Features: Stepped shoulder, 4 Slots (0, 90, 180, 270).
    """
    # 1. Red Outer Body Geometry
    # Constructed as a stack of cylinders
    geo_parts = union()(
        cylinder(h=10, r=64.0),  # Bottom Lip
        translate([0, 0, 10])(cylinder(h=25, r=68.0)),  # Shoulder
        translate([0, 0, 35])(cylinder(h=250, r=68.0)),  # Main Body
        translate([0, 0, 285])(cylinder(h=25, r1=68.0, r2=50.5)),  # Taper
        translate([0, 0, 310])(cylinder(h=40, r=50.5))  # Neck
    )

    # 2. Cutouts (4 angles)
    # Slot Params: Center=160, Span=+/-60
    slot_shape = create_slot_hull(z_center=160, span_offset=60)

    cutouts = union()(
        rotate(a=0, v=[0, 0, 1])(slot_shape),
        rotate(a=90, v=[0, 0, 1])(slot_shape),
        rotate(a=180, v=[0, 0, 1])(slot_shape),
        rotate(a=270, v=[0, 0, 1])(slot_shape)
    )

    # 3. Inner Cores (Shifted up 35 to match main body start)
    inner_sleeve = color(CONFIG['c_sleeve'])(
        translate([0, 0, 35])(cylinder(h=250, r=CONFIG['inner_sleeve_radius']))
    )
    inner_core = color(CONFIG['c_core'])(
        translate([0, 0, 35])(cylinder(h=250, r=CONFIG['inner_core_radius']))
    )

    # Assemble
    return union()(
        color(CONFIG['c_body'])(difference()(geo_parts, cutouts)),
        inner_sleeve,
        inner_core
    )


# ==========================================
# 4. ASSEMBLY
# ==========================================
def assemble_tool():
    parts = []

    # --- Step 1: Bottom Tail Pipe ---
    # Position: Base (Z=0)
    parts.append(
        create_tubing(length=150)
    )

    # --- Step 2: Lower Slip Housing ---
    # Position: Z=170 (Fixed offset from original design)
    parts.append(
        translate([0, 0, 170])(
            create_lower_slip_housing()
        )
    )

    # --- Step 3: Sealing Element Stack ---
    # Position: Z=290
    parts.append(
        translate([0, 0, 290])(
            create_sealing_stack()
        )
    )

    # --- Step 4: Upper Bypass Housing ---
    # Position: Z=429
    parts.append(
        translate([0, 0, 429])(
            create_upper_bypass_housing()
        )
    )

    # --- Step 5: Top Tubing ---
    # Position: Z=779
    parts.append(
        translate([0, 0, 779])(
            create_tubing(length=150)
        )
    )

    # --- Final: Bore Cut ---
    full_assembly = union()(parts)

    # Cut the bore through the entire Z-axis
    final_part = difference()(
        full_assembly,
        cylinder(center=True, h=4000, r=CONFIG['bore_radius'])
    )

    return final_part


# ==========================================
# 5. RENDER
# ==========================================
if __name__ == "__main__":
    out_file = "realistic_single_packer1.scad"
    print(f"Generating Modular Packer model to {out_file}...")

    design = assemble_tool()
    scad_render_to_file(design, out_file)


    print("Done! Open the .scad file to view.")
