#!/usr/bin/env python3
import sys
import os

BLENDER_MODULE_PATH = "/opt/blender"
if BLENDER_MODULE_PATH not in sys.path:
    sys.path.append(BLENDER_MODULE_PATH)

import bpy

def main():
    """
    python blender_eevee_debug_simplified.py -- <blend_file>
    """
    try:
        sep_index = sys.argv.index("--")
    except ValueError:
        print("Error: You must pass a .blend file after '--'.")
        sys.exit(1)

    if len(sys.argv) <= sep_index + 1:
        print("Error: Missing .blend file argument.")
        sys.exit(1)

    blend_file = sys.argv[sep_index + 1]
    print(f"Blend file: {blend_file}")

    # Open the .blend
    bpy.ops.wm.open_mainfile(filepath=blend_file)

    # Force EEVEE Next
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"

    # One frame
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end   = 1

    # Output to /tmp/debug_frame
    bpy.context.scene.render.filepath = "/tmp/debug_frame"

    print("Starting single-frame render with BLENDER_EEVEE_NEXT...")
    bpy.ops.render.render(animation=True)
    print("Render complete.")

if __name__ == "__main__":
    main()