import os

def print_general_info(ctx):
    print(f"Render engine '{ctx.scene.render.engine}'")
    print(f"Render resolution: {ctx.scene.render.resolution_x} x {ctx.scene.render.resolution_y}")
    print(f"Render resolution %: {ctx.scene.render.resolution_percentage}")

    if ctx.scene.render.engine == "CYCLES":
        cycles = ctx.preferences.addons["cycles"]
        print(f"Cycles samples: {ctx.scene.cycles.samples}")
        # report rendering devices -- a nice snippet for debugging and ensuring the accelerators are being used
        for dev in cycles.preferences.devices:
            print(f"ID:{dev['id']} Name:{dev['name']} Type:{dev['type']} Use:{dev['use']}")

def print_sys_info():
    os.system("nvidia-smi")
    os.system("nvcc --version")
    os.system("cat /proc/cpuinfo")
    os.system("lscpu")
    print("printing driver capabilities...")
    os.system("echo $NVIDIA_DRIVER_CAPABILITIES")
    os.system("echo $NVIDIA_VISIBLE_DEVICES")
    # os.system("cat /etc/X11/xorg.conf")
    os.system("ls /dev | grep nvidia")
    print("Printed.")
