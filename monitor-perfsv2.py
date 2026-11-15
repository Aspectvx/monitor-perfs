
import tkinter as tk
import psutil
import platform
import subprocess
import re

# =================================
# PC MONITOR - BY ASPECT
# VERSION 2.0
# =================================

BG = "#101014"
PANEL = "#1b1b23"
GREEN = "#35e69a"
WHITE = "#ffffff"
GREY = "#92929f"
BLUE = "#479cff"
ORANGE = "#ffad42"

root = tk.Tk()
root.title("PC PERFORMANCE MONITOR")
root.geometry("760x690")
root.configure(bg=BG)
root.resizable(False, False)

# Hardware detection
cpu_name = platform.processor() or "Unknown CPU"

def get_gpu_name():
    try:
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name",
             "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        return result.strip().splitlines()[0]
    except Exception:
        return "Unknown GPU"

gpu_name = get_gpu_name()

ram = psutil.virtual_memory()
total_ram = ram.total / (1024 ** 3)

# Header
tk.Label(
    root,
    text="PC PERFORMANCE MONITOR",
    font=("Segoe UI", 25, "bold"),
    fg=GREEN,
    bg=BG
).pack(pady=(20, 0))

tk.Label(
    root,
    text="SYSTEM PERFORMANCE MONITOR",
    font=("Segoe UI", 9),
    fg=GREY,
    bg=BG
).pack(pady=(0, 20))

# Hardware panel
hardware = tk.Frame(root, bg=PANEL, padx=20, pady=14)
hardware.pack(fill="x", padx=25)

tk.Label(
    hardware,
    text="HARDWARE",
    font=("Segoe UI", 11, "bold"),
    fg=BLUE,
    bg=PANEL
).pack(anchor="w")

for info in [
    f"CPU: {cpu_name}",
    f"GPU: {gpu_name}",
    f"TOTAL RAM: {total_ram:.1f} GB"
]:
    tk.Label(
        hardware,
        text=info,
        font=("Segoe UI", 10),
        fg=WHITE,
        bg=PANEL
    ).pack(anchor="w", pady=(8, 0))

# Performance panel
performance = tk.Frame(root, bg=PANEL, padx=20, pady=16)
performance.pack(fill="x", padx=25, pady=20)

tk.Label(
    performance,
    text="LIVE PERFORMANCE",
    font=("Segoe UI", 11, "bold"),
    fg=BLUE,
    bg=PANEL
).pack(anchor="w", pady=(0, 12))


def create_stat(title, color):
    frame = tk.Frame(performance, bg=PANEL)
    frame.pack(fill="x", pady=7)

    top = tk.Frame(frame, bg=PANEL)
    top.pack(fill="x")

    tk.Label(
        top,
        text=title,
        font=("Segoe UI", 10, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(side="left")

    value = tk.Label(
        top,
        text="0%",
        font=("Segoe UI", 11, "bold"),
        fg=color,
        bg=PANEL
    )
    value.pack(side="right")

    bar_bg = tk.Frame(
        frame,
        bg="#30303a",
        height=12
    )
    bar_bg.pack(fill="x", pady=(6, 0))

    bar = tk.Frame(
        bar_bg,
        bg=color,
        height=12
    )
    bar.place(x=0, y=0, relheight=1, relwidth=0)

    return value, bar


def update_bar(bar, value):
    value = max(0, min(100, value))
    bar.place_configure(relwidth=value / 100)


cpu_value, cpu_bar = create_stat("CPU USAGE", GREEN)
ram_value, ram_bar = create_stat("RAM USAGE", BLUE)
gpu_value, gpu_bar = create_stat("GPU USAGE", ORANGE)
vram_value, vram_bar = create_stat("GPU MEMORY", "#bb8cff")

# GPU temperature
temperature_frame = tk.Frame(performance, bg=PANEL)
temperature_frame.pack(fill="x", pady=(12, 0))

tk.Label(
    temperature_frame,
    text="GPU TEMPERATURE",
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(side="left")

temperature_value = tk.Label(
    temperature_frame,
    text="-- °C",
    font=("Segoe UI", 11, "bold"),
    fg=ORANGE,
    bg=PANEL
)
temperature_value.pack(side="right")


# NVIDIA data
def get_gpu_stats():
    try:
        result = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits"
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2
        )

        values = result.strip().split(",")

        gpu_usage = float(values[0].strip())
        gpu_temp = float(values[1].strip())
        vram_used = float(values[2].strip())
        vram_total = float(values[3].strip())

        return gpu_usage, gpu_temp, vram_used, vram_total

    except Exception:
        return None


# Live updates
def update_stats():
    # CPU
    cpu = psutil.cpu_percent(interval=None)
    cpu_value.config(text=f"{cpu:.1f}%")
    update_bar(cpu_bar, cpu)

    # RAM
    memory = psutil.virtual_memory()
    ram_usage = memory.percent

    ram_value.config(text=f"{ram_usage:.1f}%")
    update_bar(ram_bar, ram_usage)

    # NVIDIA GPU
    gpu_data = get_gpu_stats()

    if gpu_data is not None:
        gpu_usage, gpu_temp, vram_used, vram_total = gpu_data

        gpu_value.config(text=f"{gpu_usage:.1f}%")
        update_bar(gpu_bar, gpu_usage)

        temperature_value.config(text=f"{gpu_temp:.0f} °C")

        if vram_total > 0:
            vram_percent = (vram_used / vram_total) * 100

            vram_value.config(
                text=f"{vram_used:.0f} / {vram_total:.0f} MiB"
            )
            update_bar(vram_bar, vram_percent)

    else:
        gpu_value.config(text="N/A")
        temperature_value.config(text="N/A")
        vram_value.config(text="N/A")

    root.after(1000, update_stats)


# Footer
tk.Label(
    root,
    text="VERSION 2.0", 
    font=("Segoe UI", 8),
    fg=GREY,
    bg=BG
).pack(side="bottom", pady=15)

# Start
psutil.cpu_percent(interval=None)
root.after(1000, update_stats)

root.mainloop()
