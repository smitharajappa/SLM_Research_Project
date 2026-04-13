"""
capture_hardware.py
Captures system hardware specifications at benchmark start.

Outputs: data/hardware_spec.json
Run this before starting any benchmark to record the test environment.
"""

import os
import json
import platform
import subprocess
from datetime import datetime


def get_cpu_info():
    """Get CPU model and core count."""
    system = platform.system()
    if system == "Darwin":
        try:
            chip = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            chip = platform.processor() or "Unknown"
        try:
            cores = subprocess.check_output(
                ["sysctl", "-n", "hw.ncpu"], text=True
            ).strip()
        except Exception:
            cores = str(os.cpu_count())
        return chip, int(cores)
    elif system == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        chip = line.split(":")[1].strip()
                        break
                else:
                    chip = "Unknown"
        except Exception:
            chip = "Unknown"
        return chip, os.cpu_count() or 0
    return platform.processor() or "Unknown", os.cpu_count() or 0


def get_memory_gb():
    """Get total system memory in GB."""
    system = platform.system()
    try:
        if system == "Darwin":
            mem_bytes = int(subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"], text=True
            ).strip())
            return round(mem_bytes / (1024 ** 3), 1)
        elif system == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        return round(kb / (1024 ** 2), 1)
    except Exception:
        pass
    return 0


def get_gpu_info():
    """Get GPU info if available."""
    system = platform.system()
    if system == "Darwin":
        try:
            sp = subprocess.check_output(
                ["system_profiler", "SPDisplaysDataType"],
                text=True, timeout=10
            )
            for line in sp.split("\n"):
                if "Chipset Model" in line or "Chip" in line:
                    return line.split(":")[1].strip()
        except Exception:
            pass
        # For Apple Silicon, GPU is integrated
        try:
            chip = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            if "Apple" in chip:
                return f"{chip} (integrated GPU)"
        except Exception:
            pass
    return "None detected"


def get_swap_gb():
    """Get current swap usage in GB."""
    try:
        if platform.system() == "Darwin":
            vm = subprocess.check_output(
                ["sysctl", "-n", "vm.swapusage"], text=True
            ).strip()
            # Parse: total = X  used = Y  free = Z
            for part in vm.split():
                if part.endswith("M"):
                    pass  # skip for now
            # Simpler: just report the full string
            return vm
        elif platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if "SwapTotal" in line:
                        kb = int(line.split()[1])
                        return f"{round(kb / (1024**2), 1)} GB total"
    except Exception:
        pass
    return "Unknown"


def get_ollama_version():
    """Get Ollama version if installed."""
    try:
        version = subprocess.check_output(
            ["ollama", "--version"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        return version
    except Exception:
        return "Not installed"


def get_python_version():
    """Get Python version."""
    return platform.python_version()


def capture():
    """Capture full hardware specification."""
    cpu_model, cpu_cores = get_cpu_info()

    spec = {
        "captured_at": datetime.now().isoformat(),
        "system": {
            "os": platform.system(),
            "os_version": platform.mac_ver()[0] if platform.system() == "Darwin" else platform.release(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
        },
        "cpu": {
            "model": cpu_model,
            "cores": cpu_cores,
        },
        "memory": {
            "total_gb": get_memory_gb(),
            "swap_info": get_swap_gb(),
        },
        "gpu": {
            "model": get_gpu_info(),
        },
        "software": {
            "python_version": get_python_version(),
            "ollama_version": get_ollama_version(),
        },
        "notes": "All SLM benchmarks run locally via Ollama. LLM baseline via Groq API.",
    }
    return spec


if __name__ == "__main__":
    print()
    print("=" * 50)
    print("  Hardware Specification Capture")
    print("=" * 50)

    spec = capture()

    output_path = "data/hardware_spec.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"\n  System:  {spec['system']['os']} {spec['system']['os_version']} ({spec['system']['architecture']})")
    print(f"  CPU:     {spec['cpu']['model']} ({spec['cpu']['cores']} cores)")
    print(f"  Memory:  {spec['memory']['total_gb']} GB")
    print(f"  GPU:     {spec['gpu']['model']}")
    print(f"  Python:  {spec['software']['python_version']}")
    print(f"  Ollama:  {spec['software']['ollama_version']}")
    print(f"\n  Saved: {output_path}")
    print("=" * 50)
    print()
