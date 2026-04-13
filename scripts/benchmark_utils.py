"""
benchmark_utils.py
Shared infrastructure utilities for benchmark scripts.

Provides:
  - Model unloading between runs (frees RAM/VRAM)
  - Memory checks before loading models
  - Warm-up inference (discarded, not counted)
  - Memory state logging
"""

import os
import subprocess
import platform
import time


def get_memory_state():
    """Get current memory usage in MB. Returns (rss_mb, available_mb, swap_used_mb)."""
    system = platform.system()
    try:
        if system == "Darwin":
            import resource
            rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)

            # Get available memory via vm_stat
            vm = subprocess.check_output(["vm_stat"], text=True)
            page_size = 16384  # Apple Silicon default
            free_pages = 0
            for line in vm.split("\n"):
                if "Pages free" in line:
                    free_pages += int(line.split(":")[1].strip().rstrip("."))
                if "Pages inactive" in line:
                    free_pages += int(line.split(":")[1].strip().rstrip("."))
            available_mb = round(free_pages * page_size / (1024 * 1024))

            # Swap
            swap_info = subprocess.check_output(
                ["sysctl", "-n", "vm.swapusage"], text=True
            ).strip()
            swap_used_mb = 0
            for part in swap_info.split(","):
                if "used" in part.lower():
                    val = part.split("=")[1].strip()
                    if "M" in val:
                        swap_used_mb = float(val.replace("M", "").strip())
                    elif "G" in val:
                        swap_used_mb = float(val.replace("G", "").strip()) * 1024

            return round(rss_mb, 1), available_mb, round(swap_used_mb, 1)
        elif system == "Linux":
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            mem = {}
            for line in lines:
                parts = line.split()
                mem[parts[0].rstrip(":")] = int(parts[1])
            available_mb = mem.get("MemAvailable", 0) // 1024
            swap_used_mb = (mem.get("SwapTotal", 0) - mem.get("SwapFree", 0)) // 1024
            import resource
            rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            return round(rss_mb, 1), available_mb, round(swap_used_mb, 1)
    except Exception:
        pass
    return 0, 0, 0


def log_memory_state(label=""):
    """Print current memory state with optional label."""
    rss, available, swap = get_memory_state()
    print(f"     [MEM] {label} RSS={rss}MB  Available={available}MB  Swap={swap}MB")
    return {"rss_mb": rss, "available_mb": available, "swap_used_mb": swap}


def check_memory(min_available_mb=2048):
    """Check if sufficient memory is available. Returns True if OK."""
    _, available, swap = get_memory_state()
    if available < min_available_mb:
        print(f"     [WARNING] Low memory: {available}MB available (need {min_available_mb}MB)")
        print(f"     [WARNING] Swap usage: {swap}MB — latency may be affected")
        return False
    return True


def unload_ollama_model(model_id):
    """Unload a model from Ollama to free memory."""
    try:
        subprocess.run(
            ["ollama", "stop", model_id],
            capture_output=True, text=True, timeout=30
        )
        time.sleep(2)  # Give OS time to reclaim memory
    except Exception:
        pass  # Ollama may not be running or model not loaded


def warm_up_inference(client, model_id, system_prompt, timeout_config):
    """Run one warm-up inference to prime the model. Result is discarded."""
    try:
        client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Test message — warm-up only."},
            ],
            temperature=0.0,
            max_tokens=16,
        )
    except Exception:
        pass  # Warm-up failure is non-fatal
